from pathlib import Path

from app.features import build_state, load_external_ranking, load_games


ROOT = Path(__file__).parents[2]


def test_runtime_state_loads_project_data():
    games = load_games(str(ROOT / "base_jogos_limpa.xlsx"))
    ranking = load_external_ranking(str(ROOT / "ranking_elo_externo.xlsx"))
    state = build_state(games, ranking)
    assert len(games) == 906
    assert len(state.teams) == 189
    assert "BRASIL" in state.teams
