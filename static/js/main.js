/* main.js — Balirah Beauty Salon
   Light theme only. No dark/theme toggle code.
   Navbar / hamburger / scroll-shadow / active-link logic lives in base.html.
   This file owns all page-level interactive components.
   ─────────────────────────────────────────────────────────────────────────── */

'use strict';

const Balirah = (() => {

  /* ── Utility: debounce ──────────────────────────────────────────────────── */
  const debounce = (fn, ms = 150) => {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  /* ── Utility: safe querySelector (returns null instead of throwing) ─────── */
  const qs  = (sel, ctx = document) => ctx.querySelector(sel);
  const qsa = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ══════════════════════════════════════════════════════════════════════════
     TESTIMONIALS CAROUSEL
     Keyboard navigable, touch/swipe, auto-play pauses on hover/focus.
  ══════════════════════════════════════════════════════════════════════════ */
  const carousel = () => {
    qsa('[data-carousel]').forEach(wrapper => {
      const track   = qs('.testimonials-track', wrapper);
      const dots    = qsa('.carousel-dot', wrapper);
      const prevBtn = qs('[data-carousel-prev]', wrapper);
      const nextBtn = qs('[data-carousel-next]', wrapper);
      if (!track) return;

      const items = qsa('.testimonial-card', track);
      if (!items.length) return;

      let current   = 0;
      let autoTimer = null;
      let isAnimating = false;

      const go = (idx, source = 'auto') => {
        if (isAnimating && source !== 'auto') return;
        isAnimating = true;
        current = ((idx % items.length) + items.length) % items.length;

        track.style.transition = source === 'auto'
          ? 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
          : 'transform 0.45s cubic-bezier(0.4, 0, 0.2, 1)';
        track.style.transform = `translateX(-${current * 100}%)`;

        dots.forEach((d, i) => {
          d.classList.toggle('active', i === current);
          d.setAttribute('aria-selected', i === current ? 'true' : 'false');
        });

        // Update ARIA live region
        const liveRegion = qs('.carousel-live', wrapper);
        if (liveRegion) {
          liveRegion.textContent = `Testimonial ${current + 1} of ${items.length}`;
        }

        setTimeout(() => { isAnimating = false; }, 650);
      };

      const startAuto = () => {
        clearInterval(autoTimer);
        autoTimer = setInterval(() => go(current + 1, 'auto'), 5500);
      };
      const stopAuto = () => clearInterval(autoTimer);

      // ARIA live region for screen readers
      const liveRegion = document.createElement('span');
      liveRegion.className = 'carousel-live sr-only';
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      wrapper.appendChild(liveRegion);

      // Dot accessibility setup
      dots.forEach((dot, i) => {
        dot.setAttribute('role', 'tab');
        dot.setAttribute('aria-label', `Testimonial ${i + 1}`);
        dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
        dot.addEventListener('click', () => { go(i, 'user'); startAuto(); });
      });

      if (prevBtn) {
        prevBtn.setAttribute('aria-label', 'Previous testimonial');
        prevBtn.addEventListener('click', () => { go(current - 1, 'user'); startAuto(); });
      }
      if (nextBtn) {
        nextBtn.setAttribute('aria-label', 'Next testimonial');
        nextBtn.addEventListener('click', () => { go(current + 1, 'user'); startAuto(); });
      }

      // Touch / swipe
      let touchStartX = 0;
      let touchStartY = 0;
      track.addEventListener('touchstart', e => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }, { passive: true });
      track.addEventListener('touchend', e => {
        const dx = touchStartX - e.changedTouches[0].clientX;
        const dy = Math.abs(touchStartY - e.changedTouches[0].clientY);
        if (Math.abs(dx) > 50 && dy < 40) {
          go(dx > 0 ? current + 1 : current - 1, 'user');
          startAuto();
        }
      }, { passive: true });

      // Keyboard navigation when focused inside wrapper
      wrapper.addEventListener('keydown', e => {
        if (e.key === 'ArrowLeft')  { go(current - 1, 'user'); startAuto(); }
        if (e.key === 'ArrowRight') { go(current + 1, 'user'); startAuto(); }
      });

      // Pause on hover / focus
      wrapper.addEventListener('mouseenter', stopAuto);
      wrapper.addEventListener('mouseleave', startAuto);
      wrapper.addEventListener('focusin',   stopAuto);
      wrapper.addEventListener('focusout',  startAuto);

      go(0, 'auto');
      startAuto();
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     GALLERY LIGHTBOX
     Keyboard navigable, focus-trapped while open, lazy-loads full image.
  ══════════════════════════════════════════════════════════════════════════ */
  const lightbox = () => {
    const box = document.getElementById('lightbox');
    if (!box) return;

    const img       = qs('.lightbox__img', box);
    const caption   = qs('.lightbox__caption', box);
    const items     = qsa('[data-lightbox]');
    let current     = 0;
    let lastFocused = null;

    const focusableSelectors = 'button, [href], input, [tabindex]:not([tabindex="-1"])';

    const trapFocus = e => {
      const focusable = qsa(focusableSelectors, box).filter(el => !el.disabled);
      if (!focusable.length) return;
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };

    const open = idx => {
      lastFocused = document.activeElement;
      current = idx;
      img.src  = '';
      img.classList.add('loading');
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
      box.setAttribute('aria-hidden', 'false');

      const fullSrc = items[idx].dataset.lightbox;
      const tempImg = new Image();
      tempImg.onload = () => {
        img.src = fullSrc;
        img.alt = items[idx].dataset.title || items[idx].getAttribute('aria-label') || '';
        img.classList.remove('loading');
        if (caption) caption.textContent = items[idx].dataset.title || '';
      };
      tempImg.src = fullSrc;

      // Focus the close button
      setTimeout(() => qs('.lightbox__close', box)?.focus(), 50);
      document.addEventListener('keydown', handleLightboxKey);
    };

    const close = () => {
      box.classList.remove('open');
      document.body.style.overflow = '';
      box.setAttribute('aria-hidden', 'true');
      document.removeEventListener('keydown', handleLightboxKey);
      lastFocused?.focus();
    };

    const nav = dir => {
      current = ((current + dir + items.length) % items.length);
      img.style.opacity = '0';
      img.classList.add('loading');
      const tempImg = new Image();
      tempImg.onload = () => {
        img.src   = items[current].dataset.lightbox;
        img.alt   = items[current].dataset.title || '';
        img.style.opacity = '1';
        img.classList.remove('loading');
        if (caption) caption.textContent = items[current].dataset.title || '';
      };
      tempImg.src = items[current].dataset.lightbox;
    };

    const handleLightboxKey = e => {
      if (e.key === 'Escape')     close();
      if (e.key === 'ArrowLeft')  nav(-1);
      if (e.key === 'ArrowRight') nav(1);
      if (e.key === 'Tab')        trapFocus(e);
    };

    // Wire up gallery items
    items.forEach((el, i) => {
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
      el.setAttribute('aria-haspopup', 'dialog');
      el.setAttribute('aria-label', el.dataset.title ? `View: ${el.dataset.title}` : `View image ${i + 1}`);
      el.addEventListener('click', e => { e.preventDefault(); open(i); });
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); }
      });
    });

    qs('.lightbox__close', box)?.addEventListener('click', close);
    qs('.lightbox__prev',  box)?.addEventListener('click', () => nav(-1));
    qs('.lightbox__next',  box)?.addEventListener('click', () => nav(1));
    box.addEventListener('click', e => { if (e.target === box) close(); });

    // Set initial aria state
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Image gallery viewer');
    box.setAttribute('aria-hidden', 'true');
  };

  /* ══════════════════════════════════════════════════════════════════════════
     FAQ ACCORDION
     Only one item open at a time (optional), smooth height animation.
  ══════════════════════════════════════════════════════════════════════════ */
  const faq = () => {
    const items = qsa('.faq-item');
    if (!items.length) return;

    items.forEach((item, idx) => {
      const question = qs('.faq-question', item);
      const answer   = qs('.faq-answer',   item);
      if (!question) return;

      const id = `faq-answer-${idx}`;
      if (answer) {
        answer.id = id;
        answer.setAttribute('role', 'region');
        // Prep for smooth height animation
        answer.style.overflow = 'hidden';
        answer.style.transition = 'max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease';
        answer.style.maxHeight  = '0';
        answer.style.opacity    = '0';
      }

      question.setAttribute('role',          'button');
      question.setAttribute('tabindex',      '0');
      question.setAttribute('aria-expanded', 'false');
      if (answer) question.setAttribute('aria-controls', id);

      const toggle = () => {
        const isOpen = item.classList.contains('open');

        // Close all others
        items.forEach(other => {
          if (other === item) return;
          const otherAnswer   = qs('.faq-answer', other);
          const otherQuestion = qs('.faq-question', other);
          other.classList.remove('open');
          if (otherQuestion) otherQuestion.setAttribute('aria-expanded', 'false');
          if (otherAnswer) {
            otherAnswer.style.maxHeight = '0';
            otherAnswer.style.opacity   = '0';
          }
        });

        // Toggle this one
        item.classList.toggle('open', !isOpen);
        question.setAttribute('aria-expanded', (!isOpen).toString());
        if (answer) {
          if (!isOpen) {
            answer.style.maxHeight = answer.scrollHeight + 'px';
            answer.style.opacity   = '1';
          } else {
            answer.style.maxHeight = '0';
            answer.style.opacity   = '0';
          }
        }
      };

      question.addEventListener('click', toggle);
      question.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
        if (e.key === 'ArrowDown') { e.preventDefault(); items[(idx + 1) % items.length]?.querySelector('.faq-question')?.focus(); }
        if (e.key === 'ArrowUp')   { e.preventDefault(); items[(idx - 1 + items.length) % items.length]?.querySelector('.faq-question')?.focus(); }
      });
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     GALLERY CATEGORY FILTER
     Animated show/hide with staggered entry.
  ══════════════════════════════════════════════════════════════════════════ */
  const galleryFilter = () => {
    const filterBtns = qsa('.gallery-filter');
    const items      = qsa('.gallery-item');
    if (!filterBtns.length) return;

    const filterGroup = filterBtns[0]?.closest('[role="group"]') || filterBtns[0]?.parentElement;
    if (filterGroup && !filterGroup.getAttribute('role')) {
      filterGroup.setAttribute('role', 'group');
      filterGroup.setAttribute('aria-label', 'Filter gallery by category');
    }

    filterBtns.forEach(btn => {
      btn.setAttribute('role', 'button');
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');

        const cat = btn.dataset.filter;
        let visibleIdx = 0;

        items.forEach(item => {
          const match = cat === 'all' || item.dataset.category === cat;
          if (match) {
            item.style.display = '';
            // Staggered entry
            item.style.opacity   = '0';
            item.style.transform = 'scale(0.94)';
            item.style.transition = `opacity 0.35s ease ${visibleIdx * 60}ms, transform 0.35s ease ${visibleIdx * 60}ms`;
            requestAnimationFrame(() => {
              item.style.opacity   = '1';
              item.style.transform = 'scale(1)';
            });
            visibleIdx++;
          } else {
            item.style.display = 'none';
          }
        });
      });
    });

    // Set initial aria state
    filterBtns.forEach(b => b.setAttribute('aria-pressed', b.classList.contains('active') ? 'true' : 'false'));
  };

  /* ══════════════════════════════════════════════════════════════════════════
     SERVICE CATEGORY TABS
     ARIA tablist / tabpanel pattern.
  ══════════════════════════════════════════════════════════════════════════ */
  const serviceTabs = () => {
    const tabs   = qsa('.service-tab');
    const panels = qsa('.service-panel');
    if (!tabs.length) return;

    // ARIA setup
    const tabList = tabs[0]?.closest('.service-tab-nav') || tabs[0]?.parentElement;
    if (tabList) tabList.setAttribute('role', 'tablist');

    tabs.forEach((tab, i) => {
      const panelId = tab.dataset.tab;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('id', `tab-${panelId}`);
      tab.setAttribute('aria-controls', panelId);
      tab.setAttribute('aria-selected', tab.classList.contains('active') ? 'true' : 'false');
      tab.setAttribute('tabindex', tab.classList.contains('active') ? '0' : '-1');

      const panel = document.getElementById(panelId);
      if (panel) {
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', `tab-${panelId}`);
      }

      tab.addEventListener('click', () => activateTab(tab));
      tab.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight') { e.preventDefault(); activateTab(tabs[(i + 1) % tabs.length]); tabs[(i + 1) % tabs.length].focus(); }
        if (e.key === 'ArrowLeft')  { e.preventDefault(); activateTab(tabs[(i - 1 + tabs.length) % tabs.length]); tabs[(i - 1 + tabs.length) % tabs.length].focus(); }
        if (e.key === 'Home')       { e.preventDefault(); activateTab(tabs[0]); tabs[0].focus(); }
        if (e.key === 'End')        { e.preventDefault(); activateTab(tabs[tabs.length - 1]); tabs[tabs.length - 1].focus(); }
      });
    });

    const activateTab = tab => {
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
        t.setAttribute('tabindex', '-1');
      });
      panels.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      tab.setAttribute('tabindex', '0');

      const target = document.getElementById(tab.dataset.tab);
      if (target) {
        target.classList.add('active');
        target.style.animation = 'panelFadeIn 0.3s ease both';
      }
    };
  };

  /* ══════════════════════════════════════════════════════════════════════════
     BOOKING FLOW
     3-step wizard with summary sidebar, slot picker, validation.
  ══════════════════════════════════════════════════════════════════════════ */
  const bookingFlow = () => {
    const form = document.getElementById('bookingForm');
    if (!form) return;

    const serviceSelect   = form.querySelector('[name="service"]');
    const stylistSelect   = form.querySelector('[name="stylist"]');
    const dateInput       = form.querySelector('[name="appointment_date"]');
    const slotsWrapper    = document.getElementById('slotsWrapper');
    const slotInput       = form.querySelector('[name="time_slot"]');
    const submitBtn       = form.querySelector('[type="submit"]');

    // Summary elements
    const summaryService  = document.getElementById('summaryService');
    const summaryStylist  = document.getElementById('summaryStylist');
    const summaryDate     = document.getElementById('summaryDate');
    const summaryTime     = document.getElementById('summaryTime');
    const summaryPrice    = document.getElementById('summaryPrice');
    const summaryDuration = document.getElementById('summaryDuration');

    /* ── Date constraints: today → +30 days, disable Sundays optionally ── */
    if (dateInput) {
      const today  = new Date();
      const maxDay = new Date();
      maxDay.setDate(maxDay.getDate() + 30);
      dateInput.min = today.toISOString().split('T')[0];
      dateInput.max = maxDay.toISOString().split('T')[0];
      dateInput.setAttribute('aria-describedby', 'dateHint');

      // Add a hint if not present
      if (!document.getElementById('dateHint')) {
        const hint = document.createElement('span');
        hint.id = 'dateHint';
        hint.className = 'hint-text';
        hint.textContent = 'Available up to 30 days from today.';
        dateInput.parentElement.appendChild(hint);
      }
    }

    /* ── Fetch available slots ─────────────────────────────────────────── */
    const fetchSlots = debounce(async () => {
      const service = serviceSelect?.value;
      const date    = dateInput?.value;
      const stylist = stylistSelect?.value;
      if (!service || !date || !slotsWrapper) return;

      // Clear previous error hint
      qs('.form-error', slotsWrapper)?.remove();

      // Loading state
      slotsWrapper.innerHTML =
        '<div class="flex-center" style="padding:2.5rem 0" aria-live="polite" aria-label="Loading available time slots">' +
        '<div class="spinner" role="status"><span class="sr-only">Loading slots…</span></div></div>';
      if (slotInput) slotInput.value = '';
      if (submitBtn) submitBtn.disabled = true;
      updateStep(2);

      try {
        const params = new URLSearchParams({ service, date });
        if (stylist) params.append('stylist', stylist);

        // CSRF token from meta tag (if present) or cookie
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
          || getCookie('csrftoken');

        const res = await fetch(`/bookings/api/slots/?${params}`, {
          headers: { 'X-CSRFToken': csrfToken || '', 'Accept': 'application/json' },
          credentials: 'same-origin',
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderSlots(data.slots || []);
      } catch (err) {
        console.warn('[Balirah] Slot fetch failed:', err);
        slotsWrapper.innerHTML =
          '<p class="form-error" role="alert">' +
          '<i class="fas fa-exclamation-circle" aria-hidden="true"></i> ' +
          'Could not load time slots. Please try again or call us directly.</p>';
      }
    }, 300);

    /* ── Render slot buttons ───────────────────────────────────────────── */
    const renderSlots = slots => {
      if (!slotsWrapper) return;
      if (!slots.length) {
        slotsWrapper.innerHTML =
          '<p style="color:var(--text-muted);font-size:var(--text-sm);padding:var(--space-3) 0" role="status">' +
          '<i class="fas fa-calendar-times" aria-hidden="true" style="color:var(--gold);margin-right:6px"></i>' +
          'No slots available for this date. Please choose another date or stylist.</p>';
        return;
      }

      slotsWrapper.innerHTML = '<div class="slots-grid" role="group" aria-label="Available time slots"></div>';
      const grid = qs('.slots-grid', slotsWrapper);

      slots.forEach((slot, i) => {
        const btn = document.createElement('button');
        btn.type      = 'button';
        btn.className = 'slot-btn';
        btn.textContent = slot.display || slot.start;
        btn.dataset.slotId = slot.id   || slot.start;
        btn.dataset.time   = slot.start;
        btn.setAttribute('aria-label', `Book ${slot.display || slot.start}`);
        btn.style.animationDelay = `${i * 40}ms`;
        btn.style.animation = 'panelFadeIn 0.3s ease both';

        btn.addEventListener('click', () => {
          qsa('.slot-btn', slotsWrapper).forEach(b => {
            b.classList.remove('selected');
            b.setAttribute('aria-pressed', 'false');
          });
          btn.classList.add('selected');
          btn.setAttribute('aria-pressed', 'true');
          if (slotInput)   slotInput.value     = slot.id || slot.start;
          if (summaryTime) summaryTime.textContent = slot.display || slot.start;
          if (submitBtn)   submitBtn.disabled   = false;
          updateStep(3);

          // Clear any lingering slot error
          qs('.form-error--slot', form)?.remove();
        });

        grid.appendChild(btn);
      });
    };

    /* ── Sync booking summary sidebar ─────────────────────────────────── */
    const updateSummary = () => {
      if (summaryService && serviceSelect) {
        const opt = serviceSelect.options[serviceSelect.selectedIndex];
        if (opt?.value) {
          summaryService.textContent = opt.text;
          if (summaryPrice)    summaryPrice.textContent    = opt.dataset.price    || '—';
          if (summaryDuration) summaryDuration.textContent = opt.dataset.duration || '—';
        } else {
          summaryService.textContent = 'Not selected';
        }
      }

      if (summaryStylist && stylistSelect) {
        const opt = stylistSelect.options[stylistSelect.selectedIndex];
        summaryStylist.textContent = (opt?.value) ? opt.text : 'Any available stylist';
      }

      if (summaryDate && dateInput?.value) {
        try {
          const d = new Date(dateInput.value + 'T00:00:00');
          summaryDate.textContent = d.toLocaleDateString('en-UG', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
          });
        } catch {
          summaryDate.textContent = dateInput.value;
        }
      }
    };

    /* ── Step indicator ────────────────────────────────────────────────── */
    const updateStep = n => {
      qsa('.booking-step').forEach((s, i) => {
        s.classList.toggle('active',    i + 1 === n);
        s.classList.toggle('completed', i + 1 < n);
        s.setAttribute('aria-current', i + 1 === n ? 'step' : 'false');
      });
      qsa('.booking-step-connector').forEach((c, i) => {
        c.classList.toggle('completed', i + 1 < n);
      });
    };

    // Initial state
    updateStep(1);
    if (submitBtn) submitBtn.disabled = true;

    /* ── Event listeners ───────────────────────────────────────────────── */
    serviceSelect?.addEventListener('change', () => {
      updateSummary();
      updateStep(serviceSelect.value ? 2 : 1);
      if (dateInput?.value) fetchSlots();
    });
    stylistSelect?.addEventListener('change', () => {
      updateSummary();
      if (serviceSelect?.value && dateInput?.value) fetchSlots();
    });
    dateInput?.addEventListener('change', () => {
      updateSummary();
      fetchSlots();
    });

    /* ── Form submit guard ─────────────────────────────────────────────── */
    form.addEventListener('submit', e => {
      // Clear previous errors
      qsa('.form-control--error', form).forEach(el => el.classList.remove('form-control--error'));
      qs('.form-error--slot', form)?.remove();

      let hasError = false;

      if (!serviceSelect?.value) {
        serviceSelect?.classList.add('form-control--error');
        serviceSelect?.focus();
        hasError = true;
      }

      if (!dateInput?.value) {
        dateInput?.classList.add('form-control--error');
        if (!hasError) dateInput?.focus();
        hasError = true;
      }

      if (!slotInput?.value) {
        if (!hasError && slotsWrapper) {
          slotsWrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        const hint = document.createElement('p');
        hint.className = 'form-error form-error--slot';
        hint.setAttribute('role', 'alert');
        hint.innerHTML = '<i class="fas fa-exclamation-circle" aria-hidden="true"></i> Please select a time slot before confirming.';
        slotsWrapper?.appendChild(hint);
        hasError = true;
      }

      if (hasError) {
        e.preventDefault();
        return;
      }

      // Loading state on submit button
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner" style="width:18px;height:18px;border-width:2px" role="status"><span class="sr-only">Booking…</span></span> Confirming…';
      }
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     SMOOTH SCROLL
     Respects prefers-reduced-motion. Offsets for fixed navbar.
  ══════════════════════════════════════════════════════════════════════════ */
  const smoothScroll = () => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    qsa('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const href   = a.getAttribute('href');
        if (href === '#') return; // Skip pure anchors
        const target = document.querySelector(href);
        if (!target) return;
        e.preventDefault();

        const navHeight = parseInt(
          getComputedStyle(document.documentElement).getPropertyValue('--nav-height'),
        ) || 72;
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;

        window.scrollTo({ top, behavior: prefersReduced ? 'auto' : 'smooth' });

        // Update URL without triggering scroll
        history.pushState(null, '', href);

        // Move focus to target for accessibility
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      });
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     ANIMATED STAT COUNTERS
     Easing curve for a more polished feel than linear.
  ══════════════════════════════════════════════════════════════════════════ */
  const counterAnimation = () => {
    const counters = qsa('[data-count]');
    if (!counters.length) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Ease-out-expo
    const easeOutExpo = t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t);

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el       = entry.target;
        const target   = parseInt(el.dataset.count, 10);
        const suffix   = el.dataset.suffix || '';
        const duration = 1800;

        if (prefersReduced) {
          el.textContent = target.toLocaleString() + suffix;
          obs.unobserve(el);
          return;
        }

        const start = performance.now();
        const tick  = now => {
          const elapsed  = now - start;
          const progress = Math.min(elapsed / duration, 1);
          const value    = Math.floor(easeOutExpo(progress) * target);
          el.textContent = value.toLocaleString() + suffix;
          if (progress < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        obs.unobserve(el);
      });
    }, { threshold: 0.5, rootMargin: '0px 0px -40px 0px' });

    counters.forEach(c => obs.observe(c));
  };

  /* ══════════════════════════════════════════════════════════════════════════
     PASSWORD VISIBILITY TOGGLE
  ══════════════════════════════════════════════════════════════════════════ */
  const passwordToggle = () => {
    qsa('[data-password-toggle]').forEach(btn => {
      const input = document.getElementById(btn.dataset.passwordToggle);
      if (!input) return;

      btn.setAttribute('aria-label', 'Show password');
      btn.addEventListener('click', () => {
        const show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        btn.querySelector('i')?.classList.toggle('fa-eye',      !show);
        btn.querySelector('i')?.classList.toggle('fa-eye-slash', show);
        btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
        btn.setAttribute('aria-pressed', show.toString());
      });
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     SCROLL REVEAL
     Supplements AOS for [data-reveal] elements. Respects reduced motion.
  ══════════════════════════════════════════════════════════════════════════ */
  const scrollReveal = () => {
    const targets        = qsa('[data-reveal]');
    if (!targets.length) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      targets.forEach(el => el.classList.add('animate-on-scroll'));
      return;
    }

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const delay = entry.target.dataset.revealDelay || 0;
        setTimeout(() => entry.target.classList.add('animate-on-scroll'), parseInt(delay));
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -30px 0px' });

    targets.forEach(el => obs.observe(el));
  };

  /* ══════════════════════════════════════════════════════════════════════════
     STAGGERED CHILDREN REVEAL
     Adds sequential delay to direct children of [data-stagger] containers.
  ══════════════════════════════════════════════════════════════════════════ */
  const staggerReveal = () => {
    const containers = qsa('[data-stagger]');
    if (!containers.length) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const children = Array.from(entry.target.children);
        const base     = parseInt(entry.target.dataset.staggerBase || 0);
        const step     = parseInt(entry.target.dataset.staggerStep || 80);

        children.forEach((child, i) => {
          if (prefersReduced) {
            child.style.opacity   = '1';
            child.style.transform = 'none';
          } else {
            child.style.opacity          = '0';
            child.style.transform        = 'translateY(20px)';
            child.style.transition       = `opacity 0.5s ease ${base + i * step}ms, transform 0.5s ease ${base + i * step}ms`;
            requestAnimationFrame(() => {
              child.style.opacity   = '1';
              child.style.transform = 'translateY(0)';
            });
          }
        });
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.1 });

    containers.forEach(c => obs.observe(c));
  };

  /* ══════════════════════════════════════════════════════════════════════════
     SCROLL-TO-TOP BUTTON
     Shows after scrolling 400px. Auto-injects the button if not in HTML.
  ══════════════════════════════════════════════════════════════════════════ */
  const scrollToTop = () => {
    let btn = document.getElementById('scrollTopBtn');
    if (!btn) {
      btn = document.createElement('button');
      btn.id        = 'scrollTopBtn';
      btn.className = 'scroll-top-btn';
      btn.setAttribute('aria-label', 'Back to top');
      btn.innerHTML = '<i class="fas fa-chevron-up" aria-hidden="true"></i>';
      document.body.appendChild(btn);

      // Inject minimal styles via CSS variable tokens
      const style = document.createElement('style');
      style.textContent = `
        .scroll-top-btn {
          position: fixed;
          bottom: calc(var(--space-8, 2rem) + 70px);
          right: var(--space-8, 2rem);
          z-index: 490;
          width: 44px; height: 44px;
          border-radius: var(--radius-full, 9999px);
          background: var(--gold, #C9A84C);
          color: #1A1208;
          border: none;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 4px 16px rgba(201,168,76,0.35);
          opacity: 0;
          transform: translateY(12px);
          transition: opacity 0.3s ease, transform 0.3s ease, background 0.2s ease;
          pointer-events: none;
          font-size: 0.875rem;
        }
        .scroll-top-btn.visible {
          opacity: 1;
          transform: translateY(0);
          pointer-events: all;
        }
        .scroll-top-btn:hover {
          background: var(--gold-dark, #A07832);
          transform: translateY(-2px);
        }
        @media (max-width: 640px) {
          .scroll-top-btn {
            bottom: calc(var(--space-5, 1.25rem) + 70px);
            right: var(--space-5, 1.25rem);
          }
        }
      `;
      document.head.appendChild(style);
    }

    const onScroll = debounce(() => {
      btn.classList.toggle('visible', window.scrollY > 400);
    }, 80);

    window.addEventListener('scroll', onScroll, { passive: true });
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      document.querySelector('h1, [data-skip-target]')?.focus?.({ preventScroll: true });
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     STICKY MOBILE BOOKING CTA
     Shows a fixed bottom bar on mobile when the hero CTA scrolls out of view.
  ══════════════════════════════════════════════════════════════════════════ */
  const stickyBookingCta = () => {
    const heroCta = qs('.hero__actions .btn--primary');
    if (!heroCta) return;

    const bar = document.createElement('div');
    bar.id        = 'stickyBookingBar';
    bar.className = 'sticky-booking-bar';
    bar.setAttribute('aria-hidden', 'true');

    const bookingHref = heroCta.getAttribute('href') || '/bookings/';
    bar.innerHTML = `
      <a href="${bookingHref}" class="btn btn--primary btn--full" tabindex="-1">
        <i class="fas fa-calendar-check" aria-hidden="true"></i> Book Appointment
      </a>`;
    document.body.appendChild(bar);

    const style = document.createElement('style');
    style.textContent = `
      .sticky-booking-bar {
        display: none;
        position: fixed;
        bottom: 0; left: 0; right: 0;
        z-index: 480;
        padding: 0.75rem 1rem;
        background: var(--bg-overlay, rgba(250,249,245,0.97));
        border-top: 1px solid var(--border-color, #EDE8DF);
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        box-shadow: 0 -4px 24px rgba(0,0,0,0.07);
        transform: translateY(100%);
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .sticky-booking-bar.visible {
        transform: translateY(0);
      }
      @media (min-width: 640px) {
        .sticky-booking-bar { display: none !important; }
      }
      @media (max-width: 639px) {
        .sticky-booking-bar { display: block; }
      }
    `;
    document.head.appendChild(style);

    const obs = new IntersectionObserver(([entry]) => {
      const show = !entry.isIntersecting;
      bar.classList.toggle('visible', show);
      bar.setAttribute('aria-hidden', (!show).toString());
      bar.querySelector('a')?.setAttribute('tabindex', show ? '0' : '-1');
    }, { threshold: 0.1 });

    obs.observe(heroCta);
  };

  /* ══════════════════════════════════════════════════════════════════════════
     HERO PARALLAX
     Subtle depth effect on the hero background image. Throttled via rAF.
  ══════════════════════════════════════════════════════════════════════════ */
  const heroParallax = () => {
    const heroBg = qs('.hero__bg img');
    if (!heroBg) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        const hero    = qs('.hero');
        if (!hero) { ticking = false; return; }
        const heroH   = hero.offsetHeight;
        if (scrollY > heroH) { ticking = false; return; }
        // Move bg at 30% scroll speed (subtle)
        heroBg.style.transform = `translateY(${scrollY * 0.3}px) scale(1.05)`;
        ticking = false;
      });
    };

    window.addEventListener('scroll', onScroll, { passive: true });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     PROMO BANNER DISMISS
     Remembers dismiss state in sessionStorage.
  ══════════════════════════════════════════════════════════════════════════ */
  const promoBanner = () => {
    const banner    = qs('.promo-banner');
    const dismissBtn = qs('.promo-banner__dismiss');
    if (!banner || !dismissBtn) return;

    if (sessionStorage.getItem('promoDismissed')) {
      banner.style.display = 'none';
      return;
    }

    dismissBtn.addEventListener('click', () => {
      banner.style.transition = 'max-height 0.3s ease, opacity 0.3s ease';
      banner.style.maxHeight  = banner.offsetHeight + 'px';
      requestAnimationFrame(() => {
        banner.style.maxHeight = '0';
        banner.style.opacity   = '0';
        banner.style.overflow  = 'hidden';
      });
      setTimeout(() => banner.remove(), 350);
      sessionStorage.setItem('promoDismissed', '1');
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     FORM INLINE VALIDATION
     Real-time validation with accessible error messages.
  ══════════════════════════════════════════════════════════════════════════ */
  const formValidation = () => {
    qsa('.form-control[required]').forEach(field => {
      const errorId  = `error-${field.name || field.id || Math.random().toString(36).slice(2)}`;
      field.setAttribute('aria-describedby',
        [field.getAttribute('aria-describedby'), errorId].filter(Boolean).join(' '));

      // Create or find error container
      let errorEl = qs(`#${errorId}`, field.parentElement);
      if (!errorEl) {
        errorEl = document.createElement('span');
        errorEl.id        = errorId;
        errorEl.className = 'form-error';
        errorEl.setAttribute('role', 'alert');
        errorEl.setAttribute('aria-live', 'polite');
        field.parentElement.appendChild(errorEl);
      }

      const validate = () => {
        const valid = field.checkValidity();
        field.classList.toggle('form-control--error', !valid);
        errorEl.textContent = valid ? '' : (field.validationMessage || 'This field is required.');
        return valid;
      };

      field.addEventListener('blur',  validate);
      field.addEventListener('input', debounce(() => {
        if (field.classList.contains('form-control--error')) validate();
      }, 400));
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     COOKIE HELPER (for CSRF)
  ══════════════════════════════════════════════════════════════════════════ */
  const getCookie = name => {
    const match = document.cookie.match(new RegExp(`(^|;\\s*)${name}=([^;]*)`));
    return match ? decodeURIComponent(match[2]) : null;
  };

  /* ══════════════════════════════════════════════════════════════════════════
     IMAGE LAZY-LOAD ENHANCEMENT
     Adds fade-in when native lazy images load (supplements browser default).
  ══════════════════════════════════════════════════════════════════════════ */
  const lazyImageFade = () => {
    qsa('img[loading="lazy"]').forEach(img => {
      if (img.complete) return;
      img.style.opacity    = '0';
      img.style.transition = 'opacity 0.4s ease';
      img.addEventListener('load', () => { img.style.opacity = '1'; }, { once: true });
    });
  };

  /* ══════════════════════════════════════════════════════════════════════════
     INIT — run all modules
  ══════════════════════════════════════════════════════════════════════════ */
  const init = () => {
    carousel();
    lightbox();
    faq();
    galleryFilter();
    serviceTabs();
    bookingFlow();
    smoothScroll();
    counterAnimation();
    passwordToggle();
    scrollReveal();
    staggerReveal();
    scrollToTop();
    stickyBookingCta();
    heroParallax();
    promoBanner();
    formValidation();
    lazyImageFade();
  };

  // Fire after DOM is ready
  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();

  /* Expose only what external scripts / Django templates may need */
  return { init };

})();