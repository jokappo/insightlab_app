"""
DAG Airflow : orchestre le pipeline batch InsightLab.
Ingestion historique -> nettoyage -> features -> entraînement -> prédiction.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

default_args = {
    "owner": "insightlab",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="insightlab_batch_pipeline",
    default_args=default_args,
    description="Pipeline batch : ingestion -> nettoyage -> features -> entraînement",
    schedule_interval="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["insightlab", "batch"],
) as dag:

    ingestion = BashOperator(
        task_id="ingestion_batch",
        bash_command=f"cd {PROJECT_DIR} && python ingestion/batch_ingest.py",
    )

    processing = BashOperator(
        task_id="nettoyage_indicateurs",
        bash_command=f"cd {PROJECT_DIR} && python processing/clean_transform.py",
    )

    features = BashOperator(
        task_id="feature_store",
        bash_command=f"cd {PROJECT_DIR} && python features/feature_store.py",
    )

    training = BashOperator(
        task_id="entrainement_ml",
        bash_command=f"cd {PROJECT_DIR} && python ml/train_model.py",
    )

    prediction = BashOperator(
        task_id="prediction_volatilite",
        bash_command=f"cd {PROJECT_DIR} && python ml/predict.py",
    )

    ingestion >> processing >> features >> training >> prediction