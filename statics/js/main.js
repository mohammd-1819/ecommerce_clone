/**
 * =========================================================
 * NEW DANIDOR — MAIN JS
 * Persian RTL Coffee / Hot Chocolate Store
 *
 * Static path:
 * static/js/main.js
 *
 * Purpose:
 * - Header scroll behavior
 * - Mobile menu
 * - Hero slider, 3 second autoplay
 * - Slider dots and arrows
 * - Scroll reveal animation
 * - Quantity controls for future cart/product pages
 * - Product gallery thumbnail switching
 * - FAQ / accordion support for future pages
 *
 * No external libraries.
 * Backend-ready and safe for static Django templates.
 * =========================================================
 */

(function () {
  "use strict";

  const SELECTORS = {
    header: ".site-header",

    menuOpen: "[data-menu-open]",
    menuClose: "[data-menu-close]",
    mobileMenu: "[data-mobile-menu]",
    mobileOverlay: "[data-mobile-overlay]",

    hero: "[data-hero-slider]",
    slide: "[data-hero-slide]",
    dot: "[data-hero-dot]",
    prev: "[data-hero-prev]",
    next: "[data-hero-next]",

    reveal: ".reveal",

    quantity: "[data-quantity]",
    quantityInput: "[data-quantity-input]",
    quantityIncrease: "[data-quantity-increase]",
    quantityDecrease: "[data-quantity-decrease]",

    productGallery: "[data-product-gallery]",
    productMainImage: "[data-product-main-image]",
    productThumb: "[data-product-thumb]",

    accordion: "[data-accordion]",
    accordionTrigger: "[data-accordion-trigger]",
    accordionPanel: "[data-accordion-panel]",

    searchOpen: "[data-search-open]",
    searchClose: "[data-search-close]",
    searchOverlay: "[data-search-overlay]",
    searchInput: "[data-search-input]"
  };

  const CLASS_NAMES = {
    scrolled: "is-scrolled",
    active: "is-active",
    visible: "is-visible",
    menuOpen: "menu-open"
  };

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function ready(callback) {
    if (document.readyState !== "loading") {
      callback();
      return;
    }

    document.addEventListener("DOMContentLoaded", callback);
  }

  function $all(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
  }

  function $(selector, parent = document) {
    return parent.querySelector(selector);
  }

  function initHeaderScroll() {
    const header = $(SELECTORS.header);

    if (!header) return;

    const updateHeader = () => {
      if (window.scrollY > 16) {
        header.classList.add(CLASS_NAMES.scrolled);
      } else {
        header.classList.remove(CLASS_NAMES.scrolled);
      }
    };

    updateHeader();

    window.addEventListener("scroll", updateHeader, { passive: true });
  }

  function initMobileMenu() {
    const openButtons = $all(SELECTORS.menuOpen);
    const closeButtons = $all(SELECTORS.menuClose);
    const menu = $(SELECTORS.mobileMenu);
    const overlay = $(SELECTORS.mobileOverlay);

    if (!menu || !overlay || openButtons.length === 0) return;

    let lastFocusedElement = null;

    const focusableSelector = [
      "a[href]",
      "button:not([disabled])",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      "[tabindex]:not([tabindex='-1'])"
    ].join(",");

    const getFocusableElements = () => $all(focusableSelector, menu);

    const setOpenButtonState = (state) => {
      openButtons.forEach((button) => {
        button.setAttribute("aria-expanded", state ? "true" : "false");
      });
    };

    const openMenu = () => {
      lastFocusedElement = document.activeElement;

      menu.classList.add(CLASS_NAMES.active);
      overlay.classList.add(CLASS_NAMES.active);
      document.body.classList.add(CLASS_NAMES.menuOpen);

      menu.setAttribute("aria-hidden", "false");
      overlay.setAttribute("aria-hidden", "false");
      setOpenButtonState(true);

      const focusable = getFocusableElements();
      if (focusable.length > 0) {
        focusable[0].focus();
      }
    };

    const closeMenu = () => {
      menu.classList.remove(CLASS_NAMES.active);
      overlay.classList.remove(CLASS_NAMES.active);
      document.body.classList.remove(CLASS_NAMES.menuOpen);

      menu.setAttribute("aria-hidden", "true");
      overlay.setAttribute("aria-hidden", "true");
      setOpenButtonState(false);

      if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
        lastFocusedElement.focus();
      }
    };

    const trapFocus = (event) => {
      if (!menu.classList.contains(CLASS_NAMES.active)) return;
      if (event.key !== "Tab") return;

      const focusable = getFocusableElements();
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      }

      if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    openButtons.forEach((button) => {
      button.addEventListener("click", openMenu);
      button.setAttribute("aria-expanded", "false");
    });

    closeButtons.forEach((button) => {
      button.addEventListener("click", closeMenu);
    });

    overlay.addEventListener("click", closeMenu);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.classList.contains(CLASS_NAMES.active)) {
        closeMenu();
      }

      trapFocus(event);
    });

    $all("a", menu).forEach((link) => {
      link.addEventListener("click", closeMenu);
    });
  }

  function initHeroSlider() {
    const slider = $(SELECTORS.hero);

    if (!slider) return;

    const slides = $all(SELECTORS.slide, slider);
    const dots = $all(SELECTORS.dot, slider);
    const prevButton = $(SELECTORS.prev, slider);
    const nextButton = $(SELECTORS.next, slider);

    if (slides.length <= 1) {
      if (slides[0]) {
        slides[0].classList.add(CLASS_NAMES.active);
        slides[0].setAttribute("aria-hidden", "false");
      }

      return;
    }

    let currentIndex = slides.findIndex((slide) => slide.classList.contains(CLASS_NAMES.active));
    let autoplayId = null;

    if (currentIndex < 0) currentIndex = 0;

    function updateSlider(nextIndex) {
      const safeIndex = (nextIndex + slides.length) % slides.length;

      slides.forEach((slide, index) => {
        const isActive = index === safeIndex;

        slide.classList.toggle(CLASS_NAMES.active, isActive);
        slide.setAttribute("aria-hidden", isActive ? "false" : "true");
      });

      dots.forEach((dot, index) => {
        const isActive = index === safeIndex;

        dot.classList.toggle(CLASS_NAMES.active, isActive);
        dot.setAttribute("aria-selected", isActive ? "true" : "false");
        dot.setAttribute("tabindex", isActive ? "0" : "-1");
      });

      currentIndex = safeIndex;
    }

    function goNext() {
      updateSlider(currentIndex + 1);
    }

    function goPrev() {
      updateSlider(currentIndex - 1);
    }

    function startAutoplay() {
      if (prefersReducedMotion) return;

      stopAutoplay();
      autoplayId = window.setInterval(goNext, 3000);
    }

    function stopAutoplay() {
      if (autoplayId) {
        window.clearInterval(autoplayId);
        autoplayId = null;
      }
    }

    dots.forEach((dot, index) => {
      dot.addEventListener("click", () => {
        updateSlider(index);
        startAutoplay();
      });

      dot.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          updateSlider(index);
          startAutoplay();
        }
      });
    });

    if (nextButton) {
      nextButton.addEventListener("click", () => {
        goNext();
        startAutoplay();
      });
    }

    if (prevButton) {
      prevButton.addEventListener("click", () => {
        goPrev();
        startAutoplay();
      });
    }

    slider.addEventListener("mouseenter", stopAutoplay);
    slider.addEventListener("mouseleave", startAutoplay);
    slider.addEventListener("focusin", stopAutoplay);
    slider.addEventListener("focusout", startAutoplay);

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopAutoplay();
      } else {
        startAutoplay();
      }
    });

    updateSlider(currentIndex);
    startAutoplay();
  }

  function initReveal() {
    const revealItems = $all(SELECTORS.reveal);

    if (revealItems.length === 0) return;

    if (!("IntersectionObserver" in window) || prefersReducedMotion) {
      revealItems.forEach((item) => item.classList.add(CLASS_NAMES.visible));
      return;
    }

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          entry.target.classList.add(CLASS_NAMES.visible);
          obs.unobserve(entry.target);
        });
      },
      {
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px"
      }
    );

    revealItems.forEach((item) => observer.observe(item));
  }

  function initQuantityControls() {
    const quantityGroups = $all(SELECTORS.quantity);

    quantityGroups.forEach((group) => {
      const input = $(SELECTORS.quantityInput, group);
      const increase = $(SELECTORS.quantityIncrease, group);
      const decrease = $(SELECTORS.quantityDecrease, group);

      if (!input) return;

      const min = Number(input.getAttribute("min")) || 1;
      const maxAttr = input.getAttribute("max");
      const max = maxAttr ? Number(maxAttr) : Infinity;

      const normalizeValue = (value) => {
        const number = Number(value);

        if (Number.isNaN(number)) return min;

        return Math.min(Math.max(number, min), max);
      };

      const setValue = (value) => {
        input.value = String(normalizeValue(value));
        input.dispatchEvent(new Event("change", { bubbles: true }));
      };

      if (increase) {
        increase.addEventListener("click", () => {
          setValue(normalizeValue(input.value) + 1);
        });
      }

      if (decrease) {
        decrease.addEventListener("click", () => {
          setValue(normalizeValue(input.value) - 1);
        });
      }

      input.addEventListener("change", () => {
        setValue(input.value);
      });
    });
  }

  function initProductGallery() {
    const galleries = $all(SELECTORS.productGallery);

    galleries.forEach((gallery) => {
      const mainImage = $(SELECTORS.productMainImage, gallery);
      const thumbs = $all(SELECTORS.productThumb, gallery);

      if (!mainImage || thumbs.length === 0) return;

      thumbs.forEach((thumb) => {
        thumb.addEventListener("click", () => {
          const newSrc = thumb.getAttribute("data-image-src");
          const newAlt = thumb.getAttribute("data-image-alt");

          if (newSrc) {
            mainImage.setAttribute("src", newSrc);
          }

          if (newAlt) {
            mainImage.setAttribute("alt", newAlt);
          }

          thumbs.forEach((item) => item.classList.remove(CLASS_NAMES.active));
          thumb.classList.add(CLASS_NAMES.active);
        });
      });
    });
  }

  function initAccordions() {
    const accordions = $all(SELECTORS.accordion);

    accordions.forEach((accordion) => {
      const trigger = $(SELECTORS.accordionTrigger, accordion);
      const panel = $(SELECTORS.accordionPanel, accordion);

      if (!trigger || !panel) return;

      const isInitiallyActive = accordion.classList.contains(CLASS_NAMES.active);

      trigger.setAttribute("aria-expanded", isInitiallyActive ? "true" : "false");
      panel.hidden = !isInitiallyActive;

      trigger.addEventListener("click", () => {
        const isActive = accordion.classList.toggle(CLASS_NAMES.active);

        trigger.setAttribute("aria-expanded", isActive ? "true" : "false");
        panel.hidden = !isActive;
      });
    });
  }

  function initSearchOverlay() {
    const openButtons = $all(SELECTORS.searchOpen);
    const closeButtons = $all(SELECTORS.searchClose);
    const overlay = $(SELECTORS.searchOverlay);
    const input = $(SELECTORS.searchInput);

    if (!overlay || openButtons.length === 0) return;

    let lastFocusedElement = null;

    const openSearch = () => {
      lastFocusedElement = document.activeElement;

      overlay.classList.add(CLASS_NAMES.active);
      overlay.setAttribute("aria-hidden", "false");
      document.body.classList.add(CLASS_NAMES.menuOpen);

      if (input) {
        window.setTimeout(() => input.focus(), 80);
      }
    };

    const closeSearch = () => {
      overlay.classList.remove(CLASS_NAMES.active);
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove(CLASS_NAMES.menuOpen);

      if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
        lastFocusedElement.focus();
      }
    };

    openButtons.forEach((button) => {
      button.addEventListener("click", openSearch);
    });

    closeButtons.forEach((button) => {
      button.addEventListener("click", closeSearch);
    });

    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        closeSearch();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && overlay.classList.contains(CLASS_NAMES.active)) {
        closeSearch();
      }
    });
  }

  function initCurrentYear() {
    const yearItems = $all("[data-current-year]");
    const year = new Date().getFullYear();

    yearItems.forEach((item) => {
      item.textContent = String(year);
    });
  }

  ready(function () {
    initHeaderScroll();
    initMobileMenu();
    initHeroSlider();
    initReveal();
    initQuantityControls();
    initProductGallery();
    initAccordions();
    initSearchOverlay();
    initCurrentYear();
  });
})();