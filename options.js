// Site settings behind the gear button (top right): sound + volume, theme, language.
// Choices stay in localStorage. Sound is synthesized with Web Audio (no files) and starts on the
// first click or key press, because browsers block audio before a user gesture.
(function () {
  var root = document.documentElement;
  var me = document.currentScript;
  var base = me ? me.src : location.href;

  function load(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Theme ids stay short (they are saved in localStorage); names say what each one looks like.
  var THEMES = [
    { id: 'clean', name: 'Minimal', sw: ['#f5f5f7', '#0071e3'] },
    { id: 'vision', name: 'VISION AI', sw: ['#07040f', '#8b5cf6'] },
    { id: 'material', name: 'Material', sw: ['#eef1fb', '#3d5afe'] },
    { id: 'fluent', name: 'Fluent', sw: ['#f3f6fa', '#0f6cbd'] },
    { id: 'hud', name: 'Sci-Fi HUD', sw: ['#04101c', '#45d6ff'] },
    { id: 'soft', name: 'Warm Paper', sw: ['#f3ecdf', '#8a6a3b'] },
    { id: 'night', name: 'High Contrast', sw: ['#000000', '#ffd60a'] },
    { id: 'terminal', name: 'Hacker Terminal', sw: ['#000000', '#33ff66'] },
    { id: 'arcade', name: 'Retro Arcade', sw: ['#16002e', '#ff3df0'] },
    { id: 'holo', name: 'Gold Hologram', sw: ['#020812', '#f2b84b'] },
    { id: 'grid', name: 'Neon Grid', sw: ['#000000', '#6ff3ff'] }
  ];
  // Ethnologue 2026 top five by total speakers, then French, Portuguese, German, Italian and Japanese.
  var LANGS = [
    { id: 'en', tag: 'en', name: 'English', flag: 'us' },
    { id: 'zh', tag: 'zh-Hans', name: '中文', flag: 'cn' },
    { id: 'hi', tag: 'hi', name: 'हिन्दी', flag: 'in' },
    { id: 'es', tag: 'es', name: 'Español', flag: 'es' },
    { id: 'ar', tag: 'ar', name: 'العربية', flag: 'sa', rtl: true },
    { id: 'fr', tag: 'fr', name: 'Français', flag: 'fr' },
    { id: 'pt', tag: 'pt-BR', name: 'Português', flag: 'br' },
    { id: 'de', tag: 'de', name: 'Deutsch', flag: 'de' },
    { id: 'it', tag: 'it', name: 'Italiano', flag: 'it' },
    { id: 'ja', tag: 'ja', name: '日本語', flag: 'jp' },
    { id: 'he', tag: 'he', name: 'עברית', flag: 'il', rtl: true, en: 'Hebrew' },
    // Fan Neo-Sindarin (ISO 639-3 sjn), built from public dictionaries; approximate by nature.
    { id: 'sjn', tag: 'sjn', name: 'Edhellen (Elvish)', flag: 'elf' }
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
    de: '<rect width="30" height="20" fill="#ffce00"/><rect width="30" height="6.67" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#dd0000"/>',
    it: '<rect width="30" height="20" fill="#fff"/><rect width="10" height="20" fill="#009246"/><rect x="20" width="10" height="20" fill="#ce2b37"/>',
    jp: '<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="6" fill="#bc002d"/>',
    il: '<rect width="30" height="20" fill="#fff"/><rect y="2" width="30" height="2.4" fill="#0038b8"/><rect y="15.6" width="30" height="2.4" fill="#0038b8"/>' +
      '<path d="M15 5.6l3.8 6.6h-7.6zM15 14.4l-3.8-6.6h7.6z" fill="none" stroke="#0038b8" stroke-width=".9"/>',
    elf:'<rect width="30" height="20" fill="#1d3b2a"/><path d="M8 15C10 6 18 4 23 4c0 6-4 13-14 11z" fill="#c9e4b4"/><path d="M8 15 19 7" stroke="#1d3b2a" stroke-width=".9"/>'
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
      if (el.tagName === 'INPUT') el.placeholder = t(el.dataset.t);
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
  // Generative background music, written from what music-emotion research agrees on:
  // - major mode reads as happy and hopeful, minor as sad (Hevner 1935; Gagnon & Peretz 2003);
  // - consonant intervals feel pleasant (Bidelman & Krishnan 2009): the melody stays on the major
  //   pentatonic scale, which has no semitone clashes;
  // - soft attacks, low-passed timbres and a reverb; a melody that rises at each phrase start
  //   gives the "lift" of optimism.
  // Every theme has its own original song style: tempo, chords, arpeggio, drums and timbre.
  // The default (Minimal) is an uplifting folk-pop anthem: a mid-tempo stomp-and-clap pulse,
  // plucked arpeggios and a rising melody over I-V-vi-IV. All patterns are written here, none copied.
  // `root`: key in semitones from C4; `cut`: brightness in Hz; patterns are 8 eighth notes per bar
  // (arp: chord-tone index or -1 for a rest; kick/clap/hat: 1 = hit); `bars`: bars per chord.
  var I = [0, 4, 7], V = [-5, -1, 2], VI = [-3, 0, 4], IV = [-7, -3, 0], II7 = [2, 5, 9, 12],
    V7 = [-5, -1, 2, 5], I7 = [0, 4, 7, 11], VI7 = [-3, 0, 4, 7], III = [-8, -5, -1];
  var POP = [I, V, VI, IV], EPIC = [VI, IV, I, V];
  var PROFILES = {
    clean: { style: 'Uplifting folk-pop', root: 0, bpm: 84, prog: POP, padWave: 'sine', pad: .035, arpWave: 'triangle', arp: [0, 1, 2, 3, 4, 3, 2, 1], arpOct: 0,
      kick: [1, 0, 0, 0, 1, 0, 1, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [0, 1, 0, 1, 0, 1, 0, 1], bass: [1, 0, 0, 1, 1, 0, 0, 0], wave: 'triangle', mel: .7, cut: 2600, blip: ['sine', 659.25, 783.99, .12] },
    vision: { style: 'Future pulse', root: 2, bpm: 96, prog: EPIC, padWave: 'sawtooth', pad: .02, arpWave: 'sawtooth', arp: [0, 1, 2, 3, 4, 3, 2, 1], arpOct: 12,
      kick: [1, 0, 0, 0, 1, 0, 0, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [0, 1, 0, 1, 0, 1, 0, 1], bass: [1, 1, 1, 1, 1, 1, 1, 1], wave: 'sine', mel: .5, cut: 1900, blip: ['sine', 880, 1318.5, .1] },
    material: { style: 'Bright pop', root: 2, bpm: 104, prog: [I, VI, IV, V], padWave: 'triangle', pad: .03, arpWave: 'square', arp: [0, -1, 2, -1, 1, -1, 2, 3], arpOct: 0,
      kick: [1, 0, 1, 0, 1, 0, 1, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [0, 1, 0, 1, 0, 1, 0, 1], bass: [1, 0, 1, 0, 1, 0, 1, 0], wave: 'triangle', mel: .6, cut: 2400, blip: ['sine', 587.33, 698.46, .12] },
    fluent: { style: 'Airy chill', root: 5, bpm: 72, prog: [I7, IV, VI7, V], padWave: 'sine', pad: .05, arpWave: 'sine', arp: [0, -1, 2, -1, 3, -1, 1, -1], arpOct: 12,
      kick: [1, 0, 0, 0, 0, 0, 0, 0], clap: [0, 0, 0, 0, 0, 0, 0, 0], hat: [0, 0, 1, 0, 0, 0, 1, 1], bass: [1, 0, 0, 0, 0, 0, 0, 0], wave: 'sine', mel: .45, cut: 2200, blip: ['sine', 698.46, 880, .12] },
    hud: { style: 'Sci-fi drive', root: 7, bpm: 100, prog: [VI, III, IV, V], padWave: 'sawtooth', pad: .018, arpWave: 'square', arp: [0, 2, 1, 2, 0, 2, 1, 2], arpOct: 12,
      kick: [1, 0, 0, 0, 1, 0, 0, 0], clap: [0, 0, 0, 0, 0, 0, 0, 0], hat: [1, 1, 1, 1, 1, 1, 1, 1], bass: [1, 1, 1, 1, 1, 1, 1, 1], wave: 'sine', mel: .35, cut: 1700, blip: ['sine', 880, 987.77, .1] },
    soft: { style: 'Lo-fi', root: 5, bpm: 70, prog: [II7, V7, I7, VI7], padWave: 'triangle', pad: .03, arpWave: 'triangle', arp: [0, -1, -1, 2, -1, 1, -1, -1], arpOct: 0,
      kick: [1, 0, 0, 0, 0, 1, 0, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [1, 0, 1, 0, 1, 0, 1, 1], bass: [1, 0, 0, 0, 0, 1, 0, 0], wave: 'sine', mel: .5, cut: 1300, blip: ['sine', 523.25, 659.25, .14] },
    night: { style: 'Ambient', root: -3, bpm: 60, bars: 2, prog: [I, IV, VI, IV], padWave: 'sine', pad: .055, arpWave: 'sine', arp: [-1, -1, -1, -1, 2, -1, -1, -1], arpOct: 12,
      kick: [0, 0, 0, 0, 0, 0, 0, 0], clap: [0, 0, 0, 0, 0, 0, 0, 0], hat: [0, 0, 0, 0, 0, 0, 0, 0], bass: [1, 0, 0, 0, 0, 0, 0, 0], wave: 'sine', mel: .3, cut: 1400, blip: ['sine', 440, 493.88, .14] },
    terminal: { style: 'Minimal 8-bit', root: -2, bpm: 112, prog: [VI, IV, I, V], padWave: 'square', pad: .006, arpWave: 'square', arp: [0, 1, 2, 1, 0, 1, 2, 1], arpOct: 0,
      kick: [1, 0, 0, 0, 1, 0, 0, 0], clap: [0, 0, 0, 0, 0, 0, 0, 0], hat: [0, 0, 1, 0, 0, 0, 1, 0], bass: [1, 0, 0, 0, 1, 0, 0, 0], wave: 'square', mel: .25, cut: 1600, blip: ['square', 1046.5, 1046.5, .05] },
    arcade: { style: 'Chiptune', root: 4, bpm: 136, prog: POP, padWave: 'square', pad: .01, arpWave: 'square', arp: [0, 1, 2, 3, 2, 1, 0, 1], arpOct: 12,
      kick: [1, 0, 1, 0, 1, 0, 1, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [0, 1, 0, 1, 0, 1, 0, 1], bass: [1, 1, 0, 1, 1, 1, 0, 1], wave: 'square', mel: .7, cut: 3000, blip: ['triangle', 659.25, 987.77, .1] },
    holo: { style: 'Cinematic', root: 7, bpm: 66, bars: 2, prog: EPIC, padWave: 'sawtooth', pad: .022, arpWave: 'sine', arp: [0, 1, 2, 3, 4, 3, 2, 1], arpOct: 0,
      kick: [1, 0, 0, 0, 0, 0, 0, 0], clap: [0, 0, 0, 0, 0, 0, 0, 0], hat: [0, 0, 0, 0, 0, 0, 0, 0], bass: [1, 0, 0, 0, 0, 0, 0, 0], wave: 'sine', mel: .5, cut: 1800, blip: ['sine', 783.99, 1046.5, .1] },
    grid: { style: 'Synthwave', root: 9, bpm: 100, prog: EPIC, padWave: 'sawtooth', pad: .02, arpWave: 'sawtooth', arp: [0, 1, 2, 1, 3, 1, 2, 1], arpOct: 12,
      kick: [1, 0, 0, 0, 1, 0, 0, 0], clap: [0, 0, 1, 0, 0, 0, 1, 0], hat: [0, 1, 0, 1, 0, 1, 0, 1], bass: [1, 1, 1, 1, 1, 1, 1, 1], wave: 'triangle', mel: .45, cut: 2000, blip: ['square', 880, 880, .04] }
  };
  // Music styles the visitor can pick; 'auto' plays the theme's own song, 'clicks' keeps only the blips.
  var MUSIC = [{ id: 'auto', name: 'Auto' }, { id: 'calm', name: 'Calm' }, { id: 'bright', name: 'Bright' },
    { id: 'deep', name: 'Deep' }, { id: 'clicks', name: 'Clicks' }];
  var MUSIC_PROFILE = { calm: 'fluent', bright: 'material', deep: 'night' };
  var STEPS = 8;                                                       // eighth notes per bar
  var PENTA = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21];                     // major pentatonic, 2 octaves
  var sound = (function () {
    // 'mm-vol' replaces the old 'mm-volume' key so every visitor starts again at 15%.
    var ctx, master, pad, on = load('mm-sound', 'on') !== 'off', vol = +load('mm-vol', '15');
    var profile = PROFILES.clean, themeId = 'clean', music = load('mm-music', 'auto');
    if (!MUSIC.some(function (m) { return m.id === music; })) music = 'auto';
    if (!(vol >= 0 && vol <= 100)) vol = 15;
    function pick() { profile = PROFILES[MUSIC_PROFILE[music] || themeId] || PROFILES.clean; }
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
    function hz(semi) { return 261.63 * Math.pow(2, semi / 12); }
    // A soft hall: 3 s of decaying stereo noise as the reverb impulse.
    function hall() {
      var n = ctx.sampleRate * 3, buf = ctx.createBuffer(2, n, ctx.sampleRate);
      for (var c = 0; c < 2; c++) {
        var d = buf.getChannelData(c);
        for (var i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3);
      }
      var conv = ctx.createConvolver(); conv.buffer = buf; return conv;
    }
    // One voice: oscillator -> low-pass -> envelope -> dry bus and reverb.
    function voice(wave, freq, at, attack, hold, release, peak) {
      var o = ctx.createOscillator(), f = ctx.createBiquadFilter(), g = ctx.createGain();
      o.type = wave; o.frequency.value = freq;
      f.type = 'lowpass'; f.frequency.value = profile.cut; f.Q.value = .3;
      g.gain.setValueAtTime(0, at);
      g.gain.linearRampToValueAtTime(peak, at + attack);
      g.gain.setValueAtTime(peak, at + attack + hold);
      g.gain.exponentialRampToValueAtTime(.0001, at + attack + hold + release);
      o.connect(f); f.connect(g); g.connect(pad.bus);
      o.start(at); o.stop(at + attack + hold + release + .1);
    }
    function step() { return 60 / profile.bpm / 2; }
    function tone(chord, k) { return chord[k % chord.length] + 12 * Math.floor(k / chord.length); }
    function playChord(at, chord, len) {
      var a = Math.min(1.5, len / 4);
      for (var i = 0; i < chord.length; i++)
        voice(profile.padWave, hz(profile.root + chord[i] - 12), at, a, len - a, 1.8, profile.pad);
    }
    // Drums from shaped noise and a pitch-dropping sine; they go to the dry bus, not the reverb.
    function noiseHit(at, type, freq, len, peak) {
      var n = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
      n.buffer = pad.noise; f.type = type; f.frequency.value = freq;
      g.gain.setValueAtTime(peak, at); g.gain.exponentialRampToValueAtTime(.0001, at + len);
      n.connect(f); f.connect(g); g.connect(pad.dry); n.start(at, Math.random() * .5); n.stop(at + len + .05);
    }
    function kick(at) {
      var o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.setValueAtTime(130, at); o.frequency.exponentialRampToValueAtTime(42, at + .14);
      g.gain.setValueAtTime(.16, at); g.gain.exponentialRampToValueAtTime(.0001, at + .32);
      o.connect(g); g.connect(pad.dry); o.start(at); o.stop(at + .35);
    }
    // Melody: a gentle random walk on the pentatonic scale, rising at each phrase start
    // and landing on a chord tone when the chord changes.
    function playMelody(at, beat, chord) {
      if (beat === 0) {
        pad.step = 0;
        for (var i = chord.length - 1; i >= 0; i--) {
          var at12 = PENTA.indexOf(((chord[i] % 12) + 12) % 12);
          if (at12 >= 0) pad.step = at12;
        }
      } else {
        if (Math.random() > profile.mel) return;
        var move = [-1, 1, 1, 2, -2][Math.floor(Math.random() * 5)];
        if (beat < 4 && move < 0) move = -move;
        pad.step = Math.max(0, Math.min(PENTA.length - 1, pad.step + move));
      }
      voice(profile.wave, hz(profile.root + 12 + PENTA[pad.step]), at, .02, step() * 1.5, 1.2, .03);
    }
    // Look-ahead scheduler: every 250 ms, book the eighth notes due in the next second.
    function tick() {
      if (!pad || ctx.state !== 'running') return;
      while (pad.next < ctx.currentTime + 1) {
        var p = profile, bars = p.bars || 1, s8 = pad.beat % STEPS, at = pad.next;
        var bar = Math.floor(pad.beat / STEPS), chord = p.prog[Math.floor(bar / bars) % p.prog.length];
        if (music !== 'clicks') {
          if (s8 === 0 && bar % bars === 0) playChord(at, chord, STEPS * bars * step());
          var k = p.arp[s8];
          if (k >= 0) voice(p.arpWave, hz(p.root + p.arpOct + tone(chord, k)), at, .005, .03, .45, .022);
          if (p.bass[s8]) voice('triangle', hz(p.root + chord[0] - 24), at, .01, step() * .8, .25, .07);
          if (p.kick[s8]) kick(at);
          if (p.clap[s8]) noiseHit(at, 'bandpass', 1500, .18, .09);
          if (p.hat[s8]) noiseHit(at, 'highpass', 7500, .05, .025);
          if (s8 % 2 === 0) playMelody(at, s8, chord);
        }
        pad.beat++; pad.next += step();
      }
    }
    function startPad() {
      if (!ctx || pad) return;
      var bus = ctx.createGain(), dry = ctx.createGain(), rev = hall(), wet = ctx.createGain(), now = ctx.currentTime;
      var noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate), nd = noise.getChannelData(0);
      for (var i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
      [bus, dry].forEach(function (g) { g.gain.setValueAtTime(0, now); g.gain.linearRampToValueAtTime(1, now + 4); });
      wet.gain.value = .4;
      bus.connect(master); bus.connect(rev); rev.connect(wet); wet.connect(master); dry.connect(master);
      pad = { bus: bus, dry: dry, noise: noise, next: now + .2, beat: 0, step: 0 };
      setInterval(tick, 250);
      tick();
    }
    function note(type, f1, f2, len, peak) {
      if (!ctx || ctx.state !== 'running') return;
      var o = ctx.createOscillator(), g = ctx.createGain(), now = ctx.currentTime;
      o.type = type; o.frequency.setValueAtTime(f1, now);
      if (f2 && f2 !== f1) o.frequency.exponentialRampToValueAtTime(f2, now + len);
      g.gain.setValueAtTime(0, now);
      g.gain.linearRampToValueAtTime(peak, now + .02);
      g.gain.exponentialRampToValueAtTime(.0001, now + len + .25);
      o.connect(g); g.connect(master); o.start(now); o.stop(now + len + .3);
    }
    document.addEventListener('visibilitychange', function () {
      if (!ctx) return;
      if (document.hidden) ctx.suspend(); else if (on) ctx.resume();
    });
    return {
      get on() { return on; }, get vol() { return vol; }, get music() { return music; },
      start: start,
      blip: function () { var b = profile.blip; note(b[0], b[1], b[2], b[3], .12); },
      // A new theme or music style changes key and timbre from the next note on; the music never restarts.
      theme: function (id) { themeId = id; pick(); },
      setMusic: function (id) { music = id; save('mm-music', id); pick(); },
      set: function (o, v) {
        on = o; vol = v;
        save('mm-sound', on ? 'on' : 'off'); save('mm-vol', String(vol));
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
        var swatch = name === 'theme' ? '<span class="sw" aria-hidden="true" style="--a:' + it.sw[0] + ';--b:' + it.sw[1] + '"></span>' : '';
        return '<label class="set-opt"><input type="radio" name="mm-' + name + '" value="' + it.id + '">' + (name === 'lang'
            ? flag(it.flag) + '<span lang="' + it.tag + '">' + it.name + '</span>'
            : swatch + '<span data-t="' + it.name + '" data-t-text="1">' + t(it.name) + '</span>') + '</label>';
      }).join('') + '</div></fieldset>';
  }
  function sync() {
    if (!panel) return;
    var th = root.dataset.theme || 'clean', lg = LANGS.filter(function (x) { return x.tag === root.lang; })[0];
    panel.querySelectorAll('input[name="mm-theme"]').forEach(function (r) { r.checked = r.value === th; });
    panel.querySelectorAll('input[name="mm-lang"]').forEach(function (r) { r.checked = r.value === (lg ? lg.id : 'en'); });
    panel.querySelectorAll('input[name="mm-music"]').forEach(function (r) { r.checked = r.value === sound.music; r.disabled = !sound.on; });
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
  btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">' +
    '<path d="M4 6.5h16M4 12h16M4 17.5h16"/></svg>';

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
    radios('music', MUSIC, 'Music') + radios('theme', THEMES, 'Theme') + radios('lang', LANGS, 'Language').replace('<div class="set-lang">', '<input type="search" class="set-find" data-t="Find a language" placeholder="' + t('Find a language') + '" aria-label="' + t('Find a language') + '" autocomplete="off" spellcheck="false"><div class="set-lang">');

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

  // Language finder: matches native name, English name or code, ignoring accents and case.
  var find = panel.querySelector('.set-find');
  function fold(x) { return (x || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
  var EN = { en: 'English', zh: 'Chinese Mandarin', hi: 'Hindi', es: 'Spanish Castellano', ar: 'Arabic', fr: 'French',
    pt: 'Portuguese Brazil', de: 'German', it: 'Italian', ja: 'Japanese Nihongo', he: 'Hebrew Ivrit', sjn: 'Elvish Sindarin Tolkien' };
  find.addEventListener('input', function () {
    var q = fold(find.value.trim());
    panel.querySelectorAll('input[name="mm-lang"]').forEach(function (r) {
      var L = LANGS.filter(function (x) { return x.id === r.value; })[0];
      r.closest('label').hidden = !!q && fold(L.name + ' ' + EN[L.id] + ' ' + L.id + ' ' + L.tag).indexOf(q) < 0;
    });
  });
  find.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    var first = [].filter.call(panel.querySelectorAll('input[name="mm-lang"]'), function (r) { return !r.closest('label').hidden; })[0];
    if (first) { first.checked = true; setLang(first.value, true); sound.blip(); }
  });

  panel.addEventListener('change', function (e) {
    var r = e.target;
    if (r.name === 'mm-theme') setTheme(r.value, true);
    else if (r.name === 'mm-lang') setLang(r.value, true);
    else if (r.name === 'mm-music') { sound.setMusic(r.value); sync(); }
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
  // No saved choice: use the visitor's browser language when the site has it.
  function guess() {
    var want = (navigator.languages || [navigator.language || 'en']);
    for (var i = 0; i < want.length; i++) {
      var w = String(want[i]).toLowerCase(), base = w.split('-')[0];
      if (base === 'iw') base = 'he';
      if (LANGS.some(function (x) { return x.id === base; })) return base;
    }
    return 'en';
  }
  var startLang = load('mm-lang', '') || guess();
  setLang(startLang, false);
  if (startLang === 'en') render();
  sync();
})();
