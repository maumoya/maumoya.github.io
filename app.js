// Scene flow: the page background takes the palette of the scene in the middle of the
// screen, content animates in once, and videos play only while visible.
(function () {
  var root = document.documentElement;
  // Scroll snap waits until the page has loaded and painted (see html.snap in style.css).
  function snap() { requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.add('snap'); }); }); }
  if (document.readyState === 'complete') snap(); else window.addEventListener('load', snap, { once: true });
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var scenes = document.querySelectorAll('.scene');
  var rail = document.querySelector('.rail');
  var railLinks = rail ? rail.querySelectorAll('a') : [];

  // Video posters: fetched only when a video comes near the screen.
  var posters = [].slice.call(document.querySelectorAll('video[data-poster]'));
  function poster(v) { v.poster = v.getAttribute('data-poster'); v.removeAttribute('data-poster'); }
  if (!('IntersectionObserver' in window)) { posters.forEach(poster); return; }
  var posterIO = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { poster(e.target); posterIO.unobserve(e.target); } });
  }, { rootMargin: '800px 0px' });
  posters.forEach(function (v) { posterIO.observe(v); });
  root.classList.add('js');

  scenes.forEach(function (s) {
    s.querySelectorAll('.fx').forEach(function (el, i) { el.style.setProperty('--i', i); });
  });

  // Reveal each scene once when a fifth of it is on screen.
  var revealer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      revealer.unobserve(e.target);
    });
  }, { threshold: 0.2 });

  // The scene crossing the middle line sets the theme and the rail position.
  var theme = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var s = e.target;
      document.body.dataset.scene = s.dataset.scene;
      if (!rail) return;
      var hit = false;
      railLinks.forEach(function (a) {
        var cur = a.dataset.for === s.id;
        a.classList.toggle('cur', cur);
        if (cur) { a.setAttribute('aria-current', 'true'); hit = true; } else { a.removeAttribute('aria-current'); }
      });
      rail.classList.toggle('on', hit);
    });
  }, { rootMargin: '-50% 0px -50% 0px' });

  scenes.forEach(function (s) { revealer.observe(s); theme.observe(s); });

  // Videos: autoplay in view (unless reduced motion), with a play/pause button each.
  document.querySelectorAll('.screen').forEach(function (box) {
    var v = box.querySelector('video');
    var btn = box.querySelector('.vbtn');
    if (!v || !btn) return; // image-only screens (e.g. animated SVG) have no controls
    var userPaused = reduced;
    function sync() {
      var playing = !v.paused;
      btn.setAttribute('aria-pressed', String(playing));
      var T = window.mmT || String;
      btn.setAttribute('aria-label', T(playing ? 'Pause video' : 'Play video'));
    }
    document.addEventListener('mm:lang', sync);
    function play() {
      var p = v.play();
      if (p && p.catch) p.catch(function () { sync(); });
    }
    v.addEventListener('play', sync);
    v.addEventListener('pause', sync);
    btn.addEventListener('click', function () {
      if (v.paused) { userPaused = false; play(); } else { userPaused = true; v.pause(); }
    });
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !userPaused) play();
        else if (!e.isIntersecting && !v.paused) v.pause();
      });
    }, { threshold: 0.35 }).observe(v);
  });

  // Game families: one carousel per game (newest version first). Tabs, arrows, swipe and the
  // arrow keys switch versions; the page palette follows the version on screen.
  document.querySelectorAll('.fam').forEach(function (sec) {
    var track = sec.querySelector('.fam-track');
    var slides = [].slice.call(sec.querySelectorAll('.fam-slide'));
    var tabs = [].slice.call(sec.querySelectorAll('.fam-tab'));
    var cur = -1, timer;
    function mark(i) {
      if (i === cur) return;
      cur = i;
      tabs.forEach(function (t, j) { if (j === i) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current'); });
      slides.forEach(function (s, j) { s.inert = j !== i; });
      sec.dataset.scene = slides[i].dataset.scene;
      var r = sec.getBoundingClientRect(), mid = window.innerHeight / 2;
      if (r.top < mid && r.bottom > mid) document.body.dataset.scene = sec.dataset.scene;
    }
    function offset(i) { return slides[i].offsetLeft - slides[0].offsetLeft; }
    function go(i, instant) {
      i = (i + slides.length) % slides.length;
      track.scrollTo({ left: offset(i), behavior: instant || reduced ? 'instant' : 'smooth' });
      mark(i);
    }
    tabs.forEach(function (t, j) { t.addEventListener('click', function () { go(j); }); });
    sec.querySelectorAll('.fam-arrow').forEach(function (b) {
      b.addEventListener('click', function () { go(cur + Number(b.dataset.dir)); });
    });
    track.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      var step = e.key === 'ArrowRight' ? 1 : -1;
      go(cur + (root.dir === 'rtl' ? -step : step));
    });
    track.addEventListener('scroll', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { mark(Math.round(Math.abs(track.scrollLeft) / track.clientWidth)); }, 90);
    });
    function fromHash() {
      var id = location.hash.slice(1);
      slides.forEach(function (s, j) { if (s.id === id) { go(j, true); sec.scrollIntoView({ behavior: 'instant' }); } });
    }
    window.addEventListener('hashchange', fromHash);
    mark(0);
    fromHash();
    window.addEventListener('load', fromHash);
  });
})();

/* Card spotlight: a soft glow follows a mouse pointer across cards. Mouse only; off for reduced motion. */
(function () {
  if (!window.matchMedia || !matchMedia('(hover: hover) and (pointer: fine)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var sel = '.card, .area, .offer, .pillar';
  document.querySelectorAll(sel).forEach(function (el) { el.classList.add('spot'); });
  var still = matchMedia('(prefers-reduced-motion: reduce)'), last = null, queued = false;
  document.addEventListener('pointermove', function (e) {
    last = e;
    if (queued || still.matches) return;
    queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var el = last.target.closest && last.target.closest(sel);
      if (!el) return;
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (last.clientX - r.left) + 'px');
      el.style.setProperty('--my', (last.clientY - r.top) + 'px');
    });
  }, { passive: true });
  document.addEventListener('pointerout', function (e) {
    var el = e.target.closest && e.target.closest(sel);
    if (el && !el.contains(e.relatedTarget)) { el.style.removeProperty('--mx'); el.style.removeProperty('--my'); }
  }, { passive: true });
})();

// Compliance demo: open -> verify (evidence saved) -> closed (owner confirms) -> start over.
document.addEventListener('click', (e) => {
  const b = e.target.closest('.cdemo .abtn'); if (!b) return;
  const li = b.closest('.act'), next = { open: 'verify', verify: 'closed', closed: 'open' };
  li.dataset.state = next[li.dataset.state] || 'open';
});
