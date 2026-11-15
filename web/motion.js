/* Groundwater-inspired contour motion.
   Decorative only: it does not animate or alter scientific map measurements. */
(() => {
  'use strict';
  const visual = document.querySelector('.overview-visual');
  const canvas = visual?.querySelector('.overview-fluid');
  if (!visual || !canvas || !canvas.getContext) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = window.matchMedia('(pointer: coarse)');
  const ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  const TWO_PI = Math.PI * 2;
  const pointer = { x: 0, y: 0, targetX: 0, targetY: 0, strength: 0, targetStrength: 0 };
  let width = 1, height = 1, scale = 1, frameId = 0, lastDraw = 0;
  let inView = false;
  let phase = 0;

  function resize() {
    const bounds = visual.getBoundingClientRect();
    width = Math.max(1, bounds.width);
    height = Math.max(1, bounds.height);
    scale = Math.min(window.devicePixelRatio || 1, 1.75);
    canvas.width = Math.max(1, Math.round(width * scale));
    canvas.height = Math.max(1, Math.round(height * scale));
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    pointer.x = pointer.targetX = width / 2;
    pointer.y = pointer.targetY = height / 2;
  }

  function draw(time) {
    ctx.clearRect(0, 0, width, height);
    const span = Math.min(width, height);
    const cx = width * 0.5;
    const cy = height * 0.49;
    const radiusMax = span * 0.45;
    phase += (time - lastDraw || 24) * 0.00027;
    const movement = pointer.strength;
    const mouseRadius = Math.max(60, span * 0.24);
    const mouseAngle = Math.atan2(pointer.y - cy, pointer.x - cx);

    // Closely spaced, gently distorted contours evoke subsurface deformation.
    for (let ring = 0; ring < 11; ring++) {
      const radius = span * (0.16 + ring * 0.027);
      const outerness = ring / 10;
      ctx.beginPath();
      for (let point = 0; point <= 144; point++) {
        const angle = point / 144 * TWO_PI;
        const ux = Math.cos(angle);
        const uy = Math.sin(angle);
        const slowWave = Math.sin(angle * 3 + phase * 1.1 + ring * 0.34) * (2.2 + outerness * 3.4);
        const foldedWave = Math.cos(angle * 5 - phase * 0.8 + ring * 0.23) * (1.8 + outerness * 2.4);
        const r = radius + slowWave + foldedWave;
        let x = cx + ux * r;
        let y = cy + uy * r;
        const dist = Math.hypot(x - pointer.x, y - pointer.y);
        const proximity = Math.exp(-(dist * dist) / (2 * mouseRadius * mouseRadius));
        const shear = movement * proximity * (11 + outerness * 22);
        // The displacement leads the pointer and eases back with spring-like inertia.
        x += shear * Math.cos(mouseAngle + Math.PI / 2) + ux * shear * 0.32;
        y += shear * Math.sin(mouseAngle + Math.PI / 2) + uy * shear * 0.32;
        if (point === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.closePath();
      const warm = ring % 4 === 1;
      const opacity = ring < 3 ? 0.12 : (0.2 - outerness * 0.06);
      ctx.strokeStyle = warm
        ? 'rgba(166,75,42,' + opacity.toFixed(3) + ')'
        : 'rgba(82,102,75,' + opacity.toFixed(3) + ')';
      ctx.lineWidth = ring % 3 === 0 ? 1.2 : 0.85;
      ctx.stroke();
    }

    // A quiet pulse is visible only when somebody interacts with the illustration.
    if (movement > 0.03) {
      const r = Math.max(15, radiusMax * (0.18 + 0.16 * Math.sin(phase * 2)));
      const halo = ctx.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, r);
      halo.addColorStop(0, 'rgba(166,75,42,' + (0.045 * movement).toFixed(3) + ')');
      halo.addColorStop(1, 'rgba(166,75,42,0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(pointer.x, pointer.y, r, 0, TWO_PI);
      ctx.fill();
    }
  }

  function stop() {
    if (frameId) cancelAnimationFrame(frameId);
    frameId = 0;
    visual.style.removeProperty('--fluid-shift-x');
    visual.style.removeProperty('--fluid-shift-y');
  }

  function frame(time) {
    frameId = 0;
    if (reduced.matches || !inView || document.hidden) return;
    // Cap the decorative effect to approximately 40 fps; use 30 fps on touch devices.
    const minInterval = coarse.matches ? 33 : 25;
    if (time - lastDraw >= minInterval) {
      pointer.x += (pointer.targetX - pointer.x) * 0.09;
      pointer.y += (pointer.targetY - pointer.y) * 0.09;
      pointer.strength += (pointer.targetStrength - pointer.strength) * 0.075;
      const shiftX = (pointer.x / width - 0.5) * pointer.strength * 14;
      const shiftY = (pointer.y / height - 0.5) * pointer.strength * 14;
      visual.style.setProperty('--fluid-shift-x', shiftX.toFixed(2) + 'px');
      visual.style.setProperty('--fluid-shift-y', shiftY.toFixed(2) + 'px');
      draw(time);
      lastDraw = time;
    }
    frameId = requestAnimationFrame(frame);
  }

  function start() {
    if (!frameId && inView && !document.hidden && !reduced.matches) {
      lastDraw = 0;
      frameId = requestAnimationFrame(frame);
    }
  }

  visual.addEventListener('pointermove', event => {
    if (coarse.matches || reduced.matches) return;
    const bounds = visual.getBoundingClientRect();
    pointer.targetX = event.clientX - bounds.left;
    pointer.targetY = event.clientY - bounds.top;
    pointer.targetStrength = 1;
  }, { passive: true });
  visual.addEventListener('pointerleave', () => { pointer.targetStrength = 0; }, { passive: true });

  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(visual);
  else window.addEventListener('resize', resize, { passive: true });
  resize();

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inView = entries.some(entry => entry.isIntersecting);
      if (inView) start(); else stop();
    }, { rootMargin: '100px 0px' }).observe(visual);
  } else {
    inView = true;
    start();
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop(); else start();
  });
  if (reduced.addEventListener) reduced.addEventListener('change', () => {
    if (reduced.matches) { stop(); ctx.clearRect(0, 0, width, height); }
    else start();
  });

  // The same restrained pace carries into the editorial sections on scroll.
  const reveals = document.querySelectorAll(
    '.overview-narrative-head, .overview-narrative-grid article, ' +
    '.overview-purpose-header, .overview-audiences article, ' +
    '.overview-proof-heading, .overview-proof-card, ' +
    '.overview-evidence-copy, .overview-steps > div'
  );
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('motion-visible');
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
    document.documentElement.classList.add('motion-active');
    reveals.forEach((element, index) => {
      element.classList.add('motion-reveal');
      // Keep grouped panels flowing together instead of a theatrical cascade.
      if (element.matches('.overview-narrative-grid article, .overview-proof-card, .overview-audiences article')) {
        element.style.setProperty('--reveal-delay', (index % 3) * 65 + 'ms');
      }
      observer.observe(element);
    });
  }
})();
