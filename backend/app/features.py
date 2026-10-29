from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date
import re
import unicodedata

import numpy as np
import pandas as pd


ALIASES = {
    "RD CONGO": "REPUBLICA DEMOCRATICA DO CONGO",
    "REP. DEM. DO CONGO": "REPUBLICA DEMOCRATICA DO CONGO",
    "REPUBLICA DA COREIA": "COREIA DO SUL",
    "REPUBLICA TCHECA": "TCHEQUIA",
    "EUA": "ESTADOS UNIDOS",
    "USA": "ESTADOS UNIDOS",
    "HOLANDA": "PAISES BAIXOS",
    "IRAO": "IRA",
}

FEATURE_NAMES = (
    "Elo_dif",
    "A_pontos",
    "A_gols_feitos",
    "A_gols_sofridos",
    "A_jogos_hist",
    "A_dias_desc",
    "B_pontos",
    "B_gols_feitos",
    "B_gols_sofridos",
    "B_jogos_hist",
    "B_dias_desc",
)


def normalize_name(value: object) -> str:
    text = str(value).strip().upper()
    text = "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"\s+", " ", text)
    return ALIASES.get(text, text)


def load_games(path: str) -> pd.DataFrame:
    workbook = pd.read_excel(path, sheet_name="jogos")
    columns = {str(column).strip().upper(): column for column in workbook.columns}
    required = {"DATA", "TIME A", "TIME B", "GOLS A", "GOLS B"}
    if not required.issubset(columns):
        raise ValueError("A aba jogos não possui as colunas obrigatórias.")
    ordered_columns = ["DATA", "TIME A", "TIME B", "GOLS A", "GOLS B"]
    games = workbook[[columns[name] for name in ordered_columns]].copy()
    games.columns = ["DATA", "TIME A", "TIME B", "GOLS A", "GOLS B"]
    games["DATA"] = pd.to_datetime(games["DATA"], errors="coerce")
    games["TIME A"] = games["TIME A"].map(normalize_name)
    games["TIME B"] = games["TIME B"].map(normalize_name)
    games["GOLS A"] = pd.to_numeric(games["GOLS A"], errors="coerce")
    games["GOLS B"] = pd.to_numeric(games["GOLS B"], errors="coerce")
    games = games.dropna()
    games = games[games["TIME A"] != games["TIME B"]]
    return games.sort_values(["DATA", "TIME A", "TIME B"]).reset_index(drop=True)


def load_external_ranking(path: str) -> dict[str, float]:
    ranking = pd.read_excel(path, sheet_name=None)
    result: dict[str, float] = {}
    for frame in ranking.values():
        columns = {str(column).strip().upper(): column for column in frame.columns}
        team_column = next(
            (columns[name] for name in ("SELECAO", "SELEÇÃO", "TIME", "PAIS", "PAÍS") if name in columns),
            None,
        )
        elo_column = next(
            (columns[name] for name in ("ELO", "RATING", "PONTOS") if name in columns),
            None,
        )
        if team_column is None or elo_column is None or "JOGOS_NA_BASE" in columns:
            continue
        for team, elo in zip(frame[team_column], frame[elo_column]):
            try:
                result[normalize_name(team)] = float(elo)
            except (TypeError, ValueError):
                continue
    return result


@dataclass
class TeamSnapshot:
    elo: float
    history: list[tuple[float, float, float]]
    last_game: pd.Timestamp | None
    games: int


@dataclass
class RuntimeState:
    teams: dict[str, TeamSnapshot]
    games: pd.DataFrame
    external_ranking_size: int
    data_last_updated: date


def build_state(games: pd.DataFrame, initial_elo: dict[str, float], k: float = 25.0) -> RuntimeState:
    ratings: dict[str, float] = {}
    histories: defaultdict[str, deque[tuple[float, float, float]]] = defaultdict(lambda: deque(maxlen=5))
    last_games: dict[str, pd.Timestamp] = {}
    counts: defaultdict[str, int] = defaultdict(int)

    def rating(team: str) -> float:
        if team not in ratings:
            ratings[team] = initial_elo.get(team, 1500.0)
        return ratings[team]

    for row in games.itertuples(index=False):
        team_a, team_b = row[1], row[2]
        rating_a, rating_b = rating(team_a), rating(team_b)
        expected = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        actual = 1.0 if row[3] > row[4] else 0.5 if row[3] == row[4] else 0.0
        margin = abs(int(row[3]) - int(row[4]))
        weight = 1.0 if margin <= 1 else 1.5 if margin == 2 else (11 + margin) / 8
        adjustment = k * weight * (actual - expected)
        ratings[team_a] += adjustment
        ratings[team_b] -= adjustment

        for team, scored, conceded in (
            (team_a, float(row[3]), float(row[4])),
            (team_b, float(row[4]), float(row[3])),
        ):
            points = 1.0 if scored > conceded else 0.5 if scored == conceded else 0.0
            histories[team].append((points, scored, conceded))
            last_games[team] = row[0]
            counts[team] += 1

    teams = {
        team: TeamSnapshot(ratings[team], list(histories[team]), last_games.get(team), counts[team])
        for team in ratings
    }
    last_updated = games["DATA"].max().date() if not games.empty else date(1970, 1, 1)
    return RuntimeState(teams, games, len(initial_elo), last_updated)


def feature_vector(state: RuntimeState, team_a: str, team_b: str) -> np.ndarray:
    snapshot_a = state.teams.get(team_a, TeamSnapshot(1500.0, [], None, 0))
    snapshot_b = state.teams.get(team_b, TeamSnapshot(1500.0, [], None, 0))
    latest = pd.Timestamp(state.data_last_updated)

    def recent(snapshot: TeamSnapshot) -> list[float]:
        if not snapshot.history or snapshot.last_game is None:
            return [0.0, 0.0, 0.0, 0.0, 365.0]
        games = snapshot.history
        days = min(float((latest - snapshot.last_game).days), 365.0)
        return [
            sum(game[0] for game in games) / len(games),
            sum(game[1] for game in games) / len(games),
            sum(game[2] for game in games) / len(games),
            float(len(games)),
            days,
        ]

    return np.array([[snapshot_a.elo - snapshot_b.elo, *recent(snapshot_a), *recent(snapshot_b)]], dtype=np.float32)
