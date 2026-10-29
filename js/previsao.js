(function () {
  "use strict";
  var localApi = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") &&
    window.location.port !== "8080" ? "http://127.0.0.1:8000" : "/api";
  var apiBase = window.PREDICTION_API_URL || localApi;
  var form, teamA, teamB, button, status, error, result;

  function setMessage(message) {
    error.textContent = message;
    error.hidden = !message;
  }

  function percentage(value) {
    return (value * 100).toFixed(1) + "%";
  }

  function populateTeams(teams) {
    [teamA, teamB].forEach(function (select) {
      select.replaceChildren(new Option("Selecione uma seleção", ""));
      teams.forEach(function (team) {
        select.appendChild(new Option(team.name + " (" + team.games + " jogos)", team.name));
      });
    });
    button.disabled = false;
    status.textContent = "API ONLINE";
  }

  function loadTeams() {
    return fetch(apiBase + "/teams", { headers: { Accept: "application/json" } })
      .then(function (response) {
        if (!response.ok) throw new Error("A API respondeu com erro " + response.status + ".");
        return response.json();
      })
      .then(function (payload) { populateTeams(payload.teams); })
      .catch(function () {
        status.textContent = "API OFFLINE";
        setMessage("Não foi possível conectar à API. Inicie o Docker Compose e tente novamente.");
      });
  }

  function renderPrediction(data) {
    document.getElementById("prediction-goals").textContent =
      data.expected_goals.team_a.toFixed(1) + " × " + data.expected_goals.team_b.toFixed(1);
    document.getElementById("prediction-score").textContent =
      data.most_likely_score.goals_a + " × " + data.most_likely_score.goals_b;
    document.getElementById("prediction-win-a").textContent = percentage(data.probabilities.win_a);
    document.getElementById("prediction-draw").textContent = percentage(data.probabilities.draw);
    document.getElementById("prediction-win-b").textContent = percentage(data.probabilities.win_b);
    document.getElementById("prediction-meta").textContent =
      "Modo: " + (data.model_mode === "keras" ? "rede Keras" : "baseline runtime") +
      " · " + data.model_version + " · dados até " + data.data_last_updated;
    var warnings = document.getElementById("prediction-warnings");
    warnings.replaceChildren.apply(warnings, data.warnings.map(function (warning) {
      var item = document.createElement("li");
      item.textContent = warning;
      return item;
    }));
    result.hidden = false;
  }

  function predict(event) {
    event.preventDefault();
    setMessage("");
    button.disabled = true;
    button.firstChild.textContent = "Consultando... ";
    fetch(apiBase + "/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ team_a: teamA.value, team_b: teamB.value })
    })
      .then(function (response) {
        return response.json().then(function (payload) {
          if (!response.ok) throw new Error(payload.detail || "Não foi possível gerar a previsão.");
          return payload;
        });
      })
      .then(renderPrediction)
      .catch(function (requestError) { setMessage(requestError.message); })
      .finally(function () {
        button.disabled = false;
        button.firstChild.textContent = "Gerar previsão ";
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    form = document.getElementById("prediction-form");
    if (!form) return;
    teamA = document.getElementById("team-a");
    teamB = document.getElementById("team-b");
    button = document.getElementById("predict-button");
    status = document.getElementById("api-status");
    error = document.getElementById("prediction-error");
    result = document.getElementById("prediction-result");
    form.addEventListener("submit", predict);
    loadTeams();
  });
}());
