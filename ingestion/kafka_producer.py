"""
BF2 - Producer Kafka : interroge Yahoo Finance à intervalle régulier
et publie chaque cotation dans le topic Kafka (market-ticks).
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import datetime as dt
import yfinance as yf
from kafka import KafkaProducer

from config import TICKERS, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, STREAM_INTERVAL_SECONDS, STREAM_LOOKBACK, STREAM_GRANULARITY


def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def fetch_latest_tick(ticker: str):
    df = yf.download(ticker, period=STREAM_LOOKBACK, interval=STREAM_GRANULARITY,
                      progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None

    df = df.reset_index().tail(1)
    df.columns = [c if isinstance(c, str) else c[0] for c in df.columns]
    ts_col = "Datetime" if "Datetime" in df.columns else "Date"
    row = df.iloc[0]

    return {
        "timestamp": str(row[ts_col]),
        "ticker": ticker,
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": int(row["Volume"]),
        "ingestion_ts": dt.datetime.now(dt.UTC).isoformat(),
    }


def run_producer():
    producer = get_producer()
    print(f"=== Producer Kafka démarré (topic={KAFKA_TOPIC}, intervalle={STREAM_INTERVAL_SECONDS}s) ===")
    try:
        while True:
            for ticker in TICKERS:
                tick = fetch_latest_tick(ticker)
                if tick:
                    producer.send(KAFKA_TOPIC, value=tick)
                    print(f"  -> envoyé : {tick['ticker']} @ {tick['close']}")
            producer.flush()
            time.sleep(STREAM_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nArrêt du producer.")
    finally:
        producer.close()


if __name__ == "__main__":
    run_producer()