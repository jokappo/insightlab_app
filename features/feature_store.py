
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import pandas as pd

from config import ROLLING_WINDOWS, TARGET_HORIZON_DAYS
from datalake_utils import read_df, write_df

FEATURE_COLUMNS = (
    ["return"]
    + [f"volatility_{w}d" for w in ROLLING_WINDOWS]
    + [f"ma_{w}d" for w in ROLLING_WINDOWS]
)


def build_features(processed: pd.DataFrame, for_training: bool = True) -> pd.DataFrame:
    frames = []
    for ticker, g in processed.groupby("ticker"):
        g = g.sort_values("date").copy()

        if for_training:
            # cible = volatilité réalisée sur les N prochains jours
            g["target_future_volatility"] = (
                g["return"].shift(-1).rolling(window=TARGET_HORIZON_DAYS).std().shift(-(TARGET_HORIZON_DAYS - 1))
            )

        frames.append(g)

    feat = pd.concat(frames, ignore_index=True)
    keep = ["date", "ticker"] + FEATURE_COLUMNS
    if for_training:
        keep.append("target_future_volatility")
        feat = feat.dropna(subset=FEATURE_COLUMNS + ["target_future_volatility"])
    else:
        feat = feat.dropna(subset=FEATURE_COLUMNS)

    feat = feat[keep].copy()
    feat["feature_version_ts"] = dt.datetime.now(dt.UTC).isoformat()
    return feat


def run_feature_store(for_training: bool = True):
    print("=== Construction du Feature Store ===")
    processed = read_df("processed")
    if processed.empty:
        print("[ERREUR] table processed vide. Lance clean_transform.py d'abord.")
        return pd.DataFrame()

    feat = build_features(processed, for_training=for_training)
    write_df(feat, "features", if_exists="replace")
    print(f"[OK] {len(feat)} lignes de features -> table features.")
    return feat


if __name__ == "__main__":
    run_feature_store(for_training=True)