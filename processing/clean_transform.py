import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import pandas as pd

from config import ROLLING_WINDOWS
from datalake_utils import read_df, write_df


def clean_raw(df: pd.DataFrame) -> pd.DataFrame:
    """BF3 - nettoyage : doublons, valeurs manquantes, anomalies."""
    if df.empty:
        return df

    df = df.drop_duplicates(subset=["date", "ticker"])
    df = df.sort_values(["ticker", "date"])

    cols = ["open", "high", "low", "close", "volume"]
    df[cols] = df.groupby("ticker")[cols].transform(lambda s: s.interpolate().ffill().bfill())

    df = df[(df["close"] > 0) & (df["open"] > 0)]
    return df


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """BF5 - rendements, volatilité glissante, moyennes mobiles."""
    out = []
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("date").copy()
        g["return"] = g["close"].pct_change()

        for w in ROLLING_WINDOWS:
            g[f"volatility_{w}d"] = g["return"].rolling(window=w).std()
            g[f"ma_{w}d"] = g["close"].rolling(window=w).mean()

        out.append(g)

    result = pd.concat(out, ignore_index=True)
    result = result.dropna(subset=["return"])
    return result


def run_processing():
    print("=== Traitement : nettoyage + indicateurs financiers ===")
    raw = read_df("raw_historical")
    if raw.empty:
        print("[ERREUR] raw_historical vide. Lance batch_ingest.py d'abord.")
        return pd.DataFrame()

    cleaned = clean_raw(raw)
    enriched = compute_indicators(cleaned)

    # colonnes correspondant exactement au schéma de la table `processed`
    enriched["processed_ts"] = dt.datetime.now(dt.UTC).isoformat()
    final_cols = ["date", "ticker", "close", "return",
                  "volatility_5d", "volatility_10d", "volatility_20d",
                  "ma_5d", "ma_10d", "ma_20d", "processed_ts"]
    enriched = enriched[final_cols]

    write_df(enriched, "processed", if_exists="replace")
    print(f"[OK] {len(enriched)} lignes traitées -> table processed.")
    return enriched


if __name__ == "__main__":
    run_processing()