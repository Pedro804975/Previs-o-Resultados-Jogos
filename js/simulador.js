(function () {
  "use strict";
  var MAX = 11;
  function factorial(n) { var result = 1; for (var i = 2; i <= n; i += 1) result *= i; return result; }
  function poisson(k, lambda) { return Math.exp(-lambda) * Math.pow(lambda, k) / factorial(k); }
  function calculate(a, b) {
    var matrix = [], total = 0, i, j;
    for (i = 0; i < MAX; i += 1) { matrix[i] = []; for (j = 0; j < MAX; j += 1) { matrix[i][j] = poisson(i, a) * poisson(j, b); total += matrix[i][j]; } }
    var outcomes = [0, 0, 0];
    for (i = 0; i < MAX; i += 1) for (j = 0; j < MAX; j += 1) outcomes[i > j ? 0 : i === j ? 1 : 2] += matrix[i][j];
    return { matrix: matrix, outcomes: outcomes.map(function (value) { return value / total; }), total: total };
  }
  function render() {
    var a = Number(document.getElementById("goals-a").value), b = Number(document.getElementById("goals-b").value);
    if (!Number.isFinite(a) || !Number.isFinite(b) || a <= 0 || b <= 0) return;
    var result = calculate(a, b), matrix = result.matrix, cells = [], scores = [], i, j;
    for (i = 0; i < MAX; i += 1) for (j = 0; j < MAX; j += 1) scores.push({ a: i, b: j, value: matrix[i][j] / result.total });
    scores.sort(function (x, y) { return y.value - x.value; });
    document.getElementById("result-goals").textContent = a.toFixed(1) + " × " + b.toFixed(1);
    ["prob-a", "prob-draw", "prob-b"].forEach(function (id, index) { document.getElementById(id).textContent = (result.outcomes[index] * 100).toFixed(1) + "%"; });
    document.getElementById("likely-score").textContent = scores[0].a + " × " + scores[0].b;
    document.getElementById("likely-score-prob").textContent = (scores[0].value * 100).toFixed(1) + "% de chance";
    var heatmap = document.getElementById("heatmap"), max = scores[0].value;
    for (i = 0; i < MAX; i += 1) for (j = 0; j < MAX; j += 1) { var value = matrix[i][j] / result.total; var cell = document.createElement("span"); cell.className = "heat-cell"; cell.textContent = (value * 100).toFixed(0); cell.title = i + " × " + j + ": " + (value * 100).toFixed(2) + "%"; cell.style.backgroundColor = "rgba(55, 212, 134, " + Math.max(.08, value / max) + ")"; cells.push(cell); }
    heatmap.replaceChildren.apply(heatmap, cells);
    var list = document.getElementById("top-scores-list"); list.replaceChildren.apply(list, scores.slice(0, 5).map(function (score) { var li = document.createElement("li"); li.textContent = score.a + " × " + score.b + " (" + (score.value * 100).toFixed(1) + "%)"; return li; }));
  }
  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("simulator-form");
    form.addEventListener("submit", function (event) { event.preventDefault(); render(); });
    form.addEventListener("click", function (event) {
      if (event.target.closest("button[type='submit']")) {
        event.preventDefault();
        render();
      }
    });
    render();
  });
}());
