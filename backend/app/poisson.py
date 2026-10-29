from math import exp, factorial


MAX_GOALS = 11


def poisson_probability(goals: int, expected: float) -> float:
    return exp(-expected) * expected**goals / factorial(goals)


def score_matrix(expected_a: float, expected_b: float) -> list[list[float]]:
    matrix = [
        [
            poisson_probability(a, expected_a) * poisson_probability(b, expected_b)
            for b in range(MAX_GOALS)
        ]
        for a in range(MAX_GOALS)
    ]
    total = sum(sum(row) for row in matrix)
    return [[value / total for value in row] for row in matrix]


def probabilities(matrix: list[list[float]]) -> tuple[float, float, float]:
    win_a = sum(matrix[a][b] for a in range(MAX_GOALS) for b in range(MAX_GOALS) if a > b)
    draw = sum(matrix[a][a] for a in range(MAX_GOALS))
    win_b = sum(matrix[a][b] for a in range(MAX_GOALS) for b in range(MAX_GOALS) if a < b)
    return win_a, draw, win_b


def ranked_scores(matrix: list[list[float]]) -> list[tuple[int, int, float]]:
    scores = [
        (a, b, matrix[a][b])
        for a in range(MAX_GOALS)
        for b in range(MAX_GOALS)
    ]
    return sorted(scores, key=lambda score: score[2], reverse=True)
