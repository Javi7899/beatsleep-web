// Two behaviours, and nothing else: the masthead notices it has left the top,
// and anything marked .rise arrives as it comes into view. Both stand down
// when the reader has asked for less motion.
//
// The reveals are the only thing on this site that can hide content, so they
// are written to fail open: reduced motion, no IntersectionObserver, a script
// that runs late, an observer that never fires — every one of those ends with
// everything visible rather than with a black page.
(function () {
  var mast = document.querySelector('.mast');
  if (mast) {
    var onScroll = function () {
      mast.classList.toggle('stuck', window.scrollY > 12);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var risers = document.querySelectorAll('.rise');
  if (!risers.length) return;

  var revealAll = function () {
    for (var i = 0; i < risers.length; i++) risers[i].classList.add('seen');
  };

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
      !('IntersectionObserver' in window)) {
    revealAll();
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('seen');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });

  risers.forEach(function (el) { io.observe(el); });

  // The failsafe. If the observer has not accounted for something after four
  // seconds — a background tab, a browser that throttles it, anything — the
  // page stops waiting and shows the lot.
  window.setTimeout(revealAll, 4000);
})();
