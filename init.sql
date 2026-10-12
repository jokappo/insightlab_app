-- Table des données historiques brutes (BF1)
CREATE TABLE IF NOT EXISTS raw_historical (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    ingestion_ts TIMESTAMP NOT NULL,
    UNIQUE (date, ticker)
);

-- Table des cotations streaming brutes (BF2)
CREATE TABLE IF NOT EXISTS raw_streaming (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    source VARCHAR(20) NOT NULL DEFAULT 'live',
    ingestion_ts TIMESTAMP NOT NULL
);

-- Table des données nettoyées + indicateurs (BF3, BF5)
CREATE TABLE IF NOT EXISTS processed (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    close DOUBLE PRECISION,
    return DOUBLE PRECISION,
    volatility_5d DOUBLE PRECISION,
    volatility_10d DOUBLE PRECISION,
    volatility_20d DOUBLE PRECISION,
    ma_5d DOUBLE PRECISION,
    ma_10d DOUBLE PRECISION,
    ma_20d DOUBLE PRECISION,
    processed_ts TIMESTAMP NOT NULL
);

-- Table du Feature Store (BF6)
CREATE TABLE IF NOT EXISTS features (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    return DOUBLE PRECISION,
    volatility_5d DOUBLE PRECISION,
    volatility_10d DOUBLE PRECISION,
    volatility_20d DOUBLE PRECISION,
    ma_5d DOUBLE PRECISION,
    ma_10d DOUBLE PRECISION,
    ma_20d DOUBLE PRECISION,
    target_future_volatility DOUBLE PRECISION,
    feature_version_ts TIMESTAMP NOT NULL
);

-- Table des prédictions (BF8)
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    predicted_volatility DOUBLE PRECISION NOT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'live',
    prediction_ts TIMESTAMP NOT NULL
);

-- Table des alertes (BF10)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    predicted_volatility DOUBLE PRECISION,
    zscore DOUBLE PRECISION,
    message TEXT,
    source VARCHAR(20) NOT NULL DEFAULT 'live',
    alert_ts TIMESTAMP NOT NULL
);