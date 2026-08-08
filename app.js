/* UrbanPulse AI — Application Runtime v3.0 */

(function () {
  'use strict';

  /* ══════════════════════════════════════
     LOADING SCREEN
  ══════════════════════════════════════ */
  const loadingScreen = document.getElementById('loadingScreen');
  if (loadingScreen) {
    const msgs = [
      'Initializing city intelligence...',
      'Loading Tamil Nadu infrastructure data...',
      'Connecting sensor network...',
      'Ready',
    ];
    let mi = 0;
    const msgEl = loadingScreen.querySelector('.loading-msg');
    const msgInterval = setInterval(() => {
      mi++;
      if (mi < msgs.length && msgEl) msgEl.textContent = msgs[mi];
      if (mi >= msgs.length) clearInterval(msgInterval);
    }, 450);

    window.addEventListener('load', () => {
      setTimeout(() => {
        loadingScreen.classList.add('hidden');
      }, 1800);
    });
  }

  /* ══════════════════════════════════════
     THEME MANAGER
  ══════════════════════════════════════ */
  const saved = localStorage.getItem('up-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);

  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    updateThemeIcon(saved);
    themeBtn.addEventListener('click', () => {
      const cur  = document.documentElement.getAttribute('data-theme');
      const next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('up-theme', next);
      updateThemeIcon(next);
      if (window.lucide) lucide.createIcons();
    });
  }

  function updateThemeIcon(theme) {
    const ico = document.getElementById('themeIcon');
    if (!ico) return;
    ico.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
  }

  /* ══════════════════════════════════════
     STICKY NAV SCROLL
  ══════════════════════════════════════ */
  const lNav = document.querySelector('.landing-nav');
  if (lNav) {
    window.addEventListener('scroll', () => {
      lNav.classList.toggle('scrolled', window.scrollY > 50);
    }, { passive: true });
  }

  /* ══════════════════════════════════════
     PAGE ENTER ANIMATION
  ══════════════════════════════════════ */
  const pageBody = document.querySelector('.page-body');
  if (pageBody) pageBody.style.animationDelay = '0ms';

  /* ══════════════════════════════════════
     SMOOTH NAVIGATION TRANSITIONS
  ══════════════════════════════════════ */
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript') || link.target === '_blank') return;

    const page = document.querySelector('.page-body');
    if (page) {
      e.preventDefault();
      page.style.transition = 'opacity 0.18s ease, transform 0.18s ease';
      page.style.opacity = '0';
      page.style.transform = 'translateY(8px)';
      setTimeout(() => { window.location.href = href; }, 200);
    }
  });

  /* ══════════════════════════════════════
     ANIMATED NUMBER COUNTERS
  ══════════════════════════════════════ */
  function animateCount(el) {
    const raw      = el.dataset.counter;
    const target   = parseFloat(raw);
    const decimals = parseInt(el.dataset.decimals || '0');
    const duration = 1800;
    const start    = performance.now();

    function ease(t) { return 1 - Math.pow(1 - t, 3); }

    function step(now) {
      const p  = Math.min((now - start) / duration, 1);
      const v  = target * ease(p);
      const suffix = el.dataset.suffix || '';
      el.textContent = (decimals > 0 ? v.toFixed(decimals) : Math.floor(v).toLocaleString()) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  const counterObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { animateCount(e.target); counterObs.unobserve(e.target); }
    });
  }, { threshold: 0.25 });
  document.querySelectorAll('[data-counter]').forEach(el => counterObs.observe(el));

  /* ══════════════════════════════════════
     SCROLL REVEAL
  ══════════════════════════════════════ */
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => {
          e.target.style.opacity  = '1';
          e.target.style.transform = 'translateY(0) scale(1)';
        }, (e.target.dataset.revealDelay || 0) * 1);
        revealObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.07 });

  document.querySelectorAll('.reveal').forEach(el => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(24px) scale(0.98)';
    el.style.transition = 'opacity 0.55s cubic-bezier(0.4,0,0.2,1), transform 0.55s cubic-bezier(0.4,0,0.2,1)';
    revealObs.observe(el);
  });

  /* ══════════════════════════════════════
     PROGRESS BAR ANIMATION
  ══════════════════════════════════════ */
  const barObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const fill = e.target.querySelector('.progress-fill');
        const w    = fill?.dataset.width;
        if (w && fill) setTimeout(() => { fill.style.width = w + '%'; }, 150);
        barObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.2 });
  document.querySelectorAll('.progress-wrap').forEach(el => barObs.observe(el));

  /* ══════════════════════════════════════
     TOAST SYSTEM
  ══════════════════════════════════════ */
  window.showToast = function (msg, type = 'info', dur = 5000) {
    let stack = document.getElementById('toastStack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'toastStack';
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    const icons = { success: 'check-circle-2', danger: 'alert-triangle', warning: 'alert-circle', info: 'info', ai: 'bot' };
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `
      <i data-lucide="${icons[type] || 'info'}" style="width:16px;height:16px;flex-shrink:0;"></i>
      <span style="flex:1;line-height:1.5;">${msg}</span>
      <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:var(--text-muted);padding:0;margin-left:8px;display:flex;">
        <i data-lucide="x" style="width:14px;height:14px;"></i>
      </button>
    `;
    stack.appendChild(t);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
      t.style.opacity   = '0';
      t.style.transform = 'translateX(30px) scale(0.95)';
      t.style.transition = 'all 0.3s ease';
      setTimeout(() => t.remove(), 320);
    }, dur);
  };

  /* Auto-dismiss flash toasts in-page */
  document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => {
      t.style.opacity   = '0';
      t.style.transform = 'translateX(20px)';
      t.style.transition = 'all 0.3s ease';
      setTimeout(() => t.remove(), 330);
    }, 5000);
  });

  /* ══════════════════════════════════════
     RIPPLE EFFECT
  ══════════════════════════════════════ */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn || btn.classList.contains('btn-sos')) return;

    const rect   = btn.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height);
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.cssText = `
      width: ${size}px; height: ${size}px;
      left: ${e.clientX - rect.left - size / 2}px;
      top:  ${e.clientY - rect.top  - size / 2}px;
    `;
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });

  /* ══════════════════════════════════════
     TAB SYSTEM
  ══════════════════════════════════════ */
  document.querySelectorAll('.tabs-wrap').forEach(wrap => {
    const tabs   = wrap.querySelectorAll('.tab-btn');
    const slider = wrap.querySelector('.tab-slider');
    const panels = document.querySelectorAll('.tab-panel');

    function activateTab(tab) {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      if (slider) {
        slider.style.left  = tab.offsetLeft + 'px';
        slider.style.width = tab.offsetWidth + 'px';
      }
      const target = tab.dataset.tab;
      panels.forEach(p => {
        p.style.display = p.id === target ? 'block' : 'none';
        if (p.id === target) {
          p.style.animation = 'fadeUp 0.3s ease';
        }
      });
    }

    const firstActive = wrap.querySelector('.tab-btn.active') || tabs[0];
    if (firstActive) activateTab(firstActive);

    tabs.forEach(tab => {
      tab.addEventListener('click', () => activateTab(tab));
    });
  });

  /* ══════════════════════════════════════
     TYPEWRITER FOR AI
  ══════════════════════════════════════ */
  window.typeWrite = function (el, text, speed = 16, onDone) {
    el.textContent = '';
    let i = 0;
    const id = setInterval(() => {
      el.textContent += text[i++];
      if (i >= text.length) {
        clearInterval(id);
        if (onDone) onDone();
      }
    }, speed);
    return id;
  };

  /* ══════════════════════════════════════
     ACTIVE NAV LINK
  ══════════════════════════════════════ */
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[href]').forEach(item => {
    const href = item.getAttribute('href') || '';
    if (href !== '/' && path.startsWith(href.split('?')[0])) {
      item.classList.add('active');
    }
  });

  /* ══════════════════════════════════════
     MICRO INTERACTIONS — Icon hover
  ══════════════════════════════════════ */
  document.querySelectorAll('.kpi-icon').forEach(icon => {
    const card = icon.closest('.kpi-card') || icon.parentElement;
    if (!card) return;
    card.addEventListener('mouseenter', () => {
      icon.style.transition = 'transform var(--t-spring), box-shadow var(--t-med)';
    });
  });

  /* ══════════════════════════════════════
     NAVBAR PROGRESS BAR (page load indicator)
  ══════════════════════════════════════ */
  const navbar = document.querySelector('.top-navbar');
  if (navbar) {
    const bar = document.createElement('div');
    bar.className = 'navbar-progress';
    navbar.appendChild(bar);
    setTimeout(() => {
      bar.style.opacity = '0';
      bar.style.transition = 'opacity 0.4s ease';
    }, 1200);
  }

  /* ══════════════════════════════════════
     LUCIDE ICONS INIT
  ══════════════════════════════════════ */
  if (window.lucide) lucide.createIcons();

})();
