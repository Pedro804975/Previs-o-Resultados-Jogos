from app.poisson import probabilities, ranked_scores, score_matrix


def test_score_matrix_is_normalized():
    matrix = score_matrix(2.1, 0.9)
    assert len(matrix) == 11
    assert abs(sum(map(sum, matrix)) - 1) < 1e-9


def test_outcomes_are_normalized_and_ranked():
    matrix = score_matrix(2.1, 0.9)
    outcomes = probabilities(matrix)
    assert abs(sum(outcomes) - 1) < 1e-9
    scores = ranked_scores(matrix)
    assert scores[0][2] >= scores[-1][2]
