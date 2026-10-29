"""Treina o pacote opcional Keras sem editar o notebook original."""
from pathlib import Path
import json
import os

import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

from app.features import build_state, feature_vector, load_external_ranking, load_games


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = Path(os.getenv("DATA_DIR", str(project_root)))
    model_dir = Path(os.getenv("MODEL_DIR", str(project_root / "backend" / "models")))
    model_dir.mkdir(parents=True, exist_ok=True)
    games = load_games(str(data_dir / "base_jogos_limpa.xlsx"))
    ranking = load_external_ranking(str(data_dir / "ranking_elo_externo.xlsx"))
    state = build_state(games, ranking)
    rows = []
    targets = []
    for index in range(len(games)):
        historical_state = build_state(games.iloc[:index], ranking)
        row = games.iloc[index]
        rows.append(feature_vector(historical_state, row["TIME A"], row["TIME B"])[0])
        targets.append([float(row["GOLS A"]), float(row["GOLS B"])])
    x = np.vstack(rows)
    y = np.asarray(targets, dtype=np.float32)
    scaler = StandardScaler().fit(x)

    from tensorflow import keras
    from tensorflow.keras import layers, regularizers

    keras.utils.set_random_seed(42)
    model = keras.Sequential([
        layers.Input(shape=(x.shape[1],)),
        layers.Dense(16, activation="relu", kernel_regularizer=regularizers.l2(0.01)),
        layers.Dropout(0.3),
        layers.Dense(8, activation="relu", kernel_regularizer=regularizers.l2(0.01)),
        layers.Dropout(0.3),
        layers.Dense(2, activation="exponential"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(0.003), loss="poisson")
    model.fit(scaler.transform(x), y, epochs=300, batch_size=32, validation_split=0.15, callbacks=[keras.callbacks.EarlyStopping(patience=25, restore_best_weights=True)], verbose=0)
    model.save(model_dir / "modelo_prever_jogos_v3.keras")
    joblib.dump(scaler, model_dir / "scaler.joblib")
    (model_dir / "metadata.json").write_text(json.dumps({"version": "v3-trained", "features": 11, "data_last_updated": str(state.data_last_updated)}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
