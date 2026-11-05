// Site settings behind the gear button (top right): sound + volume, theme, language.
// Choices stay in localStorage. Sound is synthesized with Web Audio (no files) and starts on the
// first click or key press, because browsers block audio before a user gesture.
(function () {
  var root = document.documentElement;
  var me = document.currentScript;
  var base = me ? me.src : location.href;

  function load(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var THEMES = [
    { id: 'clean', name: 'Clean', sw: ['#f5f5f7', '#0071e3'] },
    { id: 'material', name: 'Material', sw: ['#eef1fb', '#3d5afe'] },
    { id: 'hud', name: 'HUD', sw: ['#04101c', '#45d6ff'] },
    { id: 'soft', name: 'Soft', sw: ['#f3ecdf', '#8a6a3b'] },
    { id: 'night', name: 'Night', sw: ['#000000', '#ffd60a'] },
    { id: 'terminal', name: 'Terminal', sw: ['#000000', '#33ff66'] },
    { id: 'arcade', name: 'Arcade', sw: ['#16002e', '#ff3df0'] }
  ];
  // Ethnologue 2026 top five by total speakers, then French, Portuguese and German.
  var LANGS = [
    { id: 'en', tag: 'en', name: 'English', flag: 'us' },
    { id: 'zh', tag: 'zh-Hans', name: '中文', flag: 'cn' },
    { id: 'hi', tag: 'hi', name: 'हिन्दी', flag: 'in' },
    { id: 'es', tag: 'es', name: 'Español', flag: 'es' },
    { id: 'ar', tag: 'ar', name: 'العربية', flag: 'sa', rtl: true },
    { id: 'fr', tag: 'fr', name: 'Français', flag: 'fr' },
    { id: 'pt', tag: 'pt-BR', name: 'Português', flag: 'br' },
    { id: 'de', tag: 'de', name: 'Deutsch', flag: 'de' }
  ];

  // ---------- Flags: simple original drawings, 30x20 ----------
  function star(cx, cy, r, rot) {
    var p = [];
    for (var i = 0; i < 10; i++) {
      var a = (rot || 0) + Math.PI / 2 * -1 + i * Math.PI / 5, rr = i % 2 ? r * 0.4 : r;
      p.push((cx + rr * Math.cos(a)).toFixed(2) + ',' + (cy + rr * Math.sin(a)).toFixed(2));
    }
    return '<polygon fill="#ffde00" points="' + p.join(' ') + '"/>';
  }
  var FLAGS = {
    us: (function () {
      var s = '<rect width="30" height="20" fill="#fff"/>';
      for (var i = 0; i < 7; i++) s += '<rect y="' + (i * 20 / 6.5).toFixed(2) + '" width="30" height="1.54" fill="#b22234"/>';
      return s + '<rect width="13" height="10.8" fill="#3c3b6e"/>';
    })(),
    cn: '<rect width="30" height="20" fill="#de2910"/>' + star(5, 5, 3) + star(10, 2, 1, .3) + star(12, 4, 1, .8) + star(12, 7, 1, 0) + star(10, 9, 1, .4),
    in: '<rect width="30" height="20" fill="#fff"/><rect width="30" height="6.67" fill="#ff9933"/><rect y="13.33" width="30" height="6.67" fill="#138808"/><circle cx="15" cy="10" r="2.6" fill="none" stroke="#000080" stroke-width=".8"/>',
    es: '<rect width="30" height="20" fill="#c60b1e"/><rect y="5" width="30" height="10" fill="#ffc400"/>',
    sa: '<rect width="30" height="20" fill="#006c35"/><path d="M7 8.2h16M8 12.6h13l1.6-1" stroke="#fff" stroke-width="1.1" fill="none" stroke-linecap="round"/>',
    fr: '<rect width="30" height="20" fill="#fff"/><rect width="10" height="20" fill="#002395"/><rect x="20" width="10" height="20" fill="#ed2939"/>',
    br: '<rect width="30" height="20" fill="#009c3b"/><path d="M15 2.5 27 10 15 17.5 3 10z" fill="#ffdf00"/><circle cx="15" cy="10" r="4.2" fill="#002776"/>',
    de: '<rect width="30" height="20" fill="#ffce00"/><rect width="30" height="6.67" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#dd0000"/>'
  };
  function flag(id) {
    return '<svg class="flag" viewBox="0 0 30 20" width="21" height="14" aria-hidden="true" focusable="false">' + FLAGS[id] + '</svg>';
  }

  // ---------- Translation ----------
  var LETTER = /\p{L}/u, PLACE = /\{(\d+)\}/g;
  var ATTRS = ['aria-label', 'alt', 'title', 'placeholder'];
  var SKIP = { SCRIPT: 1, STYLE: 1, SVG: 1, NOSCRIPT: 1, TEMPLATE: 1, SOURCE: 1, svg: 1 };
  var units = null, attrs = null, origTitle = document.title, dict = {}, lang = 'en';
  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  function hasLetter(k) { return LETTER.test(k.replace(PLACE, '')); }

  // Same cut as tools/i18n.py: own text is the key, child elements and fact numbers become {n}.
  function unit(el) {
    var parts = [], groups = [], own = '', inFact = false, nodes = Array.prototype.slice.call(el.childNodes);
    nodes.forEach(function (k) {
      if (k.nodeType === 1) { parts.push('{' + groups.length + '}'); groups.push([k]); }
      else if (k.nodeType === 8) {
        if (k.data.indexOf('fact:') === 0) { inFact = true; parts.push('{' + groups.length + '}'); groups.push([k]); }
        else if (k.data.indexOf('/fact') === 0) { inFact = false; groups[groups.length - 1].push(k); }
      } else if (k.nodeType === 3) {
        if (inFact) groups[groups.length - 1].push(k);
        else { parts.push(k.data); own += k.data; }
      }
    });
    if (!LETTER.test(own)) return null;
    return { el: el, key: norm(parts.join('')), orig: nodes, groups: groups };
  }
  function collect() {
    units = []; attrs = [];
    (function walk(el) {
      if (SKIP[el.tagName] || el.getAttribute('translate') === 'no') {
        if (el.getAttribute('translate') !== 'no') addAttrs(el);
        return;
      }
      addAttrs(el);
      var u = unit(el);
      if (u) units.push(u);
      for (var c = el.firstElementChild; c; c = c.nextElementSibling) walk(c);
    })(document.body);
  }
  function addAttrs(el) {
    if (el.classList.contains('vbtn')) return; // app.js labels these itself
    ATTRS.forEach(function (a) {
      var v = el.getAttribute(a);
      if (v && hasLetter(norm(v))) attrs.push({ el: el, a: a, key: norm(v), orig: v });
    });
  }
  function t(s) { return (lang !== 'en' && dict[s]) || s; }
  window.mmT = t;

  function render() {
    if (!units) collect();
    units.forEach(function (u) {
      var tr = lang !== 'en' && dict[u.key];
      if (!tr) { u.el.replaceChildren.apply(u.el, u.orig); return; }
      var out = [], last = 0, m;
      PLACE.lastIndex = 0;
      while ((m = PLACE.exec(tr))) {
        if (m.index > last) out.push(document.createTextNode(tr.slice(last, m.index)));
        (u.groups[+m[1]] || []).forEach(function (n) { out.push(n); });
        last = m.index + m[0].length;
      }
      if (last < tr.length) out.push(document.createTextNode(tr.slice(last)));
      u.el.replaceChildren.apply(u.el, out);
    });
    attrs.forEach(function (x) { x.el.setAttribute(x.a, (lang !== 'en' && dict[x.key]) || x.orig); });
    document.title = t(norm(origTitle));
    document.querySelectorAll('[data-t]').forEach(function (el) {
      if (el.dataset.tText) el.textContent = t(el.dataset.t);
      else el.setAttribute('aria-label', t(el.dataset.t));
    });
    document.dispatchEvent(new CustomEvent('mm:lang', { detail: lang }));
  }
  function setLang(id, fromUser) {
    var L = LANGS.filter(function (x) { return x.id === id; })[0] || LANGS[0];
    function apply(d) {
      dict = d || {}; lang = d || L.id === 'en' ? L.id : 'en';
      var cur = lang === L.id ? L : LANGS[0];
      root.lang = cur.tag; root.dir = cur.rtl ? 'rtl' : 'ltr';
      render();
      root.classList.remove('i18n-wait');
      sync();
    }
    if (fromUser) save('mm-lang', L.id);
    if (L.id === 'en') return apply(null);
    fetch(new URL('i18n/' + L.id + '.json', base)).then(function (r) { return r.ok ? r.json() : null; })
      .then(apply, function () { apply(null); });
  }

  // ---------- Theme ----------
  function setTheme(id, fromUser) {
    if (!THEMES.some(function (x) { return x.id === id; })) id = 'clean';
    if (id === 'clean') root.removeAttribute('data-theme'); else root.dataset.theme = id;
    if (fromUser) save('mm-theme', id);
    sync();
    sound.theme(id);
  }

  // ---------- Sound ----------
  var PROFILES = {
    clean: { pad: 'sine', notes: [220, 277.18, 329.63], cut: 900, blip: ['sine', 880, 1320, .06] },
    material: { pad: 'triangle', notes: [261.63, 329.63, 392], cut: 1100, blip: ['triangle', 660, 990, .05] },
    hud: { pad: 'sawtooth', notes: [55, 110, 164.81], cut: 380, lfo: .08, blip: ['square', 1400, 900, .05] },
    soft: { pad: 'sine', notes: [196, 246.94, 293.66], cut: 600, blip: ['sine', 523.25, 659.25, .08] },
    night: { pad: 'sine', notes: [146.83, 220], cut: 500, blip: ['sine', 440, 440, .07] },
    terminal: { pad: 'square', notes: [60], cut: 160, blip: ['square', 1800, 1800, .015] },
    arcade: { arp: [523.25, 659.25, 783.99, 1046.5, 783.99, 659.25], blip: ['square', 440, 1320, .08] }
  };
  var sound = (function () {
    var ctx, master, pad, arpTimer, on = load('mm-sound', 'on') !== 'off', vol = +load('mm-volume', '25');
    var profile = PROFILES.clean;
    if (!(vol >= 0 && vol <= 100)) vol = 25;
    function level() { return on ? Math.pow(vol / 100, 2) * 0.8 : 0; }
    function start() {
      if (!on) return;
      if (!ctx) {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        ctx = new AC();
        master = ctx.createGain();
        master.gain.value = level();
        master.connect(ctx.destination);
        startPad();
      }
      if (ctx.state === 'suspended' && !document.hidden) ctx.resume();
    }
    function stopPad() {
      clearInterval(arpTimer); arpTimer = null;
      if (!pad) return;
      var p = pad, now = ctx.currentTime;
      p.gain.gain.cancelScheduledValues(now);
      p.gain.gain.setValueAtTime(p.gain.gain.value, now);
      p.gain.gain.linearRampToValueAtTime(0, now + .8);
      setTimeout(function () { p.osc.forEach(function (o) { o.stop(); }); p.gain.disconnect(); }, 900);
      pad = null;
    }
    function startPad() {
      if (!ctx) return;
      stopPad();
      if (profile.arp) {
        var i = 0;
        arpTimer = setInterval(function () {
          if (ctx.state !== 'running') return;
          note('square', profile.arp[i++ % profile.arp.length], null, .12, .05);
        }, 220);
        return;
      }
      var g = ctx.createGain(), f = ctx.createBiquadFilter(), now = ctx.currentTime, osc = [];
      f.type = 'lowpass'; f.frequency.value = profile.cut;
      g.gain.setValueAtTime(0, now);
      g.gain.linearRampToValueAtTime(.16 / profile.notes.length, now + 2.5);
      f.connect(g); g.connect(master);
      profile.notes.forEach(function (fr) {
        [-6, 6].forEach(function (d) {
          var o = ctx.createOscillator();
          o.type = profile.pad; o.frequency.value = fr; o.detune.value = d;
          o.connect(f); o.start(); osc.push(o);
        });
      });
      if (profile.lfo) {
        var l = ctx.createOscillator(), lg = ctx.createGain();
        l.frequency.value = profile.lfo; lg.gain.value = profile.cut * .5;
        l.connect(lg); lg.connect(f.frequency); l.start(); osc.push(l);
      }
      pad = { gain: g, osc: osc };
    }
    function note(type, f1, f2, len, peak) {
      if (!ctx || ctx.state !== 'running') return;
      var o = ctx.createOscillator(), g = ctx.createGain(), now = ctx.currentTime;
      o.type = type; o.frequency.setValueAtTime(f1, now);
      if (f2 && f2 !== f1) o.frequency.exponentialRampToValueAtTime(f2, now + len);
      g.gain.setValueAtTime(0, now);
      g.gain.linearRampToValueAtTime(peak, now + .005);
      g.gain.exponentialRampToValueAtTime(.0001, now + len + .04);
      o.connect(g); g.connect(master); o.start(now); o.stop(now + len + .06);
    }
    document.addEventListener('visibilitychange', function () {
      if (!ctx) return;
      if (document.hidden) ctx.suspend(); else if (on) ctx.resume();
    });
    return {
      get on() { return on; }, get vol() { return vol; },
      start: start,
      blip: function () { var b = profile.blip; note(b[0], b[1], b[2], b[3], .35); },
      theme: function (id) { profile = PROFILES[id] || PROFILES.clean; startPad(); },
      set: function (o, v) {
        on = o; vol = v;
        save('mm-sound', on ? 'on' : 'off'); save('mm-volume', String(vol));
        if (on) start();
        if (ctx) {
          master.gain.setTargetAtTime(level(), ctx.currentTime, .05);
          if (!on) setTimeout(function () { if (!on) ctx.suspend(); }, 200);
        }
      }
    };
  })();

  // ---------- Settings panel: ☰ button at the top right of the nav ----------
  var panel, btn;
  function radios(name, items, label) {
    return '<fieldset class="set-group"><legend data-t="' + label + '" data-t-text="1">' + t(label) + '</legend><div class="set-' + name + '">' +
      items.map(function (it) {
        return '<label class="set-opt"><input type="radio" name="mm-' + name + '" value="' + it.id + '">' + (name === 'theme'
            ? '<span class="sw" aria-hidden="true" style="--a:' + it.sw[0] + ';--b:' + it.sw[1] + '"></span><span data-t="' + it.name + '" data-t-text="1">' + t(it.name) + '</span>'
            : flag(it.flag) + '<span lang="' + it.tag + '">' + it.name + '</span>') + '</label>';
      }).join('') + '</div></fieldset>';
  }
  function sync() {
    if (!panel) return;
    var th = root.dataset.theme || 'clean', lg = LANGS.filter(function (x) { return x.tag === root.lang; })[0];
    panel.querySelectorAll('input[name="mm-theme"]').forEach(function (r) { r.checked = r.value === th; });
    panel.querySelectorAll('input[name="mm-lang"]').forEach(function (r) { r.checked = r.value === (lg ? lg.id : 'en'); });
    var sb = panel.querySelector('.set-sound button'), sv = panel.querySelector('.set-sound input');
    sb.setAttribute('aria-pressed', String(sound.on));
    sv.value = sound.vol; sv.disabled = !sound.on;
    sv.setAttribute('aria-valuetext', sound.vol + '%');
    panel.querySelector('.set-vol').textContent = sound.vol + '%';
  }

  btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'set-btn';
  btn.dataset.t = 'Settings';
  btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'mm-settings');
  btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor">' +
    '<circle cx="12" cy="12" r="8.6" stroke-width="2.6" stroke-dasharray="3.38 3.38"/><circle cx="12" cy="12" r="6.6" stroke-width="1.3"/><circle cx="12" cy="12" r="2.6" stroke-width="1.3"/></svg>';

  panel = document.createElement('div');
  panel.id = 'mm-settings'; panel.className = 'set-panel';
  panel.setAttribute('role', 'dialog'); panel.dataset.t = 'Settings';
  panel.setAttribute('translate', 'no'); btn.setAttribute('translate', 'no');
  panel.hidden = true;
  panel.innerHTML =
    '<fieldset class="set-group"><legend data-t="Sound" data-t-text="1">' + t('Sound') + '</legend><div class="set-sound">' +
    '<button type="button" class="set-icon" data-t="Sound" aria-pressed="false">' +
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/>' +
    '<path class="w" d="M16 9.5a3.5 3.5 0 0 1 0 5M18.5 7a7 7 0 0 1 0 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>' +
    '<path class="x" d="M16.5 9.5l5 5m0-5l-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>' +
    '<input type="range" min="0" max="100" step="5" data-t="Volume"><span class="set-vol" aria-hidden="true"></span></div></fieldset>' +
    radios('theme', THEMES, 'Theme') + radios('lang', LANGS, 'Language');

  var navIn = document.querySelector('.nav-in');
  (navIn || document.body).appendChild(btn);
  (navIn || document.body).appendChild(panel);

  function open() {
    panel.hidden = false; btn.setAttribute('aria-expanded', 'true');
    panel.querySelector('.set-sound button').focus();
  }
  function close(focus) {
    if (panel.hidden) return;
    panel.hidden = true; btn.setAttribute('aria-expanded', 'false');
    if (focus) btn.focus();
  }
  btn.addEventListener('click', function () { panel.hidden ? open() : close(); });
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); close(true); } });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) close(true); });
  document.addEventListener('pointerdown', function (e) { if (!panel.hidden && !panel.contains(e.target) && !btn.contains(e.target)) close(); });
  panel.addEventListener('focusout', function (e) { if (e.relatedTarget && !panel.contains(e.relatedTarget) && e.relatedTarget !== btn) close(); });

  panel.addEventListener('change', function (e) {
    var r = e.target;
    if (r.name === 'mm-theme') setTheme(r.value, true);
    else if (r.name === 'mm-lang') setLang(r.value, true);
    sound.blip();
  });
  var sBtn = panel.querySelector('.set-sound button'), sVol = panel.querySelector('.set-sound input');
  sBtn.addEventListener('click', function () { sound.set(!sound.on, sound.vol); sync(); sound.blip(); });
  sVol.addEventListener('input', function () { sound.set(true, +sVol.value); sync(); });
  sVol.addEventListener('change', function () { sound.blip(); });

  // Sound on the first gesture, and a blip for clicks on links and buttons.
  function gesture() { sound.start(); }
  document.addEventListener('pointerdown', gesture, true);
  document.addEventListener('keydown', gesture, true);
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a, button');
    if (a && !panel.contains(a)) sound.blip();
  }, true);

  setTheme(load('mm-theme', 'clean'), false);
  setLang(load('mm-lang', 'en'), false);
  if (load('mm-lang', 'en') === 'en') render();
  sync();
})();
