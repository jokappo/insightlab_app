"""
BF1 - Ingestion des données financières historiques (traitement BATCH).
Source : Yahoo Finance (données réelles) via yfinance.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import pandas as pd
import yfinance as yf

from config import TICKERS, HISTORICAL_PERIOD, HISTORICAL_INTERVAL
from datalake_utils import write_df


def fetch_historical(ticker: str) -> pd.DataFrame:
    df = yf.download(
        ticker,
        period=HISTORICAL_PERIOD,
        interval=HISTORICAL_INTERVAL,
        progress=False,
        auto_adjust=True,
    )
    if df is None or df.empty:
        print(f"[WARN] Aucune donnée reçue pour {ticker}")
        return pd.DataFrame()

    df = df.reset_index()
    df.columns = [c if isinstance(c, str) else c[0] for c in df.columns]
    df["ticker"] = ticker
    df["ingestion_ts"] = dt.datetime.now(dt.UTC).isoformat()
    df = df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    return df[
        ["date", "ticker", "open", "high", "low", "close", "volume", "ingestion_ts"]
    ]


def run_batch_ingestion():
    print(
        f"=== Ingestion BATCH historique ({HISTORICAL_PERIOD}, {HISTORICAL_INTERVAL}) ==="
    )
    all_data = []
    for ticker in TICKERS:
        print(f"  -> téléchargement {ticker} ...")
        df = fetch_historical(ticker)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        print("[ERREUR] Aucune donnée récupérée. Vérifie ta connexion internet.")
        return pd.DataFrame()

    full_df = pd.concat(all_data, ignore_index=True)
    full_df["date"] = pd.to_datetime(full_df["date"]).dt.strftime("%Y-%m-%d")
    write_df(full_df, "raw_historical", if_exists="append", deduplicate_on=["date", "ticker"])
    print(f"[OK] {len(full_df)} lignes ingérées dans raw_historical.")
    return full_df


if __name__ == "__main__":
    run_batch_ingestion()
