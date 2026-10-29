from pathlib import Path
import json
import os

import numpy as np

from .features import RuntimeState, build_state, feature_vector, load_external_ranking, load_games, normalize_name
from .poisson import probabilities, ranked_scores, score_matrix


class PredictionRuntime:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        data_dir = Path(os.getenv("DATA_DIR", str(project_root)))
        model_dir = Path(os.getenv("MODEL_DIR", str(project_root / "backend" / "models")))
        games = load_games(str(data_dir / "base_jogos_limpa.xlsx"))
        ranking = load_external_ranking(str(data_dir / "ranking_elo_externo.xlsx"))
        self.state: RuntimeState = build_state(games, ranking)
        self.model = None
        self.scaler = None
        self.version = os.getenv("MODEL_VERSION", "v3-runtime-baseline")
        self.mode = "baseline"
        self._load_bundle(model_dir)

    def _load_bundle(self, model_dir: Path) -> None:
        metadata_path = model_dir / "metadata.json"
        model_path = model_dir / "modelo_prever_jogos_v3.keras"
        scaler_path = model_dir / "scaler.joblib"
        if not (metadata_path.exists() and model_path.exists() and scaler_path.exists()):
            return
        try:
            import joblib
            from tensorflow import keras

            self.model = keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.version = str(metadata.get("version", self.version))
            self.mode = "keras"
        except (ImportError, OSError, ValueError, TypeError):
            self.model = None
            self.scaler = None

    def _baseline_goals(self, team_a: str, team_b: str) -> tuple[float, float]:
        features = feature_vector(self.state, team_a, team_b)[0]
        league_scored = float(self.state.games[["GOLS A", "GOLS B"]].to_numpy().mean())
        league_scored = max(league_scored, 0.1)
        elo = features[0]
        a_points, a_scored, a_conceded, _, _ = features[1:6]
        b_points, b_scored, b_conceded, _, _ = features[6:11]
        expected_a = league_scored + 0.28 * (a_points - 0.5) + 0.16 * (a_scored - league_scored)
        expected_a += 0.12 * (b_conceded - league_scored) + 0.0008 * elo
        expected_b = league_scored + 0.28 * (b_points - 0.5) + 0.16 * (b_scored - league_scored)
        expected_b += 0.12 * (a_conceded - league_scored) - 0.0008 * elo
        return max(0.05, min(expected_a, 5.0)), max(0.05, min(expected_b, 5.0))

    def _expected_goals(self, team_a: str, team_b: str) -> tuple[float, float]:
        if self.mode == "keras" and self.model is not None and self.scaler is not None:
            values = self.model.predict(self.scaler.transform(feature_vector(self.state, team_a, team_b)), verbose=0)[0]
            return float(values[0]), float(values[1])
        return self._baseline_goals(team_a, team_b)

    def teams(self) -> list[dict[str, object]]:
        return [
            {"name": name, "games": snapshot.games}
            for name, snapshot in sorted(self.state.teams.items())
        ]

    def predict(self, raw_team_a: str, raw_team_b: str) -> dict[str, object]:
        team_a, team_b = normalize_name(raw_team_a), normalize_name(raw_team_b)
        if team_a not in self.state.teams:
            raise KeyError(f"Seleção não encontrada: {raw_team_a}")
        if team_b not in self.state.teams:
            raise KeyError(f"Seleção não encontrada: {raw_team_b}")
        if team_a == team_b:
            raise ValueError("Escolha duas seleções diferentes.")

        expected_a, expected_b = self._expected_goals(team_a, team_b)
        matrix = score_matrix(expected_a, expected_b)
        win_a, draw, win_b = probabilities(matrix)
        scores = ranked_scores(matrix)
        warnings = []
        for team in (team_a, team_b):
            if self.state.teams[team].games < 5:
                warnings.append(f"{team} tem menos de 5 jogos na base.")
        return {
            "team_a": team_a,
            "team_b": team_b,
            "expected_goals": {"team_a": round(expected_a, 3), "team_b": round(expected_b, 3)},
            "probabilities": {"win_a": round(win_a, 6), "draw": round(draw, 6), "win_b": round(win_b, 6)},
            "most_likely_score": {"goals_a": scores[0][0], "goals_b": scores[0][1], "probability": round(scores[0][2], 6)},
            "top_scores": [
                {"goals_a": a, "goals_b": b, "probability": round(probability, 6)}
                for a, b, probability in scores[:5]
            ],
            "warnings": warnings,
            "model_mode": self.mode,
            "model_version": self.version,
            "data_last_updated": self.state.data_last_updated.isoformat(),
        }
