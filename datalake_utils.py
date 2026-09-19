"""
Utilitaires d'accès au Data Lake (PostgreSQL).
"""
import pandas as pd
from sqlalchemy import create_engine
from config import DATABASE_URL

_engine = create_engine(DATABASE_URL)


def get_engine():
    return _engine


def write_df(df: pd.DataFrame, table: str, if_exists: str = "append", deduplicate_on=None):
    if df is None or df.empty:
        return

    if deduplicate_on:
        cols = list(deduplicate_on)
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"Colonnes absentes pour la déduplication {missing} dans {table}")

        df = df.copy()
        for col in cols:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d") if col == "date" else df[col].astype(str)

        try:
            existing = pd.read_sql(f"SELECT {', '.join(cols)} FROM {table}", _engine).copy()
        except Exception:
            existing = pd.DataFrame(columns=cols)

        if not existing.empty:
            for col in cols:
                existing[col] = pd.to_datetime(existing[col], errors="coerce").dt.strftime("%Y-%m-%d") if col == "date" else existing[col].astype(str)
            existing_key = existing[cols].drop_duplicates()
            df = df.merge(existing_key, on=cols, how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

        if df.empty:
            print(f"[OK] aucune ligne à insérer dans {table} (déjà présente)")
            return

    df.to_sql(table, _engine, if_exists=if_exists, index=False, method="multi")


def read_df(table: str, where: str = "") -> pd.DataFrame:
    query = f"SELECT * FROM {table} {where}"
    try:
        df = pd.read_sql(query, _engine)
        # Convert to object first so None survives JSON serialization in numeric columns.
        return df.astype(object).where(pd.notna(df), None)
    except Exception as e:
        print(f"[WARN] lecture {table} impossible : {e}")
        return pd.DataFrame()