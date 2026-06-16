(function () {
  "use strict";

  var script = document.currentScript;
  var TENANT = (script && script.getAttribute("data-tenant")) || "lyvica";
  var ENDPOINT = (script && script.getAttribute("data-endpoint")) || "http://localhost:8000";

  // ---------- styles ----------
  var css =
    ".ava-fab{position:fixed;bottom:24px;right:24px;width:56px;height:56px;border-radius:50%;background:#6c5ce7;color:#fff;border:none;font-size:24px;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.25);z-index:2147483000}" +
    ".ava-panel{position:fixed;bottom:92px;right:24px;width:340px;max-height:60vh;background:#fff;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;z-index:2147483000;font-family:system-ui,-apple-system,sans-serif}" +
    ".ava-panel.open{display:flex}" +
    ".ava-head{background:#6c5ce7;color:#fff;padding:12px 16px;font-weight:600}" +
    ".ava-body{padding:12px 16px;overflow-y:auto;flex:1;font-size:14px;color:#222}" +
    ".ava-msg{margin:8px 0;line-height:1.45}" +
    ".ava-next{color:#6c5ce7;font-size:13px;margin:2px 0 8px}" +
    ".ava-foot{display:flex;border-top:1px solid #eee}" +
    ".ava-input{flex:1;border:none;padding:12px;font-size:14px;outline:none}" +
    ".ava-send{border:none;background:#6c5ce7;color:#fff;padding:0 16px;cursor:pointer;font-size:16px}" +
    ".ava-highlight{outline:3px solid #6c5ce7 !important;outline-offset:2px;border-radius:4px}";
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  // ---------- UI ----------
  var fab = document.createElement("button");
  fab.className = "ava-fab";
  fab.textContent = "💬";
  fab.title = "Ava";

  var panel = document.createElement("div");
  panel.className = "ava-panel";
  panel.innerHTML =
    '<div class="ava-head">Ava</div>' +
    '<div class="ava-body" id="ava-body"><div class="ava-msg">Bonjour 👋 Pose-moi une question sur cette page.</div></div>' +
    '<div class="ava-foot"><input class="ava-input" id="ava-input" placeholder="Écris ta question…"/><button class="ava-send" id="ava-send">➤</button></div>';

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var body = panel.querySelector("#ava-body");
  var input = panel.querySelector("#ava-input");
  fab.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) input.focus();
  });
  panel.querySelector("#ava-send").addEventListener("click", send);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") send();
  });

  function addMsg(text, next) {
    var d = document.createElement("div");
    d.className = "ava-msg";
    d.textContent = text;
    body.appendChild(d);
    if (next) {
      var n = document.createElement("div");
      n.className = "ava-next";
      n.textContent = "→ " + next;
      body.appendChild(n);
    }
    body.scrollTop = body.scrollHeight;
  }

  // ---------- DOM capture ----------
  function selectorFor(el) {
    if (el.hasAttribute("data-ava")) return '[data-ava="' + el.getAttribute("data-ava") + '"]';
    if (el.id) return "#" + (window.CSS && CSS.escape ? CSS.escape(el.id) : el.id);
    var aria = el.getAttribute("aria-label");
    if (aria) return el.tagName.toLowerCase() + '[aria-label="' + aria + '"]';
    var name = el.getAttribute("name");
    if (name) return el.tagName.toLowerCase() + '[name="' + name + '"]';
    return null;
  }

  function errorFor(el) {
    if (el.getAttribute("aria-invalid") === "true") {
      var d = el.getAttribute("aria-describedby");
      if (d) {
        var node = document.getElementById(d);
        if (node) return node.textContent.trim();
      }
    }
    if (el.validationMessage) return el.validationMessage;
    return null;
  }

  function captureDom() {
    var nodes = document.querySelectorAll(
      "button,a,input,select,textarea,[role=button],[data-ava]"
    );
    var els = [];
    nodes.forEach(function (el) {
      var sel = selectorFor(el);
      if (!sel) return;
      var rect = el.getBoundingClientRect();
      els.push({
        selector: sel,
        tag: el.tagName.toLowerCase(),
        label: (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 80) || null,
        text: (el.value || "").toString().slice(0, 80) || null,
        disabled: !!(el.disabled || el.getAttribute("aria-disabled") === "true"),
        visible: rect.width > 0 && rect.height > 0,
        error: errorFor(el),
        aria: {},
      });
    });
    return { url: location.href, title: document.title, elements: els.slice(0, 60) };
  }

  // ---------- highlight ----------
  var current = null;
  function highlight(sel) {
    if (current) {
      current.classList.remove("ava-highlight");
      current = null;
    }
    if (!sel) return;
    var el = document.querySelector(sel);
    if (el) {
      el.classList.add("ava-highlight");
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      current = el;
    }
  }

  // ---------- ask ----------
  function send() {
    var q = input.value.trim();
    if (!q) return;
    addMsg("🧑 " + q);
    input.value = "";
    fetch(ENDPOINT + "/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: TENANT,
        question: q,
        url: location.href,
        dom: captureDom(),
      }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (res) {
        addMsg("🤖 " + (res.speech || "…"), res.next_step);
        highlight(res.highlight_selector);
        if (window.AvaSpeak) window.AvaSpeak(res.speech); // avatar TTS hook (milestone 4)
      })
      .catch(function () {
        addMsg("🤖 Désolé, je n'ai pas pu répondre (backend injoignable).");
      });
  }

  // expose for the avatar layer / debugging
  window.Ava = { captureDom: captureDom, highlight: highlight, ask: send };
})();
