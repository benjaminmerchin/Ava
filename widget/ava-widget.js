(function () {
  "use strict";

  var script = document.currentScript;
  var TENANT = (script && script.getAttribute("data-tenant")) || "lyvica";
  var ENDPOINT = (script && script.getAttribute("data-endpoint")) || "http://localhost:8000";

  // ---------- styles (self-contained; explicit colors so the host theme can't leak in) ----------
  var css =
    ".ava-fab{position:fixed;bottom:24px;right:24px;width:60px;height:60px;border-radius:50%;background:#6c5ce7;color:#fff;border:none;cursor:pointer;box-shadow:0 8px 24px rgba(108,92,231,.5);z-index:2147483000;overflow:hidden;padding:0}" +
    ".ava-fab img{width:100%;height:100%;object-fit:cover}" +
    ".ava-panel{position:fixed;bottom:96px;right:24px;width:360px;max-height:72vh;background:#fff;color:#1c2024;border-radius:18px;box-shadow:0 14px 44px rgba(0,0,0,.4);display:none;flex-direction:column;overflow:hidden;z-index:2147483000;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}" +
    ".ava-panel.open{display:flex}" +
    ".ava-hero{position:relative;height:200px;background:linear-gradient(150deg,#6c5ce7,#3a2f7a);flex-shrink:0}" +
    ".ava-stage{width:100%;height:100%;border:0;display:block;background:transparent}" +
    ".ava-headbar{position:absolute;top:10px;left:14px;right:10px;display:flex;align-items:flex-start;justify-content:space-between;pointer-events:none}" +
    ".ava-headbar .ava-title{color:#fff;font-weight:700;line-height:1.1;text-shadow:0 1px 5px rgba(0,0,0,.45)}" +
    ".ava-headbar .ava-sub{color:rgba(255,255,255,.85);font-size:11px;text-shadow:0 1px 4px rgba(0,0,0,.45)}" +
    ".ava-mute{pointer-events:auto;background:rgba(0,0,0,.28);border:none;color:#fff;width:32px;height:32px;border-radius:9px;cursor:pointer;font-size:15px}" +
    ".ava-body{padding:14px 16px;overflow-y:auto;flex:1;font-size:14px;color:#1c2024;background:#fff}" +
    ".ava-msg{margin:8px 0;line-height:1.45;color:#1c2024}" +
    ".ava-msg.user{text-align:right;color:#4b5563}" +
    ".ava-next{color:#6c5ce7;font-size:13px;margin:2px 0 10px;font-weight:500}" +
    ".ava-foot{display:flex;border-top:1px solid #ececf0;background:#fff}" +
    ".ava-input{flex:1;border:none;padding:13px 14px;font-size:14px;outline:none;color:#1c2024;background:#fff}" +
    ".ava-input::placeholder{color:#9aa0a6}" +
    ".ava-send{border:none;background:#6c5ce7;color:#fff;padding:0 18px;cursor:pointer;font-size:16px}" +
    ".ava-highlight{outline:3px solid #6c5ce7 !important;outline-offset:3px;border-radius:6px;animation:ava-ring 1.1s ease-in-out infinite}" +
    "@keyframes ava-ring{0%,100%{box-shadow:0 0 0 0 rgba(108,92,231,.55)}50%{box-shadow:0 0 0 9px rgba(108,92,231,0)}}" +
    ".ava-pointer{position:fixed;z-index:2147483001;pointer-events:none;display:flex;flex-direction:column;align-items:center;transform:translateX(-50%)}" +
    ".ava-pointer.below{flex-direction:column-reverse}" +
    ".ava-pointer .ava-bubble{background:#6c5ce7;color:#fff;font:600 12px/1.3 system-ui,sans-serif;padding:6px 10px;border-radius:10px;max-width:230px;text-align:center;box-shadow:0 6px 18px rgba(108,92,231,.5)}" +
    ".ava-pointer .ava-arrow{font-size:26px;line-height:1;animation:ava-bounce .8s ease-in-out infinite;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}" +
    "@keyframes ava-bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(7px)}}" +
    ".ava-typing{display:inline-flex;gap:4px;align-items:center;padding:3px 0}" +
    ".ava-typing span{width:7px;height:7px;border-radius:50%;background:#6c5ce7;display:inline-block;animation:ava-blink 1.2s infinite ease-in-out both}" +
    ".ava-typing span:nth-child(2){animation-delay:.2s}.ava-typing span:nth-child(3){animation-delay:.4s}" +
    "@keyframes ava-blink{0%,80%,100%{transform:scale(.6);opacity:.35}40%{transform:scale(1);opacity:1}}";
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  // ---------- UI ----------
  var fab = document.createElement("button");
  fab.className = "ava-fab";
  fab.title = "Ava";
  fab.innerHTML = '<img src="' + ENDPOINT + '/ava-face.jpg" alt="Ava"/>';

  var panel = document.createElement("div");
  panel.className = "ava-panel";
  panel.innerHTML =
    '<div class="ava-hero">' +
    '<iframe class="ava-stage" id="ava-stage" src="' + ENDPOINT + '/avatar" title="Ava" allow="autoplay"></iframe>' +
    '<div class="ava-headbar">' +
    '<div><div class="ava-title">Ava</div><div class="ava-sub">Support assistant</div></div>' +
    '<button class="ava-mute" id="ava-mute" title="Mute voice">🔊</button>' +
    "</div></div>" +
    '<div class="ava-body" id="ava-body"><div class="ava-msg">Hi 👋 Ask me anything about this page — I can see what\'s blocked and point you to the fix.</div></div>' +
    '<div class="ava-foot"><input class="ava-input" id="ava-input" placeholder="Type your question…"/><button class="ava-send" id="ava-send">➤</button></div>';

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var body = panel.querySelector("#ava-body");
  var input = panel.querySelector("#ava-input");
  var stage = panel.querySelector("#ava-stage");
  var muteBtn = panel.querySelector("#ava-mute");

  function avatarSend(msg) {
    try { stage.contentWindow.postMessage(msg, "*"); } catch (e) { /* ignore */ }
  }

  fab.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) input.focus();
    else clearPointer();
  });
  panel.querySelector("#ava-send").addEventListener("click", send);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") send();
  });

  var muted = false;
  muteBtn.addEventListener("click", function () {
    muted = !muted;
    muteBtn.textContent = muted ? "🔇" : "🔊";
    avatarSend({ ava: "mute", value: muted });
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

  // ---------- attention pointer ----------
  var current = null;
  var pointer = null;

  function clearPointer() {
    if (current) { current.classList.remove("ava-highlight"); current = null; }
    if (pointer) { pointer.remove(); pointer = null; }
    window.removeEventListener("scroll", positionPointer, true);
    window.removeEventListener("resize", positionPointer);
  }

  function positionPointer() {
    if (!current || !pointer) return;
    var r = current.getBoundingClientRect();
    var above = r.top > 90;
    pointer.classList.toggle("below", !above);
    pointer.querySelector(".ava-arrow").textContent = above ? "👇" : "👆";
    pointer.style.left = r.left + r.width / 2 + "px";
    var h = pointer.offsetHeight;
    pointer.style.top = (above ? r.top - h - 6 : r.bottom + 6) + "px";
  }

  function highlight(selector, label) {
    clearPointer();
    if (!selector) return;
    var el;
    try { el = document.querySelector(selector); } catch (e) { return; }
    if (!el) return;
    current = el;
    el.classList.add("ava-highlight");
    el.scrollIntoView({ behavior: "smooth", block: "center" });

    pointer = document.createElement("div");
    pointer.className = "ava-pointer";
    pointer.innerHTML =
      (label ? '<div class="ava-bubble"></div>' : "") + '<div class="ava-arrow">👇</div>';
    if (label) pointer.querySelector(".ava-bubble").textContent = label;
    document.body.appendChild(pointer);

    window.addEventListener("scroll", positionPointer, true);
    window.addEventListener("resize", positionPointer);
    var t0 = null;
    function follow(ts) {
      if (t0 === null) t0 = ts;
      positionPointer();
      if (ts - t0 < 700 && pointer) requestAnimationFrame(follow);
    }
    requestAnimationFrame(follow);
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
    return { url: location.href, title: document.title, elements: els.slice(0, 120) };
  }

  // ---------- ask ----------
  function send() {
    var q = input.value.trim();
    if (!q) return;
    addMsg(q, null, "user");
    input.value = "";
    var thinking = document.createElement("div");
    thinking.className = "ava-msg";
    thinking.innerHTML =
      '<span class="ava-typing"><span></span><span></span><span></span></span>';
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
      .then(function (r) { return r.json(); })
      .then(function (res) {
        thinking.remove();
        addMsg(res.speech || "…", res.next_step);
        highlight(res.highlight_selector, res.next_step);
        avatarSend({ ava: "speak", text: res.speech }); // avatar speaks + lip-syncs
      })
      .catch(function () {
        thinking.remove();
        addMsg("Sorry, I couldn't reach the assistant backend.");
      });
  }

  window.Ava = { captureDom: captureDom, highlight: highlight, ask: send };
})();
