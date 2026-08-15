/* The section cut: progressive enhancement only.
   The SVG is static and carries <title> on every element, so it works with
   JavaScript off — this just promotes those titles into a persistent panel
   that is readable on a phone, where hover does not exist. */
(function () {
  'use strict';

  var svg = document.getElementById('sectioncut');
  var panel = document.getElementById('section-detail');
  if (!svg || !panel) return;

  var SELECTOR = '.sc-struct, .sc-room, .sc-band, .sc-haz';
  var current = null;

  function kindOf(el) {
    if (el.classList.contains('sc-room')) return 'under';
    if (el.classList.contains('sc-haz')) return 'hazard';
    return 'surface';
  }

  function show(el) {
    var title = el.querySelector('title');
    if (!title) return;
    var text = title.textContent.trim();
    var split = text.indexOf(' — ');
    var name = split > -1 ? text.slice(0, split) : text;
    var body = split > -1 ? text.slice(split + 3) : '';

    if (current && current !== el) current.removeAttribute('data-active');
    el.setAttribute('data-active', '');
    current = el;

    panel.setAttribute('data-kind', kindOf(el));
    panel.innerHTML = '';
    var h = document.createElement('h3');
    h.textContent = name;
    var p = document.createElement('p');
    p.textContent = body;
    panel.appendChild(h);
    if (body) panel.appendChild(p);
  }

  svg.querySelectorAll(SELECTOR).forEach(function (el) {
    el.addEventListener('click', function () { show(el); });
    el.addEventListener('mouseenter', function () { show(el); });
    el.addEventListener('focus', function () { show(el); });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        show(el);
      }
    });
  });

  /* Nudge the scroller so the parcel, not the empty sea, is what you land on. */
  var scroller = svg.closest('.section-scroll');
  if (scroller && scroller.scrollWidth > scroller.clientWidth) {
    scroller.scrollLeft = Math.min(180, scroller.scrollWidth - scroller.clientWidth);
  }
})();
