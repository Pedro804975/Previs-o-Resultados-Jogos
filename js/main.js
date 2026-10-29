(function () {
  "use strict";
  function setTheme(theme) { document.documentElement.dataset.theme = theme; localStorage.setItem("theme", theme); document.getElementById("theme-toggle").textContent = theme === "dark" ? "☀" : "☾"; }
  document.addEventListener("DOMContentLoaded", function () {
    var saved = localStorage.getItem("theme"), preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"; setTheme(saved || preferred);
    document.getElementById("theme-toggle").addEventListener("click", function () { setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"); });
    var menu = document.querySelector(".menu-toggle"), nav = document.getElementById("primary-nav"); menu.addEventListener("click", function () { var open = nav.classList.toggle("is-open"); menu.setAttribute("aria-expanded", String(open)); }); nav.addEventListener("click", function (event) { if (event.target.tagName === "A") { nav.classList.remove("is-open"); menu.setAttribute("aria-expanded", "false"); } });
    var observer = new IntersectionObserver(function (entries) { entries.forEach(function (entry) { if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); } }); }, { threshold: .12 }); document.querySelectorAll(".reveal").forEach(function (element) { observer.observe(element); });
    var countObserver = new IntersectionObserver(function (entries, obs) { entries.forEach(function (entry) { if (!entry.isIntersecting) return; var el = entry.target, target = Number(el.dataset.count), start = performance.now(); function tick(now) { var progress = Math.min((now - start) / 900, 1); el.textContent = Math.floor(target * (1 - Math.pow(1 - progress, 3))); if (progress < 1) requestAnimationFrame(tick); } requestAnimationFrame(tick); obs.unobserve(el); }); }, { threshold: .8 }); document.querySelectorAll("[data-count]").forEach(function (el) { countObserver.observe(el); });
    document.querySelectorAll(".copy-button").forEach(function (button) { button.addEventListener("click", function () { navigator.clipboard.writeText(document.getElementById(button.dataset.copy).innerText).then(function () { var original = button.textContent; button.textContent = "Copiado!"; setTimeout(function () { button.textContent = original; }, 1400); }); }); });
  });
}());
