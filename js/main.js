const COOKIE_CONSENT_KEY = 'sopjanitech_cookie_consent';
const cookieBanner = document.getElementById('cookieBanner');
const cookieAccept = document.getElementById('cookieAccept');

const GA4_ID = 'G-KXN3RQB89P';
let ga4Loaded = false;

function hasCookieConsent() {
  try { return localStorage.getItem(COOKIE_CONSENT_KEY) === '1'; } catch (e) { return false; }
}

function loadGA4() {
  if (!GA4_ID || ga4Loaded) return;
  ga4Loaded = true;
  const link = document.createElement('link');
  link.rel = 'preconnect';
  link.href = 'https://www.googletagmanager.com';
  document.head.appendChild(link);
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  document.head.appendChild(s);
  s.onload = () => {
    gtag('js', new Date());
    gtag('config', GA4_ID, {
      anonymize_ip: true,
      cookie_flags: 'SameSite=None;Secure',
      send_page_view: true
    });
  };
}

function initCookieBanner() {
  if (!cookieBanner) return;
  if (hasCookieConsent()) return;
  cookieBanner.hidden = false;
}

function acceptCookies() {
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, '1');
  } catch (e) {}
  if (cookieBanner) cookieBanner.hidden = true;
  loadGA4();
}

if (cookieAccept) {
  cookieAccept.addEventListener('click', acceptCookies);
}
initCookieBanner();
if (hasCookieConsent()) loadGA4();

const burger = document.getElementById('burger');
const mobileNav = document.getElementById('mobileNav');
const mobileNavOverlay = document.getElementById('mobileNavOverlay');
const mobileNavClose = document.getElementById('mobileNavClose');

function setMobileNav(open) {
  if (!mobileNav || !burger) return;
  mobileNav.classList.toggle('open', open);
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  mobileNav.setAttribute('aria-hidden', !open);
  document.body.classList.toggle('nav-open', open);
  if (mobileNavOverlay) {
    mobileNavOverlay.hidden = !open;
  }
}

function closeMobileNav() {
  setMobileNav(false);
}

if (burger && mobileNav) {
  burger.addEventListener('click', () => {
    setMobileNav(!mobileNav.classList.contains('open'));
  });
  if (mobileNavClose) {
    mobileNavClose.addEventListener('click', closeMobileNav);
  }
  mobileNav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', closeMobileNav);
  });
  if (mobileNavOverlay) {
    mobileNavOverlay.addEventListener('click', closeMobileNav);
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && mobileNav.classList.contains('open')) closeMobileNav();
  });
}
function closeNavDropdowns() {
  document.querySelectorAll('.nav-item.is-open').forEach(item => {
    item.classList.remove('is-open');
    item.querySelector('.nav-trigger')?.setAttribute('aria-expanded', 'false');
  });
}
document.querySelectorAll('.nav-item').forEach(item => {
  const trigger = item.querySelector('.nav-trigger');
  const submenu = item.querySelector('.nav-submenu');
  if (!trigger || !submenu) return;
  trigger.addEventListener('click', e => {
    e.stopPropagation();
    const isOpen = item.classList.contains('is-open');
    closeNavDropdowns();
    if (!isOpen) {
      item.classList.add('is-open');
      trigger.setAttribute('aria-expanded', 'true');
    }
  });
  submenu.addEventListener('click', e => e.stopPropagation());
});
document.addEventListener('click', closeNavDropdowns);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNavDropdowns(); });
document.querySelectorAll('.mobile-nav-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const group = btn.closest('.mobile-nav-group');
    if (!group) return;
    const willOpen = !group.classList.contains('is-open');
    document.querySelectorAll('.mobile-nav-group.is-open').forEach(openGroup => {
      if (openGroup === group) return;
      openGroup.classList.remove('is-open');
      openGroup.querySelector('.mobile-nav-toggle')?.setAttribute('aria-expanded', 'false');
    });
    group.classList.toggle('is-open', willOpen);
    btn.setAttribute('aria-expanded', willOpen);
  });
});
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const answer = btn.nextElementSibling;
    const isActive = btn.classList.contains('active');
    document.querySelectorAll('.faq-q').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-expanded', 'false');
      b.nextElementSibling.classList.remove('open');
    });
    if (!isActive) {
      btn.classList.add('active');
      btn.setAttribute('aria-expanded', 'true');
      answer.classList.add('open');
    }
  });
});
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});
function trackEvent(name, params) {
  if (typeof gtag === 'function') gtag('event', name, params || {});
}
document.querySelectorAll('.track-phone').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'phone', event_category: 'contact' });
    trackEvent('click_phone', { event_category: 'contact', event_label: 'phone' });
  });
});
document.querySelectorAll('.track-email').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'email', event_category: 'contact' });
    trackEvent('click_email', { event_category: 'contact', event_label: 'email' });
  });
});
document.querySelectorAll('.track-whatsapp').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'whatsapp', event_category: 'contact' });
    trackEvent('click_whatsapp', { event_category: 'contact', event_label: 'whatsapp' });
  });
});
document.querySelectorAll('.track-devis').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('generate_lead', { method: 'devis_button', event_category: 'conversion' });
    trackEvent('click_devis', { event_category: 'conversion', event_label: 'demande_devis' });
  });
});
document.querySelectorAll('.track-form').forEach(form => {
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const endpoint = form.getAttribute('data-form-endpoint') || form.getAttribute('action') || '';
    const feedback = form.querySelector('.form-feedback');
    const submitBtn = form.querySelector('[type="submit"]');
    trackEvent('generate_lead', { method: 'contact_form', event_category: 'conversion' });
    trackEvent('form_submit', { event_category: 'conversion', event_label: 'contact_form' });

    if (!endpoint || endpoint === '#') {
      window.location.assign('/merci/');
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
    }
    if (feedback) {
      feedback.textContent = 'Envoi en cours…';
      feedback.hidden = false;
    }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });
      const data = await res.json().catch(() => ({}));
      const ok = data.success === true || data.success === 'true';
      if (!res.ok || !ok) {
        const raw = String((data && data.message) || '');
        if (/activat/i.test(raw)) {
          throw new Error('activation');
        }
        throw new Error(raw || 'send_failed');
      }
      window.location.assign('/merci/');
      return;
    } catch (err) {
      if (feedback) {
        if (err && err.message === 'activation') {
          feedback.textContent = 'Le formulaire n’est pas encore activé. Ouvrez la boîte info@sopjanitech.ch (et les indésirables), cherchez l’e-mail FormSubmit « Activate Form », puis cliquez le lien. Ensuite renvoyez une demande.';
        } else {
          feedback.textContent = 'Envoi impossible pour le moment. Appelez-nous au +41 79 932 68 62 ou écrivez à info@sopjanitech.ch.';
        }
        feedback.hidden = false;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
      }
    }
  });
});

function updateSmartFormProgress(form, step) {
  const bar = form.querySelector('[data-form-progress]');
  const labels = form.querySelectorAll('[data-step-label]');
  if (bar) bar.style.setProperty('--progress', (step / 4 * 100) + '%');
  labels.forEach(li => {
    const n = Number(li.getAttribute('data-step-label'));
    li.classList.toggle('is-active', n === step);
    li.classList.toggle('is-done', n < step);
  });
}

function validateSmartStep(stepEl) {
  const required = stepEl.querySelectorAll('[required]');
  for (const el of required) {
    if (el.type === 'radio') {
      const name = el.name;
      if (!stepEl.querySelector(`input[name="${name}"]:checked`)) {
        const first = stepEl.querySelector(`input[name="${name}"]`);
        if (first) first.focus();
        return false;
      }
    } else if (!el.value.trim()) {
      el.focus();
      return false;
    }
  }
  return true;
}

document.querySelectorAll('.contact-form--smart').forEach(form => {
  const steps = Array.from(form.querySelectorAll('.form-step'));
  let current = 1;
  updateSmartFormProgress(form, current);

  // Prefill from ?need=installation|maintenance|depannage
  try {
    const params = new URLSearchParams(window.location.search);
    const needMap = {
      installation: 'Devis installation',
      maintenance: 'Maintenance / entretien',
      depannage: 'Dépannage',
      sprinkler: 'Sprinkler / incendie',
    };
    const needKey = (params.get('need') || '').toLowerCase();
    if (needMap[needKey]) {
      const radio = form.querySelector(`input[name="need"][value="${needMap[needKey]}"]`);
      if (radio) radio.checked = true;
    }
  } catch (_) {}

  form.addEventListener('change', e => {
    if (e.target && e.target.name === 'urgency') {
      const urgent = form.querySelector('[data-urgent-cta]');
      if (urgent) urgent.hidden = e.target.value !== 'Urgent';
    }
  });

  form.querySelectorAll('[data-form-next]').forEach(btn => {
    btn.addEventListener('click', () => {
      const stepEl = form.querySelector(`.form-step[data-step="${current}"]`);
      if (!stepEl || !validateSmartStep(stepEl)) return;
      if (current >= steps.length) return;
      stepEl.hidden = true;
      stepEl.classList.remove('is-active');
      current += 1;
      const next = form.querySelector(`.form-step[data-step="${current}"]`);
      if (next) {
        next.hidden = false;
        next.classList.add('is-active');
      }
      updateSmartFormProgress(form, current);
    });
  });

  form.querySelectorAll('[data-form-back]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (current <= 1) return;
      const stepEl = form.querySelector(`.form-step[data-step="${current}"]`);
      if (stepEl) {
        stepEl.hidden = true;
        stepEl.classList.remove('is-active');
      }
      current -= 1;
      const prev = form.querySelector(`.form-step[data-step="${current}"]`);
      if (prev) {
        prev.hidden = false;
        prev.classList.add('is-active');
      }
      updateSmartFormProgress(form, current);
    });
  });
});
document.querySelectorAll('.track-google').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('click_google', { event_category: 'contact', event_label: 'google_business' });
  });
});

/* Magnetic carousel — dock-style magnify (vanilla, no React) */
(function initMagneticCarousels() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isCoarse = window.matchMedia('(pointer: coarse)').matches;

  document.querySelectorAll('.magnetic-carousel').forEach(root => {
    const track = root.querySelector('.magnetic-carousel__track');
    const backdrop = root.querySelector('.magnetic-carousel__backdrop');
    const bars = Array.from(root.querySelectorAll('.magnetic-bar'));
    if (!track || bars.length === 0) return;

    const gap = 14;
    const influence = 220;
    const blurPx = 3;
    const openDur = 300;

    function getCollapsedSize() {
      const narrow = window.matchMedia('(max-width: 768px)').matches;
      return narrow
        ? { w: 120, h: 180, hoverW: 160, hoverH: 220 }
        : { w: 148, h: 220, hoverW: 240, hoverH: 280 };
    }

    function getOpenSize() {
      return Math.min(560, Math.floor(window.innerWidth * 0.88));
    }

    let openIndex = null;
    let closing = false;
    let factors = bars.map(() => 0);
    let target = bars.map(() => 0);
    let cur = bars.map(() => 0);
    let loopId = 0;
    let closeTimer = 0;

    function applySizes() {
      const sizes = getCollapsedSize();
      const collapsedW = sizes.w;
      const collapsedH = sizes.h;
      const hoverW = sizes.hoverW;
      const hoverH = sizes.hoverH;
      const openSize = getOpenSize();
      bars.forEach((bar, i) => {
        let w = collapsedW;
        let h = collapsedH;
        if (openIndex !== null) {
          if (i === openIndex) {
            w = openSize;
            h = openSize;
          }
        } else if (!reduceMotion && !isCoarse) {
          const f = factors[i] || 0;
          w = collapsedW + (hoverW - collapsedW) * f;
          h = collapsedH + (hoverH - collapsedH) * f;
        }
        const blurred = openIndex !== null && i !== openIndex;
        bar.style.width = w + 'px';
        bar.style.height = h + 'px';
        bar.style.filter = blurred ? 'blur(' + blurPx + 'px)' : 'none';
        bar.style.opacity = blurred ? '0.55' : '1';
        bar.style.zIndex = i === openIndex ? '3' : '2';
        bar.classList.toggle('is-open', i === openIndex);
        bar.setAttribute('aria-expanded', i === openIndex ? 'true' : 'false');
        const useTransition = openIndex !== null || closing;
        bar.style.transition = useTransition
          ? 'width ' + openDur + 'ms ease-in-out, height ' + openDur + 'ms ease-in-out, filter ' + openDur + 'ms ease-in-out, opacity ' + openDur + 'ms ease-in-out'
          : 'none';
      });
      if (backdrop) {
        backdrop.hidden = openIndex === null;
        backdrop.setAttribute('aria-hidden', openIndex === null ? 'true' : 'false');
      }
      root.classList.toggle('is-expanded', openIndex !== null);
    }

    function startLoop() {
      if (loopId || reduceMotion || isCoarse || openIndex !== null) return;
      const step = () => {
        let moving = false;
        for (let i = 0; i < cur.length; i++) {
          const d = (target[i] || 0) - cur[i];
          if (Math.abs(d) > 0.001) {
            cur[i] += d * 0.2;
            moving = true;
          } else {
            cur[i] = target[i] || 0;
          }
        }
        factors = cur.slice();
        applySizes();
        loopId = moving ? requestAnimationFrame(step) : 0;
      };
      loopId = requestAnimationFrame(step);
    }

    function setTargetFromCursor(clientX) {
      const sizes = getCollapsedSize();
      const collapsedW = sizes.w;
      const rect = track.getBoundingClientRect();
      const cx = clientX - rect.left;
      const n = bars.length;
      const totalBase = n * collapsedW + (n - 1) * gap;
      const startX = (rect.width - totalBase) / 2;
      target = bars.map((_, i) => {
        const center = startX + i * (collapsedW + gap) + collapsedW / 2;
        const dist = Math.abs(cx - center);
        const f = Math.max(0, 1 - dist / influence);
        return f * f * (3 - 2 * f);
      });
      startLoop();
    }

    function close() {
      target = bars.map(() => 0);
      cur = bars.map(() => 0);
      factors = bars.map(() => 0);
      closing = true;
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => { closing = false; applySizes(); }, openDur);
      openIndex = null;
      applySizes();
    }

    function openAt(i) {
      if (openIndex === i) {
        close();
        return;
      }
      openIndex = i;
      target = bars.map(() => 0);
      cur = bars.map(() => 0);
      factors = bars.map(() => 0);
      applySizes();
    }

    track.addEventListener('mousemove', e => {
      if (reduceMotion || isCoarse || openIndex !== null) return;
      setTargetFromCursor(e.clientX);
    });
    track.addEventListener('mouseleave', () => {
      if (openIndex !== null) return;
      target = bars.map(() => 0);
      startLoop();
    });

    bars.forEach((bar, i) => {
      bar.addEventListener('click', e => {
        e.stopPropagation();
        openAt(i);
      });
    });
    if (backdrop) backdrop.addEventListener('click', close);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && openIndex !== null) close();
    });

    applySizes();
  });
})();
