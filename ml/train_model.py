
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score

from config import MODEL_PATH
from datalake_utils import read_df
from features.feature_store import FEATURE_COLUMNS

CANDIDATES = {
    "Ridge (baseline linéaire)": Ridge(alpha=1.0),
    "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42),
}


def evaluate_candidate(model, X, y, n_splits=5):
    """Validation croisée temporelle -> MAE et R² moyens sur les splits."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    maes, r2s = [], []
    for train_idx, test_idx in tscv.split(X):
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        preds = model.predict(X.iloc[test_idx])
        maes.append(mean_absolute_error(y.iloc[test_idx], preds))
        r2s.append(r2_score(y.iloc[test_idx], preds))
    return np.mean(maes), np.mean(r2s)


def train():
    print("=== Entraînement et comparaison des modèles ===")
    feat = read_df("features")
    if feat.empty or "target_future_volatility" not in feat.columns:
        print("[ERREUR] table features vide ou sans cible. Lance feature_store.py d'abord.")
        return None

    feat = feat.sort_values("date").reset_index(drop=True)
    X_all = feat[FEATURE_COLUMNS]
    y_all = feat["target_future_volatility"]

    # --- Split chronologique 80% train+CV / 20% test final ---
    split_idx = int(len(feat) * 0.8)
    X_train, X_test = X_all.iloc[:split_idx], X_all.iloc[split_idx:]
    y_train, y_test = y_all.iloc[:split_idx], y_all.iloc[split_idx:]
    print(f"Train+CV : {len(X_train)} lignes | Test final : {len(X_test)} lignes\n")

    # --- Comparaison des candidats par validation croisée sur le train ---
    print("--- Comparaison des algorithmes (validation croisée temporelle) ---")
    results = {}
    for name, model in CANDIDATES.items():
        mae, r2 = evaluate_candidate(model, X_train, y_train)
        results[name] = {"mae": mae, "r2": r2}
        print(f"  {name:30s} | MAE moyen: {mae:.6f} | R² moyen: {r2:.3f}")

    best_name = min(results, key=lambda n: results[n]["mae"])
    print(f"\n>>> Meilleur modèle (MAE le plus bas) : {best_name}")

    # --- Évaluation finale sur le test set jamais vu ---
    best_model = CANDIDATES[best_name]
    best_model.fit(X_train, y_train)
    test_preds = best_model.predict(X_test)
    test_mae = mean_absolute_error(y_test, test_preds)
    test_r2 = r2_score(y_test, test_preds)
    print(f"--- Évaluation finale (test set, jamais vu) ---")
    print(f"  MAE test: {test_mae:.6f} | R² test: {test_r2:.3f}")

    # --- Réentraînement sur 100% des données pour la production ---
    final_model = CANDIDATES[best_name]
    final_model.fit(X_all, y_all)
    joblib.dump({
        "model": final_model,
        "features": FEATURE_COLUMNS,
        "model_name": best_name,
        "test_mae": test_mae,
        "test_r2": test_r2,
    }, MODEL_PATH)
    print(f"\n[OK] Modèle '{best_name}' sauvegardé -> {MODEL_PATH}")
    return final_model


if __name__ == "__main__":
    train()