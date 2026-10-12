"""
API FastAPI - expose les données du Data Lake pour le dashboard React.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
import datetime as dt
import pandas as pd

from datalake_utils import get_engine, read_df, write_df
from ml.predict import run_predictions
from config import TICKERS

app = FastAPI(title="InsightLab API")

# autorise le front React (autre port) à appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    ticker: str
    shock_percent: float = Field(default=-8.0, ge=-50.0, le=50.0)


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


@app.post("/simulation/market-shock")
def simulate_market_shock(payload: SimulationRequest):
    ticker = validate_ticker(payload.ticker)
    latest = read_df("raw_historical", where=f"WHERE ticker = '{ticker}' ORDER BY date DESC LIMIT 1")
    if latest.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée historique pour {ticker}")

    source = latest.iloc[0]
    base_close = float(source["close"])
    simulated_close = base_close * (1 + payload.shock_percent / 100)
    if simulated_close <= 0:
        raise HTTPException(status_code=422, detail="Le choc produit un prix invalide")

    simulation_ts = dt.datetime.now(dt.UTC)
    with get_engine().begin() as connection:
        connection.execute(text(
            "ALTER TABLE raw_streaming ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'live'"
        ))

    simulated_tick = pd.DataFrame([{
        "timestamp": simulation_ts,
        "ticker": ticker,
        "open": simulated_close,
        "high": simulated_close,
        "low": simulated_close,
        "close": simulated_close,
        "volume": int(source["volume"] or 0),
        "source": "simulation",
        "ingestion_ts": simulation_ts,
    }])
    write_df(simulated_tick, "raw_streaming", if_exists="append")

    predictions = run_predictions(source="simulation", tickers=[ticker])
    if predictions.empty:
        raise HTTPException(status_code=503, detail="Le modèle n'a produit aucune prédiction")

    result = predictions[predictions["ticker"] == ticker]
    if result.empty:
        raise HTTPException(status_code=503, detail=f"Aucune prédiction produite pour {ticker}")

    prediction = result.iloc[-1].to_dict()
    alerts = read_df(
        "alerts",
        where=f"WHERE ticker = '{ticker}' AND source = 'simulation' AND alert_ts >= '{simulation_ts.isoformat()}' ORDER BY alert_ts DESC",
    )
    return {
        "simulation": {
            "ticker": ticker,
            "shock_percent": payload.shock_percent,
            "base_close": base_close,
            "simulated_close": simulated_close,
            "timestamp": simulation_ts,
        },
        "prediction": prediction,
        "alerts": alerts.to_dict(orient="records"),
    }


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