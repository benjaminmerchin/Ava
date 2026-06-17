(function () {
  "use strict";

  var script = document.currentScript;
  var TENANT = (script && script.getAttribute("data-tenant")) || "lyvica";
  var ENDPOINT = (script && script.getAttribute("data-endpoint")) || "http://localhost:8000";

  // ---------- styles (self-contained: explicit colors so the host's dark theme can't leak in) ----------
  var css =
    ".ava-fab{position:fixed;bottom:24px;right:24px;width:56px;height:56px;border-radius:50%;background:#6c5ce7;color:#fff;border:none;font-size:24px;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.3);z-index:2147483000}" +
    ".ava-panel{position:fixed;bottom:92px;right:24px;width:360px;max-height:64vh;background:#fff;color:#1c2024;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.35);display:none;flex-direction:column;overflow:hidden;z-index:2147483000;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}" +
    ".ava-panel.open{display:flex}" +
    ".ava-head{display:flex;align-items:center;gap:10px;background:linear-gradient(135deg,#6c5ce7,#8e7bff);color:#fff;padding:12px 16px}" +
    ".ava-ava{width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;overflow:hidden}" +
    ".ava-ava img{width:100%;height:100%;object-fit:cover}" +
    ".ava-title{font-weight:600;line-height:1.1}" +
    ".ava-sub{font-size:11px;opacity:.85}" +
    ".ava-body{padding:14px 16px;overflow-y:auto;flex:1;font-size:14px;color:#1c2024;background:#fff}" +
    ".ava-msg{margin:8px 0;line-height:1.45;color:#1c2024}" +
    ".ava-msg.user{text-align:right;color:#4b5563}" +
    ".ava-next{color:#6c5ce7;font-size:13px;margin:2px 0 10px;font-weight:500}" +
    ".ava-foot{display:flex;border-top:1px solid #ececf0;background:#fff}" +
    ".ava-input{flex:1;border:none;padding:13px 14px;font-size:14px;outline:none;color:#1c2024;background:#fff}" +
    ".ava-input::placeholder{color:#9aa0a6}" +
    ".ava-send{border:none;background:#6c5ce7;color:#fff;padding:0 18px;cursor:pointer;font-size:16px}" +
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
    '<div class="ava-head">' +
    '<div class="ava-ava" id="ava-ava">A</div>' +
    '<div><div class="ava-title">Ava</div><div class="ava-sub">Support assistant</div></div>' +
    "</div>" +
    '<div class="ava-body" id="ava-body"><div class="ava-msg">Hi 👋 Ask me anything about this page — I can see what\'s blocked and why.</div></div>' +
    '<div class="ava-foot"><input class="ava-input" id="ava-input" placeholder="Type your question…"/><button class="ava-send" id="ava-send">➤</button></div>';

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

  function addMsg(text, next, who) {
    var d = document.createElement("div");
    d.className = "ava-msg" + (who === "user" ? " user" : "");
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
    try {
      var el = document.querySelector(sel);
      if (el) {
        el.classList.add("ava-highlight");
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        current = el;
      }
    } catch (e) {
      /* invalid selector — ignore */
    }
  }

  // ---------- ask ----------
  function send() {
    var q = input.value.trim();
    if (!q) return;
    addMsg(q, null, "user");
    input.value = "";
    var thinking = document.createElement("div");
    thinking.className = "ava-msg";
    thinking.textContent = "…";
    body.appendChild(thinking);
    body.scrollTop = body.scrollHeight;

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
        thinking.remove();
        addMsg(res.speech || "…", res.next_step);
        highlight(res.highlight_selector);
        if (window.AvaSpeak) window.AvaSpeak(res.speech); // avatar TTS hook (milestone 4)
      })
      .catch(function () {
        thinking.remove();
        addMsg("Sorry, I couldn't reach the assistant backend.");
      });
  }

  // expose for the avatar layer / debugging
  window.Ava = { captureDom: captureDom, highlight: highlight, ask: send };
})();
