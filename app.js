// Two behaviours, and nothing else: the masthead notices it has left the top,
// and anything marked .rise arrives as it comes into view. Both stand down
// when the reader has asked for less motion.
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

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
      !('IntersectionObserver' in window)) {
    risers.forEach(function (el) { el.classList.add('seen'); });
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
})();
