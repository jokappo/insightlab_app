import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import joblib
import pandas as pd

from config import MODEL_PATH, ROLLING_WINDOWS, TICKERS
from datalake_utils import read_df, write_df
from alerts.alert_manager import check_and_raise_alerts


def build_live_features(ticker: str) -> pd.DataFrame:
    hist = read_df("raw_historical", where=f"WHERE ticker = '{ticker}' ORDER BY date")
    stream = read_df("raw_streaming", where=f"WHERE ticker = '{ticker}' ORDER BY timestamp")

    if hist.empty:
        return pd.DataFrame()

    closes = hist["close"].tolist()
    if not stream.empty:
        closes.append(float(stream["close"].iloc[-1]))  # dernière cotation live

    s = pd.Series(closes)
    returns = s.pct_change()

    row = {"return": returns.iloc[-1]}
    for w in ROLLING_WINDOWS:
        row[f"volatility_{w}d"] = returns.rolling(window=w).std().iloc[-1]
        row[f"ma_{w}d"] = s.rolling(window=w).mean().iloc[-1]

    return pd.DataFrame([row])


def run_predictions():
    if not os.path.exists(MODEL_PATH):
        print("[ERREUR] Modèle introuvable. Lance ml/train_model.py d'abord.")
        return pd.DataFrame()

    bundle = joblib.load(MODEL_PATH)
    model, feature_cols = bundle["model"], bundle["features"]

    results = []
    for ticker in TICKERS:
        feats = build_live_features(ticker)
        if feats.empty or feats[feature_cols].isnull().any(axis=1).iloc[0]:
            continue
        pred = model.predict(feats[feature_cols])[0]
        results.append({
            "ticker": ticker,
            "predicted_volatility": float(pred),
            "prediction_ts": dt.datetime.now(dt.UTC).isoformat(),
        })

    if not results:
        print("[WARN] Aucune prédiction générée.")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    # Evaluate alerts before persisting the new batch so it is not part of its own baseline.
    check_and_raise_alerts(df)
    write_df(df, "predictions", if_exists="append")
    print(f"[OK] {len(df)} prédictions générées -> table predictions.")
    for r in results:
        print(f"  {r['ticker']:10s} volatilité prédite : {r['predicted_volatility']:.6f}")
    return df


if __name__ == "__main__":
    run_predictions()