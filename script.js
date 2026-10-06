/**
 * Latchya.R - Personal Portfolio Website Script
 * Minimal, modern, and performant vanilla JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initMobileDrawer();
  initScrollSpy();
  initAiCanvas();
  initContactForm();
  initResumeModal();
  initCertLightbox();
  initBackToTop();
});

/* ==========================================================================
   1. NAVBAR SCROLL EFFECT
   ========================================================================== */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  const handleScroll = () => {
    if (window.scrollY > 30) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/* ==========================================================================
   2. MOBILE DRAWER MENU
   ========================================================================== */
function initMobileDrawer() {
  const mobileToggle = document.getElementById('mobileToggle');
  const closeDrawer = document.getElementById('closeDrawer');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link');

  if (!mobileToggle || !mobileDrawer || !drawerOverlay) return;

  function openMenu() {
    mobileDrawer.classList.add('open');
    drawerOverlay.classList.add('active');
    mobileToggle.setAttribute('aria-expanded', 'true');
    mobileDrawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    mobileDrawer.classList.remove('open');
    drawerOverlay.classList.remove('active');
    mobileToggle.setAttribute('aria-expanded', 'false');
    mobileDrawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  mobileToggle.addEventListener('click', openMenu);
  if (closeDrawer) closeDrawer.addEventListener('click', closeMenu);
  drawerOverlay.addEventListener('click', closeMenu);

  mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeMenu();
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileDrawer.classList.contains('open')) {
      closeMenu();
    }
  });
}

/* ==========================================================================
   3. SCROLL SPY (ACTIVE NAV LINK HIGHLIGHTING)
   ========================================================================== */
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const desktopLinks = document.querySelectorAll('.nav-link');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link');

  if (sections.length === 0) return;

  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -60% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');

        desktopLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
        });

        mobileLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, observerOptions);

  sections.forEach(sec => observer.observe(sec));
}

/* ==========================================================================
   4. AMBIENT AI NETWORK CANVAS
   ========================================================================== */
function initAiCanvas() {
  const canvas = document.getElementById('network-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let animationFrameId;
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  const particleCount = Math.min(Math.floor((width * height) / 22000), 55);
  const particles = [];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.45;
      this.vy = (Math.random() - 0.5) * 0.45;
      this.radius = Math.random() * 2 + 1.2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0) this.x = width;
      if (this.x > width) this.x = 0;
      if (this.y < 0) this.y = height;
      if (this.y > height) this.y = 0;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(167, 139, 250, 0.45)'; // soft lavender
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Draw connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          const alpha = (1 - dist / 130) * 0.22;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(167, 139, 250, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    // Draw particles
    particles.forEach(p => {
      p.update();
      p.draw();
    });

    animationFrameId = requestAnimationFrame(render);
  }

  render();

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }, { passive: true });
}

/* ==========================================================================
   5. CONTACT FORM VALIDATION & INTERACTION
   ========================================================================== */
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const nameInput = document.getElementById('name');
  const emailInput = document.getElementById('email');
  const messageInput = document.getElementById('message');
  const nameError = document.getElementById('nameError');
  const emailError = document.getElementById('emailError');
  const messageError = document.getElementById('messageError');
  const formAlert = document.getElementById('formAlert');
  const submitBtn = document.getElementById('submitBtn');

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    let isValid = true;

    // Name validation
    if (!nameInput.value.trim()) {
      nameError.classList.add('active');
      nameInput.classList.add('input-error');
      isValid = false;
    } else {
      nameError.classList.remove('active');
      nameInput.classList.remove('input-error');
    }

    // Email validation
    if (!emailInput.value.trim() || !emailRegex.test(emailInput.value.trim())) {
      emailError.classList.add('active');
      emailInput.classList.add('input-error');
      isValid = false;
    } else {
      emailError.classList.remove('active');
      emailInput.classList.remove('input-error');
    }

    // Message validation
    if (!messageInput.value.trim()) {
      messageError.classList.add('active');
      messageInput.classList.add('input-error');
      isValid = false;
    } else {
      messageError.classList.remove('active');
      messageInput.classList.remove('input-error');
    }

    if (isValid) {
      const senderName = nameInput.value.trim();

      // UI Feedback
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Sending...</span>`;

      setTimeout(() => {
        formAlert.className = 'form-alert success';
        formAlert.innerHTML = `✨ Thank you, <strong>${senderName}</strong>! Your message has been noted. You can also reach me directly at <a href="mailto:latchya.r07@gmail.com" style="text-decoration: underline;">latchya.r07@gmail.com</a>.`;
        
        form.reset();
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
          <span>Send Message</span>
          <svg class="btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        `;

        setTimeout(() => {
          formAlert.className = 'form-alert';
          formAlert.innerHTML = '';
        }, 8000);
      }, 700);
    }
  });

  // Clear errors on typing
  [nameInput, emailInput, messageInput].forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('input-error');
      const err = document.getElementById(`${input.id}Error`);
      if (err) err.classList.remove('active');
    });
  });
}

/* ==========================================================================
   6. RESUME MODAL & PRINT HANDLER
   ========================================================================== */
function initResumeModal() {
  const resumeBtn = document.getElementById('resumeBtn');
  const modal = document.getElementById('resumeModal');
  const closeModal = document.getElementById('closeModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const printResumeBtn = document.getElementById('printResumeBtn');

  if (!resumeBtn || !modal) return;

  function openResumeModal() {
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeResumeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  resumeBtn.addEventListener('click', openResumeModal);
  if (closeModal) closeModal.addEventListener('click', closeResumeModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeResumeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeResumeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeResumeModal();
    }
  });

  if (printResumeBtn) {
    printResumeBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

/* ==========================================================================
   7. CERTIFICATE LIGHTBOX MODAL
   ========================================================================== */
function initCertLightbox() {
  const lightbox = document.getElementById('certLightbox');
  const lightboxTitle = document.getElementById('lightboxTitle');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxOpenLink = document.getElementById('lightboxOpenLink');
  const closeLightbox = document.getElementById('closeLightbox');
  const closeLightboxBtn = document.getElementById('closeLightboxBtn');

  if (!lightbox || !lightboxImg) return;

  const triggerElements = document.querySelectorAll('.cert-media-preview, .cert-action-btn');

  function openLightbox(title, imgSrc, linkHref) {
    if (lightboxTitle) lightboxTitle.innerHTML = title || 'Certificate Preview';
    lightboxImg.src = imgSrc || '';
    lightboxImg.alt = title || 'Certificate Full Preview';
    if (lightboxOpenLink) {
      lightboxOpenLink.href = linkHref || imgSrc || '#';
    }

    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightboxModal() {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  triggerElements.forEach(elem => {
    elem.addEventListener('click', (e) => {
      e.stopPropagation();
      const title = elem.getAttribute('data-cert-title');
      const img = elem.getAttribute('data-cert-img');
      const link = elem.getAttribute('data-cert-link');
      openLightbox(title, img, link);
    });
  });

  if (closeLightbox) closeLightbox.addEventListener('click', closeLightboxModal);
  if (closeLightboxBtn) closeLightboxBtn.addEventListener('click', closeLightboxModal);

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightboxModal();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightbox.classList.contains('open')) {
      closeLightboxModal();
    }
  });
}

/* ==========================================================================
   8. BACK TO TOP
   ========================================================================== */
function initBackToTop() {
  const backToTopBtn = document.getElementById('backToTop');
  if (!backToTopBtn) return;

  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}
