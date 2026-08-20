// Hot Pot World Rotary. Progressive enhancement only.
// Every page works with JavaScript disabled; this just improves it.

(function () {
  'use strict';

  // Marks the document so the stylesheet knows it may hide things before
  // revealing them. Without JS nothing is ever hidden in the first place.
  document.documentElement.classList.add('js');

  var MOBILE_NAV = 900;   // keep in sync with the nav breakpoint in style.css

  // --- mobile navigation -------------------------------------------------
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');

  function closeNav() {
    toggle.setAttribute('aria-expanded', 'false');
    nav.setAttribute('data-open', 'false');
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.setAttribute('data-open', String(!open));
    });

    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && window.innerWidth <= MOBILE_NAV) closeNav();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.getAttribute('data-open') === 'true') {
        closeNav();
        toggle.focus();
      }
    });
  }

  // --- click-to-load video ----------------------------------------------
  // The YouTube iframe is only injected on click, so loading a page never
  // fires a request at youtube.com.
  document.querySelectorAll('.video[data-video-id]').forEach(function (el) {
    el.addEventListener('click', function () {
      var id = el.getAttribute('data-video-id');
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id +
                  '?autoplay=1&rel=0&modestbranding=1';
      frame.title = el.getAttribute('data-video-title') || 'Video';
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; ' +
                    'gyroscope; picture-in-picture; web-share';
      frame.allowFullscreen = true;
      el.replaceChildren(frame);
    }, { once: true });
  });

  // --- in-page nav highlighting ------------------------------------------
  // The nav points at sections of this one page, so it should say which one you
  // are looking at. Same IntersectionObserver approach as the reveals, never a
  // scroll listener. The observer's root margin leaves a thin band across the
  // upper middle of the viewport; whichever section occupies that band is the
  // one the reader is in.
  if (nav) {
    var spyLinks = [];
    nav.querySelectorAll('a[href^="#"]').forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      // #top is the whole document, so hang it off the hero instead.
      var target = id === 'top' ? document.querySelector('.hero')
                                : document.getElementById(id);
      if (target) spyLinks.push({ link: a, target: target });
    });

    if (spyLinks.length && 'IntersectionObserver' in window) {
      var setCurrent = function (link) {
        spyLinks.forEach(function (s) {
          if (s.link === link) s.link.setAttribute('aria-current', 'true');
          else s.link.removeAttribute('aria-current');
        });
      };

      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var match = spyLinks.filter(function (s) { return s.target === entry.target; })[0];
          if (match) setCurrent(match.link);
        });
      }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

      spyLinks.forEach(function (s) { spy.observe(s.target); });
    }
  }

  // --- scroll reveal -----------------------------------------------------
  // Sequencing only: a section's heading lands before its content. Uses
  // IntersectionObserver, never a scroll listener, and does nothing at all
  // when the visitor has asked for reduced motion.
  var reveals = document.querySelectorAll('[data-reveal]');
  var wantsMotion = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reveals.length && wantsMotion && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }
})();
