// scroll-dive engine (ADR 0176): scroll position picks a frame from a numbered JPEG sequence and draws it on a
// sticky canvas. Same-origin files only; no network beyond the page's own folder.
(function () {
  "use strict";
  var PX_PER_FRAME = 14;       // scroll distance per frame
  var WINDOW = 24;             // frames preloaded ahead of and behind the current one
  var EASE = 0.18;             // how fast the shown frame catches up with the scroll target

  function pad(n, w) { var s = String(n); while (s.length < w) s = "0" + s; return s; }

  function start(man) {
    var root = document.getElementById("dive");
    var track = document.getElementById("track");
    var canvas = document.getElementById("stage");
    var caption = document.getElementById("caption");
    var ctx = canvas.getContext("2d");
    var cache = {};
    var target = 0, shown = 0, drawn = -1, dirty = true;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function src(n) { return man.pattern.replace("{n}", pad(n, man.pad)); }

    function img(n) {
      if (n < 0 || n >= man.frames) return null;
      if (!cache[n]) {
        var im = new Image();
        im.decoding = "async";
        im.onload = function () { if (Math.round(shown) === n) dirty = true; };
        im.src = src(n);
        cache[n] = im;
      }
      return cache[n];
    }

    function preload(center) {
      for (var d = 0; d <= WINDOW; d++) { img(center + d); img(center - d); }
      for (var k in cache) {   // keep memory flat on long pages
        if (Math.abs(k - center) > WINDOW * 4) { delete cache[k]; }
      }
    }

    function nearestLoaded(n) {
      for (var d = 0; d <= WINDOW; d++) {
        var a = cache[n - d], b = cache[n + d];
        if (a && a.complete && a.naturalWidth) return a;
        if (b && b.complete && b.naturalWidth) return b;
      }
      return null;
    }

    function resize() {
      var r = window.devicePixelRatio || 1;
      canvas.width = Math.round(canvas.clientWidth * r);
      canvas.height = Math.round(canvas.clientHeight * r);
      dirty = true;
    }

    function draw(im) {
      var cw = canvas.width, ch = canvas.height;
      var s = Math.max(cw / im.naturalWidth, ch / im.naturalHeight);   // cover fit
      var w = im.naturalWidth * s, h = im.naturalHeight * s;
      ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
    }

    function section(n) {
      for (var i = 0; i < man.sections.length; i++) {
        var s = man.sections[i];
        if (n >= s.start && n <= s.end) return i;
      }
      return -1;
    }

    var current = -2;
    function caption_for(n) {
      var i = section(n);
      if (i === current) return;
      current = i;
      caption.classList.remove("on");
      if (i < 0) return;
      caption.querySelector("h2").textContent = man.sections[i].heading;
      caption.querySelector("p").textContent = man.sections[i].body;
      var more = caption.querySelector("a");
      if (more) { more.hidden = !man.sections[i].link; if (man.sections[i].link) more.href = man.sections[i].link; }
      if (man.sections[i].heading || man.sections[i].body) {
        requestAnimationFrame(function () { caption.classList.add("on"); });
      }
    }

    function onScroll() {
      var rect = track.getBoundingClientRect();
      var span = track.offsetHeight - window.innerHeight;
      var p = span > 0 ? Math.min(1, Math.max(0, -rect.top / span)) : 0;
      target = p * (man.frames - 1);
    }

    // Autoplay: the page scrolls itself at one frame per video frame until the visitor scrolls, taps or presses a key.
    var playBtn = document.getElementById("play");
    var auto = !reduce, last = 0, carry = 0;
    function setAuto(on) { auto = on; last = 0; if (playBtn) playBtn.textContent = on ? "Pause" : "Play"; }
    function userTook() { if (auto) setAuto(false); }
    ["wheel", "touchstart", "keydown"].forEach(function (ev) { window.addEventListener(ev, userTook, { passive: true }); });
    if (playBtn) {
      playBtn.hidden = false;
      playBtn.addEventListener("click", function (ev) {
        ev.stopPropagation();
        if (!auto && window.scrollY >= document.documentElement.scrollHeight - window.innerHeight - 2) window.scrollTo(0, 0);
        setAuto(!auto);
      });
    }
    function autoStep(now) {
      if (!auto) return;
      if (last) {
        carry += Math.min(100, now - last) / 1000 * (man.fps || 24) * PX_PER_FRAME;
        var px = Math.floor(carry);
        if (px > 0) { carry -= px; window.scrollBy(0, px); }
        if (window.scrollY >= document.documentElement.scrollHeight - window.innerHeight - 1) setAuto(false);
      }
      last = now;
    }

    function tick(now) {
      autoStep(now);
      shown += (target - shown) * (reduce ? 1 : EASE);
      if (Math.abs(target - shown) < 0.01) shown = target;
      var n = Math.round(shown);
      if (n !== drawn || dirty) {
        preload(n);
        var im = nearestLoaded(n);
        if (im) { draw(im); drawn = n; dirty = false; }
        caption_for(n);
      }
      requestAnimationFrame(tick);
    }

    document.title = man.title;
    track.style.height = (man.frames * PX_PER_FRAME + window.innerHeight) + "px";
    root.hidden = false;
    window.addEventListener("resize", function () { resize(); onScroll(); });
    window.addEventListener("scroll", onScroll, { passive: true });
    resize();
    onScroll();
    preload(0);
    setAuto(auto);
    requestAnimationFrame(tick);
  }

  fetch("manifest.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error("manifest " + r.status); return r.json(); })
    .then(start)
    .catch(function (e) {
      var msg = document.getElementById("error");
      msg.textContent = "Could not load the page frames (" + e.message + "). Serve this folder over http.";
      msg.hidden = false;
    });
})();
