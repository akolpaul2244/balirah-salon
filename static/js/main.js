const Balirah = (() => {
  const navbar = () => {
    const nav = document.getElementById('navbar');
    if (!nav) return;
    const hamburger = nav.querySelector('.navbar__hamburger');
    const mobile = document.getElementById('mobileMenu');

    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 30);
    }, { passive: true });

    if (hamburger && mobile) {
      hamburger.addEventListener('click', () => {
        const open = hamburger.classList.toggle('open');
        mobile.classList.toggle('open', open);
        document.body.style.overflow = open ? 'hidden' : '';
        hamburger.setAttribute('aria-expanded', open);
      });
      mobile.querySelectorAll('.navbar__mobile-link').forEach(link => {
        link.addEventListener('click', () => {
          hamburger.classList.remove('open');
          mobile.classList.remove('open');
          document.body.style.overflow = '';
        });
      });
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && mobile.classList.contains('open')) {
          hamburger.classList.remove('open');
          mobile.classList.remove('open');
          document.body.style.overflow = '';
        }
      });
    }

    const currentPath = window.location.pathname;
    nav.querySelectorAll('.navbar__link').forEach(link => {
      const href = link.getAttribute('href');
      if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
        link.classList.add('active');
      }
    });
  };

  const carousel = () => {
    document.querySelectorAll('[data-carousel]').forEach(wrapper => {
      const track = wrapper.querySelector('.testimonials-track');
      const dots = wrapper.querySelectorAll('.carousel-dot');
      const prevBtn = wrapper.querySelector('[data-carousel-prev]');
      const nextBtn = wrapper.querySelector('[data-carousel-next]');
      if (!track) return;

      const items = track.querySelectorAll('.testimonial-card');
      let current = 0;
      let autoTimer;

      const go = idx => {
        current = (idx + items.length) % items.length;
        track.style.transform = `translateX(-${current * 100}%)`;
        dots.forEach((d, i) => d.classList.toggle('active', i === current));
      };

      const startAuto = () => {
        clearInterval(autoTimer);
        autoTimer = setInterval(() => go(current + 1), 5000);
      };

      dots.forEach((dot, i) => dot.addEventListener('click', () => { go(i); startAuto(); }));
      if (prevBtn) prevBtn.addEventListener('click', () => { go(current - 1); startAuto(); });
      if (nextBtn) nextBtn.addEventListener('click', () => { go(current + 1); startAuto(); });

      let startX = 0;
      track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
      track.addEventListener('touchend', e => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) { go(diff > 0 ? current + 1 : current - 1); startAuto(); }
      });

      go(0);
      startAuto();

      wrapper.addEventListener('mouseenter', () => clearInterval(autoTimer));
      wrapper.addEventListener('mouseleave', startAuto);
    });
  };

  const lightbox = () => {
    const box = document.getElementById('lightbox');
    if (!box) return;

    const img = box.querySelector('.lightbox__img');
    const items = Array.from(document.querySelectorAll('[data-lightbox]'));
    let current = 0;

    const open = idx => {
      current = idx;
      img.src = items[idx].dataset.lightbox;
      img.alt = items[idx].dataset.title || '';
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
      img.focus();
    };

    const close = () => {
      box.classList.remove('open');
      document.body.style.overflow = '';
    };

    const nav = dir => {
      current = (current + dir + items.length) % items.length;
      img.style.opacity = '0';
      setTimeout(() => {
        img.src = items[current].dataset.lightbox;
        img.style.opacity = '1';
      }, 150);
    };

    items.forEach((el, i) => {
      el.addEventListener('click', e => { e.preventDefault(); open(i); });
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') open(i); });
    });

    box.querySelector('.lightbox__close')?.addEventListener('click', close);
    box.querySelector('.lightbox__prev')?.addEventListener('click', () => nav(-1));
    box.querySelector('.lightbox__next')?.addEventListener('click', () => nav(1));
    box.addEventListener('click', e => { if (e.target === box) close(); });
    document.addEventListener('keydown', e => {
      if (!box.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') nav(-1);
      if (e.key === 'ArrowRight') nav(1);
    });
  };

  const faq = () => {
    document.querySelectorAll('.faq-item').forEach(item => {
      const question = item.querySelector('.faq-question');
      if (!question) return;
      question.setAttribute('role', 'button');
      question.setAttribute('tabindex', '0');
      question.setAttribute('aria-expanded', 'false');
      const toggle = () => {
        const open = item.classList.toggle('open');
        question.setAttribute('aria-expanded', open);
      };
      question.addEventListener('click', toggle);
      question.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
    });
  };

  const galleryFilter = () => {
    const filters = document.querySelectorAll('.gallery-filter');
    const items = document.querySelectorAll('.gallery-item');
    if (!filters.length) return;

    filters.forEach(btn => {
      btn.addEventListener('click', () => {
        filters.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.dataset.filter;
        items.forEach(item => {
          const match = cat === 'all' || item.dataset.category === cat;
          item.style.display = match ? '' : 'none';
          if (match) item.style.animation = 'fadeIn 0.3s ease';
        });
      });
    });
  };

  const serviceTabs = () => {
    const tabs = document.querySelectorAll('.service-tab');
    const panels = document.querySelectorAll('.service-panel');
    if (!tabs.length) return;

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
        panels.forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        const target = document.getElementById(tab.dataset.tab);
        if (target) target.classList.add('active');
      });
    });
  };

  const bookingFlow = () => {
    const form = document.getElementById('bookingForm');
    if (!form) return;

    const serviceSelect = form.querySelector('[name="service"]');
    const stylistSelect = form.querySelector('[name="stylist"]');
    const dateInput = form.querySelector('[name="appointment_date"]');
    const slotsWrapper = document.getElementById('slotsWrapper');
    const slotInput = form.querySelector('[name="time_slot"]');
    const summaryService = document.getElementById('summaryService');
    const summaryStylist = document.getElementById('summaryStylist');
    const summaryDate = document.getElementById('summaryDate');
    const summaryTime = document.getElementById('summaryTime');
    const summaryPrice = document.getElementById('summaryPrice');
    const summaryDuration = document.getElementById('summaryDuration');

    const today = new Date().toISOString().split('T')[0];
    if (dateInput) {
      dateInput.min = today;
      const maxDate = new Date();
      maxDate.setDate(maxDate.getDate() + 30);
      dateInput.max = maxDate.toISOString().split('T')[0];
    }

    const fetchSlots = async () => {
      const service = serviceSelect?.value;
      const date = dateInput?.value;
      const stylist = stylistSelect?.value;
      if (!service || !date || !slotsWrapper) return;

      slotsWrapper.innerHTML = '<div class="flex-center" style="padding:2rem"><div class="spinner"></div></div>';
      slotInput.value = '';

      try {
        const params = new URLSearchParams({ service, date });
        if (stylist) params.append('stylist', stylist);
        const res = await fetch(`/bookings/api/slots/?${params}`);
        const data = await res.json();
        renderSlots(data.slots || []);
      } catch {
        slotsWrapper.innerHTML = '<p style="color:var(--error);font-size:.875rem;padding:.5rem 0">Could not load time slots. Please try again.</p>';
      }
    };

    const renderSlots = slots => {
      if (!slotsWrapper) return;
      if (!slots.length) {
        slotsWrapper.innerHTML = '<p style="color:var(--grey-400);font-size:.875rem;padding:.5rem 0">No available slots for this date. Please choose another date.</p>';
        return;
      }
      slotsWrapper.innerHTML = '<div class="slots-grid"></div>';
      const grid = slotsWrapper.querySelector('.slots-grid');
      slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'slot-btn';
        btn.textContent = slot.start;
        btn.dataset.slotId = slot.id || slot.start;
        btn.dataset.time = slot.start;
        btn.addEventListener('click', () => {
          slotsWrapper.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          slotInput.value = slot.id || slot.start;
          if (summaryTime) summaryTime.textContent = slot.start;
          updateStep(3);
        });
        grid.appendChild(btn);
      });
    };

    const updateSummary = () => {
      if (summaryService && serviceSelect) {
        const opt = serviceSelect.options[serviceSelect.selectedIndex];
        if (opt && opt.value) {
          summaryService.textContent = opt.text;
          if (summaryPrice) summaryPrice.textContent = opt.dataset.price || '';
          if (summaryDuration) summaryDuration.textContent = opt.dataset.duration || '';
        }
      }
      if (summaryStylist && stylistSelect) {
        const opt = stylistSelect.options[stylistSelect.selectedIndex];
        summaryStylist.textContent = opt && opt.value ? opt.text : 'Any Available';
      }
      if (summaryDate && dateInput?.value) {
        const d = new Date(dateInput.value + 'T00:00:00');
        summaryDate.textContent = d.toLocaleDateString('en-UG', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
      }
    };

    const updateStep = n => {
      document.querySelectorAll('.booking-step').forEach((s, i) => {
        s.classList.toggle('active', i + 1 === n);
        s.classList.toggle('completed', i + 1 < n);
      });
      document.querySelectorAll('.booking-step-connector').forEach((c, i) => {
        c.classList.toggle('completed', i + 1 < n);
      });
    };

    serviceSelect?.addEventListener('change', () => { updateSummary(); fetchSlots(); updateStep(2); });
    stylistSelect?.addEventListener('change', () => { updateSummary(); fetchSlots(); });
    dateInput?.addEventListener('change', () => { updateSummary(); fetchSlots(); updateStep(2); });

    form.addEventListener('submit', e => {
      if (!slotInput?.value) {
        e.preventDefault();
        slotsWrapper?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const hint = document.createElement('p');
        hint.className = 'form-error';
        hint.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please select a time slot.';
        if (!slotsWrapper?.querySelector('.form-error')) slotsWrapper?.appendChild(hint);
      }
    });
  };

  const csrfSetup = () => {
    const getCsrf = () => document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
    document.querySelectorAll('form[method="post"]').forEach(form => {
      if (!form.querySelector('[name=csrfmiddlewaretoken]')) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = getCsrf();
        form.prepend(input);
      }
    });
  };

  const smoothScroll = () => {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
          e.preventDefault();
          const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-height')) || 72;
          const top = target.getBoundingClientRect().top + window.scrollY - offset - 16;
          window.scrollTo({ top, behavior: 'smooth' });
        }
      });
    });
  };

  const counterAnimation = () => {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count);
        const duration = 1500;
        const step = target / (duration / 16);
        let current = 0;
        const tick = () => {
          current = Math.min(current + step, target);
          el.textContent = Math.floor(current).toLocaleString() + (el.dataset.suffix || '');
          if (current < target) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        obs.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(c => obs.observe(c));
  };

  const passwordToggle = () => {
    document.querySelectorAll('[data-password-toggle]').forEach(btn => {
      const input = document.getElementById(btn.dataset.passwordToggle);
      if (!input) return;
      btn.addEventListener('click', () => {
        const show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        btn.querySelector('i')?.classList.toggle('fa-eye', !show);
        btn.querySelector('i')?.classList.toggle('fa-eye-slash', show);
        btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      });
    });
  };

  const init = () => {
    navbar();
    carousel();
    lightbox();
    faq();
    galleryFilter();
    serviceTabs();
    bookingFlow();
    smoothScroll();
    counterAnimation();
    passwordToggle();
  };

  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();

  return { navbar, fetchSlots: bookingFlow };
})();
