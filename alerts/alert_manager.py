
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import pandas as pd

from config import ALERT_ZSCORE_THRESHOLD
from datalake_utils import get_engine, read_df, write_df
from sqlalchemy import text


def check_and_raise_alerts(new_predictions: pd.DataFrame):
    if new_predictions.empty:
        return

    with get_engine().begin() as connection:
        connection.execute(text(
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'live'"
        ))
        connection.execute(text(
            "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'live'"
        ))

    history = read_df("predictions")
    history = history[history["source"].fillna("live") == "live"]
    alerts = []

    for _, row in new_predictions.iterrows():
        ticker = row["ticker"]
        pred = row["predicted_volatility"]

        past = history[history["ticker"] == ticker]["predicted_volatility"]
        if len(past) < 5:
            continue  # pas assez d'historique pour un seuil fiable

        mean_, std_ = past.mean(), past.std()
        if std_ == 0 or pd.isna(std_):
            continue

        zscore = (pred - mean_) / std_
        if zscore > ALERT_ZSCORE_THRESHOLD:
            alerts.append({
                "ticker": ticker,
                "predicted_volatility": pred,
                "zscore": float(zscore),
                "message": f"Volatilité anormalement élevée pour {ticker} (z-score={zscore:.2f})",
                "source": row.get("source", "live"),
                "alert_ts": dt.datetime.now(dt.UTC).isoformat(),
            })

    if alerts:
        df = pd.DataFrame(alerts)
        write_df(df, "alerts", if_exists="append")
        for a in alerts:
            print(f"[ALERTE] {a['message']}")
    else:
        print("[OK] Aucune alerte déclenchée sur cette itération.")


if __name__ == "__main__":
    # test manuel : relit les dernières prédictions et vérifie les alertes
    preds = read_df("predictions")
    if not preds.empty:
        last_batch = preds.sort_values("prediction_ts").tail(len(preds["ticker"].unique()))
        check_and_raise_alerts(last_batch)