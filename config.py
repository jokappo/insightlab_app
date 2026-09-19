"""
Configuration centrale du projet InsightLab.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "volatility_model.joblib")
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)

# --- Connexion PostgreSQL (Data Lake) ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "insightlab_datalake")
POSTGRES_USER = os.getenv("POSTGRES_USER", "insightlab")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "insightlab")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "market-ticks"

# --- Actifs suivis (réels, via Yahoo Finance) ---
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "BTC-USD", "^GSPC"]

# --- Historique batch (BF1) ---
HISTORICAL_PERIOD = "2y"
HISTORICAL_INTERVAL = "1d"

# --- Streaming (BF2) ---
STREAM_INTERVAL_SECONDS = 60
STREAM_LOOKBACK = "1d"
STREAM_GRANULARITY = "1m"

# --- Feature engineering (BF5/BF6) ---
ROLLING_WINDOWS = [5, 10, 20]

# --- Cible ML (BF7) ---
TARGET_HORIZON_DAYS = 5

# --- Alertes (BF10) ---
ALERT_ZSCORE_THRESHOLD = 2.0