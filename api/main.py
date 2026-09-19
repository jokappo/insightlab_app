"""
API FastAPI - expose les données du Data Lake pour le dashboard React.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from datalake_utils import get_engine, read_df
from config import TICKERS

app = FastAPI(title="InsightLab API")

# autorise le front React (autre port) à appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "insightlab-api"}


@app.get("/ready")
def readiness():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error
    return {"status": "ready", "database": "ok"}


@app.get("/tickers")
def get_tickers():
    return {"tickers": TICKERS}


def validate_ticker(ticker: str) -> str:
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"Ticker inconnu: {ticker}")
    return ticker


@app.get("/processed/{ticker}")
def get_processed(ticker: str, limit: int = Query(500, ge=1, le=2000)):
    ticker = validate_ticker(ticker)
    df = read_df("processed", where=f"WHERE ticker = '{ticker}' ORDER BY date DESC LIMIT {limit}")
    df = df.sort_values("date") if not df.empty else df
    return df.to_dict(orient="records")




@app.get("/alerts/{ticker}")
def get_alerts(ticker: str, limit: int = Query(100, ge=1, le=500)):
    ticker = validate_ticker(ticker)
    df = read_df("alerts", where=f"WHERE ticker = '{ticker}' ORDER BY alert_ts DESC LIMIT {limit}")
    return df.to_dict(orient="records")


@app.get("/predictions/latest")
def get_latest_predictions():
    df = read_df("predictions", where="ORDER BY prediction_ts DESC")
    if df.empty:
        return []
    latest = df.groupby("ticker").first().reset_index()
    return latest.to_dict(orient="records")

@app.get("/predictions/{ticker}")
def get_predictions(ticker: str, limit: int = Query(500, ge=1, le=2000)):
    ticker = validate_ticker(ticker)
    df = read_df("predictions", where=f"WHERE ticker = '{ticker}' ORDER BY prediction_ts DESC LIMIT {limit}")
    df = df.sort_values("prediction_ts") if not df.empty else df
    return df.to_dict(orient="records")