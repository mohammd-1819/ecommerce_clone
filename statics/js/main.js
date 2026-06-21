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

    profileMenu: ".profile-menu",
    profileActiveLink: ".profile-menu-link.is-active",

    orderTabsRoot: "[data-order-tabs]",
    orderTab: "[data-order-tab]",
    orderPanel: "[data-order-panel]",

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
    searchInput: "[data-search-input]",

    addressModalOpen: "[data-address-modal-open]",
    addressModalClose: "[data-address-modal-close]",
    addressModal: "[data-address-modal]",
    addressForm: "[data-address-form]",
    addressModalTitle: "[data-address-modal-title]",
    addressSubmitText: "[data-address-submit-text]",
    addressIdInput: "[data-address-id-input]",
    addressField: "[data-address-field]",


    cartPage: "[data-cart-page]",
    cartFilled: "[data-cart-filled]",
    cartEmpty: "[data-cart-empty]",
    cartItems: "[data-cart-items]",
    cartItem: "[data-cart-item]",
    cartRemove: "[data-cart-remove]",
    cartItemTotal: "[data-cart-item-total]",
    cartCountLabel: "[data-cart-count-label]",
    cartSubtotal: "[data-cart-subtotal]",
    cartTax: "[data-cart-tax]",
    cartFinal: "[data-cart-final]",


    checkoutForm: "[data-checkout-form]",
    checkoutChoice: "[data-checkout-choice]",
    checkoutChoiceInput: ".checkout-choice-input",
    checkoutSubmitButton: ".checkout-form button[type='submit']",

    checkoutCoupon: "[data-checkout-coupon]",
    checkoutCouponInput: "[data-checkout-coupon-input]",
    checkoutCouponApply: "[data-checkout-coupon-apply]",
    checkoutCouponMessage: "[data-checkout-coupon-message]",
    checkoutDiscountRow: "[data-checkout-discount-row]",
    checkoutDiscountAmount: "[data-checkout-discount-amount]",
    checkoutFinalTotal: "[data-checkout-final-total]",


    productVariants: "[data-product-variants]",
    variantOption: "[data-variant-option]",
    selectedVariantLabel: "[data-selected-variant-label]",
    selectedVariantInput: "[data-selected-variant-input]",
    selectedWeightAttribute: "[data-selected-weight-attribute]",
    productPrice: "[data-product-price]",
    productStockStatus: "[data-product-stock-status]",
    productUnavailableNote: "[data-product-unavailable-note]",
    addToCartButton: "[data-add-to-cart-button]",

    commentModalOpen: "[data-comment-modal-open]",
    commentModalClose: "[data-comment-modal-close]",
    commentModal: "[data-comment-modal]",
    commentModalOverlay: "[data-comment-modal-overlay]",
    commentForm: "[data-comment-form]",
    commentsList: "[data-comments-list]",
    commentsEmpty: "[data-comments-empty]",
  };

  const CLASS_NAMES = {
    scrolled: "is-scrolled",
    active: "is-active",
    visible: "is-visible",
    menuOpen: "menu-open",
    addressModalOpen: "address-modal-open",
    commentModalOpen: "comment-modal-open"
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

        const notifyQuantityChange = () => {
          input.dispatchEvent(new Event("input", { bubbles: true }));
        };

        const setValue = (value) => {
          input.value = String(normalizeValue(value));
          notifyQuantityChange();
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
          input.value = String(normalizeValue(input.value));
          notifyQuantityChange();
        });
      });
    }


  function initCartPage() {
    const cartPage = $(SELECTORS.cartPage);

    if (!cartPage) return;

    const filledState = $(SELECTORS.cartFilled, cartPage);
    const emptyState = $(SELECTORS.cartEmpty, cartPage);
    const itemsWrapper = $(SELECTORS.cartItems, cartPage);
    const countLabel = $(SELECTORS.cartCountLabel, cartPage);
    const subtotalEl = $(SELECTORS.cartSubtotal, cartPage);
    const taxEl = $(SELECTORS.cartTax, cartPage);
    const finalEl = $(SELECTORS.cartFinal, cartPage);
    const summaryCount = $(".cart-summary-head span", cartPage);

    if (!itemsWrapper) return;

    const TAX_RATE = 0.1;

    const formatNumberFa = (number) => {
      return new Intl.NumberFormat("fa-IR").format(Math.round(number));
    };

    const formatMoneyFa = (number) => {
      return `${formatNumberFa(number)} تومان`;
    };

    const getCartItems = () => {
      return $all(SELECTORS.cartItem, itemsWrapper);
    };

    const getQuantityInput = (item) => {
      return $(SELECTORS.quantityInput, item);
    };

    const getQuantityValue = (item) => {
      const input = getQuantityInput(item);
      const value = input ? Number(input.value) : 1;

      if (Number.isNaN(value) || value < 1) return 1;

      return value;
    };

    const getUnitPrice = (item) => {
      const price = Number(item.getAttribute("data-price"));

      if (Number.isNaN(price)) return 0;

      return price;
    };

    const updateEmptyState = (itemCount) => {
      const isEmpty = itemCount === 0;

      if (filledState) {
        filledState.classList.toggle("hidden", isEmpty);
      }

      if (emptyState) {
        emptyState.classList.toggle("hidden", !isEmpty);
      }
    };

    const updateCountLabels = (itemCount) => {
      const labelText = `${formatNumberFa(itemCount)} کالا`;

      if (countLabel) {
        countLabel.textContent = labelText;
      }

      if (summaryCount) {
        summaryCount.textContent = labelText;
      }
    };

    const updateTotals = () => {
      const items = getCartItems();

      let subtotal = 0;

      items.forEach((item) => {
        const unitPrice = getUnitPrice(item);
        const quantity = getQuantityValue(item);
        const itemTotal = unitPrice * quantity;
        const itemTotalEl = $(SELECTORS.cartItemTotal, item);

        subtotal += itemTotal;

        if (itemTotalEl) {
          itemTotalEl.textContent = formatMoneyFa(itemTotal);
        }
      });

      const tax = subtotal * TAX_RATE;
      const finalTotal = subtotal + tax;

      if (subtotalEl) {
        subtotalEl.textContent = formatMoneyFa(subtotal);
      }

      if (taxEl) {
        taxEl.textContent = formatMoneyFa(tax);
      }

      if (finalEl) {
        finalEl.textContent = formatMoneyFa(finalTotal);
      }

      updateCountLabels(items.length);
      updateEmptyState(items.length);
    };

    const removeCartItem = (item) => {
      item.style.transition = "opacity 180ms ease, transform 180ms ease";
      item.style.opacity = "0";
      item.style.transform = "translateY(8px)";

      window.setTimeout(() => {
        item.remove();
        updateTotals();
      }, 180);
    };

    itemsWrapper.addEventListener("click", (event) => {
      const removeButton = event.target.closest(SELECTORS.cartRemove);

      if (!removeButton) return;

      const item = removeButton.closest(SELECTORS.cartItem);

      if (!item) return;

      removeCartItem(item);
    });

    itemsWrapper.addEventListener("input", (event) => {
      if (!event.target.matches(SELECTORS.quantityInput)) return;

      updateTotals();
    });

    itemsWrapper.addEventListener("change", (event) => {
      if (!event.target.matches(SELECTORS.quantityInput)) return;

      updateTotals();
    });

    updateTotals();
  }


  function initProductGallery() {
    const galleries = $all(SELECTORS.productGallery);

    galleries.forEach((gallery) => {
      const mainImage = $(SELECTORS.productMainImage, gallery);
      const thumbs = $all(SELECTORS.productThumb, gallery);

      if (!mainImage || thumbs.length === 0) return;

      function updateMainImage(thumb) {
        const thumbImage = thumb.querySelector("img");

        const newSrc =
          thumb.getAttribute("data-image-src") ||
          thumb.getAttribute("data-image") ||
          (thumbImage ? thumbImage.getAttribute("src") : "");

        const newAlt =
          thumb.getAttribute("data-image-alt") ||
          (thumbImage ? thumbImage.getAttribute("alt") : "");

        if (!newSrc) return;

        mainImage.style.opacity = "0";

        window.setTimeout(() => {
          mainImage.setAttribute("src", newSrc);

          if (newAlt) {
            mainImage.setAttribute("alt", newAlt);
          }

          mainImage.style.opacity = "1";
        }, 120);

        thumbs.forEach((item) => {
          const isActive = item === thumb;

          item.classList.toggle(CLASS_NAMES.active, isActive);
          item.setAttribute("aria-selected", isActive ? "true" : "false");
        });
      }

      thumbs.forEach((thumb) => {
        thumb.setAttribute("aria-selected", thumb.classList.contains(CLASS_NAMES.active) ? "true" : "false");

        thumb.addEventListener("click", () => {
          updateMainImage(thumb);
        });

        thumb.addEventListener("keydown", (event) => {
          if (event.key !== "Enter" && event.key !== " ") return;

          event.preventDefault();
          updateMainImage(thumb);
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

    const form = $("[data-search-form]", overlay);
    const chips = $all("[data-search-chip]", overlay);
    const resultItems = $all("[data-search-item]", overlay);
    const emptyState = $("[data-search-empty]", overlay);
    const resultsLabel = $("[data-search-results-label]", overlay);

    let lastFocusedElement = null;

    const focusableSelector = [
      "a[href]",
      "button:not([disabled])",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      "[tabindex]:not([tabindex='-1'])"
    ].join(",");

    const normalizeText = (value) => {
      return String(value || "")
        .trim()
        .toLowerCase()
        .replace(/ي/g, "ی")
        .replace(/ك/g, "ک")
        .replace(/ة/g, "ه")
        .replace(/أ|إ|آ/g, "ا")
        .replace(/۰/g, "0")
        .replace(/۱/g, "1")
        .replace(/۲/g, "2")
        .replace(/۳/g, "3")
        .replace(/۴/g, "4")
        .replace(/۵/g, "5")
        .replace(/۶/g, "6")
        .replace(/۷/g, "7")
        .replace(/۸/g, "8")
        .replace(/۹/g, "9");
    };

    const getFocusableElements = () => $all(focusableSelector, overlay);

    const setOpenButtonState = (state) => {
      openButtons.forEach((button) => {
        button.setAttribute("aria-expanded", state ? "true" : "false");
      });
    };

    const updateResults = () => {
      if (!input || resultItems.length === 0) return;

      const query = normalizeText(input.value);
      let visibleCount = 0;

      resultItems.forEach((item) => {
        const searchableText = normalizeText(
          `${item.textContent || ""} ${item.getAttribute("data-search-keywords") || ""}`
        );

        const isVisible = query === "" || searchableText.includes(query);

        item.classList.toggle("is-hidden", !isVisible);

        if (isVisible) {
          visibleCount += 1;
        }
      });

      if (emptyState) {
        emptyState.hidden = visibleCount !== 0;
      }

      if (resultsLabel) {
        if (query === "") {
          resultsLabel.textContent = "چند انتخاب مناسب برای شروع";
        } else if (visibleCount === 0) {
          resultsLabel.textContent = "نتیجه‌ای پیدا نشد";
        } else {
          resultsLabel.textContent = `${visibleCount} نتیجه پیدا شد`;
        }
      }
    };

    const openSearch = () => {
      lastFocusedElement = document.activeElement;

      overlay.classList.add(CLASS_NAMES.active);
      overlay.setAttribute("aria-hidden", "false");
      document.body.classList.add(CLASS_NAMES.menuOpen);
      setOpenButtonState(true);

      updateResults();

      if (input) {
        window.setTimeout(() => input.focus(), 80);
      }
    };

    const closeSearch = () => {
      overlay.classList.remove(CLASS_NAMES.active);
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove(CLASS_NAMES.menuOpen);
      setOpenButtonState(false);

      if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
        lastFocusedElement.focus();
      }
    };

    const trapFocus = (event) => {
      if (!overlay.classList.contains(CLASS_NAMES.active)) return;
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
      button.addEventListener("click", openSearch);
      button.setAttribute("aria-expanded", "false");
    });

    closeButtons.forEach((button) => {
      button.addEventListener("click", closeSearch);
    });

    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        closeSearch();
      }
    });

    if (input) {
      input.addEventListener("input", updateResults);
    }

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const value = chip.getAttribute("data-search-chip") || chip.textContent || "";

        if (input) {
          input.value = value.trim();
          input.focus();
          updateResults();
        }
      });
    });

    resultItems.forEach((item) => {
      item.addEventListener("click", closeSearch);
    });

    if (form && input) {
      form.addEventListener("submit", (event) => {
        if (input.value.trim() === "") {
          event.preventDefault();
          input.focus();
        }
      });
    }

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && overlay.classList.contains(CLASS_NAMES.active)) {
        closeSearch();
      }

      trapFocus(event);
    });
  }

  function initCurrentYear() {
    const yearItems = $all("[data-current-year]");
    const year = new Date().getFullYear();

    yearItems.forEach((item) => {
      item.textContent = String(year);
    });
  }

  function initProfileMenu() {
  const menus = $all(SELECTORS.profileMenu);

  if (menus.length === 0) return;

  menus.forEach((menu) => {
    const activeLink = $(SELECTORS.profileActiveLink, menu);

    if (!activeLink) return;

    activeLink.setAttribute("aria-current", "page");

    window.requestAnimationFrame(() => {
      const isScrollable = menu.scrollWidth > menu.clientWidth;

      if (!isScrollable) return;

      activeLink.scrollIntoView({
        behavior: prefersReducedMotion ? "auto" : "smooth",
        block: "nearest",
        inline: "center"
      });
    });
  });
}


function initOrderTabs() {
    const tabGroups = $all(SELECTORS.orderTabsRoot);

    if (tabGroups.length === 0) return;

    tabGroups.forEach((group) => {
      const tabs = $all(SELECTORS.orderTab, group);
      const panels = $all(SELECTORS.orderPanel, group);

      if (tabs.length === 0 || panels.length === 0) return;

      function activateTab(targetName) {
        tabs.forEach((tab) => {
          const isActive = tab.getAttribute("data-order-tab") === targetName;

          tab.classList.toggle(CLASS_NAMES.active, isActive);
          tab.setAttribute("aria-selected", isActive ? "true" : "false");
          tab.setAttribute("tabindex", isActive ? "0" : "-1");
        });

        panels.forEach((panel) => {
          const isActive = panel.getAttribute("data-order-panel") === targetName;

          panel.classList.toggle(CLASS_NAMES.active, isActive);

          if (isActive) {
            panel.removeAttribute("hidden");
          } else {
            panel.setAttribute("hidden", "");
          }
        });
      }

      tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          const targetName = tab.getAttribute("data-order-tab");

          if (!targetName) return;

          activateTab(targetName);
        });

        tab.addEventListener("keydown", (event) => {
          const currentIndex = tabs.indexOf(tab);

          if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;

          event.preventDefault();

          const direction = event.key === "ArrowRight" ? -1 : 1;
          const nextIndex = (currentIndex + direction + tabs.length) % tabs.length;
          const nextTab = tabs[nextIndex];
          const targetName = nextTab.getAttribute("data-order-tab");

          if (!targetName) return;

          activateTab(targetName);
          nextTab.focus();
        });
      });

      const activeTab = tabs.find((tab) => tab.classList.contains(CLASS_NAMES.active)) || tabs[0];
      const initialTarget = activeTab.getAttribute("data-order-tab");

      if (initialTarget) {
        activateTab(initialTarget);
      }
    });
  }


  function initAddressModal() {
      const modal = $(SELECTORS.addressModal);
      const form = $(SELECTORS.addressForm);
      const openButtons = $all(SELECTORS.addressModalOpen);
      const closeButtons = $all(SELECTORS.addressModalClose);

      if (!modal || openButtons.length === 0) return;

      const dialog = $(".address-modal-dialog", modal);
      const title = $(SELECTORS.addressModalTitle, modal);
      const submitText = $(SELECTORS.addressSubmitText, modal);
      const addressIdInput = $(SELECTORS.addressIdInput, modal);
      const fields = $all(SELECTORS.addressField, modal);

      let lastFocusedElement = null;

      const focusableSelector = [
        "a[href]",
        "button:not([disabled])",
        "input:not([disabled])",
        "select:not([disabled])",
        "textarea:not([disabled])",
        "[tabindex]:not([tabindex='-1'])"
      ].join(",");

      const getFocusableElements = () => $all(focusableSelector, modal);

      const toDatasetKey = (name) => {
        return name.replace(/_([a-z])/g, function (_, letter) {
          return letter.toUpperCase();
        });
      };

      const setOpenButtonState = (state) => {
        openButtons.forEach((button) => {
          button.setAttribute("aria-expanded", state ? "true" : "false");
        });
      };

      const resetForm = () => {
        if (form) {
          form.reset();
        }

        if (addressIdInput) {
          addressIdInput.value = "";
        }

        fields.forEach((field) => {
          field.value = "";
        });
      };

      const fillFormFromButton = (button) => {
        if (!button) return;

        if (addressIdInput) {
          addressIdInput.value = button.getAttribute("data-address-id") || "";
        }

        fields.forEach((field) => {
          const fieldName = field.getAttribute("data-address-field");

          if (!fieldName) return;

          const datasetKey = toDatasetKey(fieldName);
          const value = button.dataset[datasetKey] || "";

          field.value = value;
        });
      };

      const setModalMode = (mode) => {
        const isEdit = mode === "edit";

        if (title) {
          title.textContent = isEdit ? "ویرایش آدرس" : "افزودن آدرس جدید";
        }

        if (submitText) {
          submitText.textContent = isEdit ? "ذخیره تغییرات" : "ذخیره آدرس";
        }
      };

      const openModal = (button) => {
        const mode = button.getAttribute("data-address-mode") || "create";

        lastFocusedElement = document.activeElement;

        resetForm();
        setModalMode(mode);

        if (mode === "edit") {
          fillFormFromButton(button);
        }

        modal.classList.add(CLASS_NAMES.active);
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add(CLASS_NAMES.addressModalOpen);
        setOpenButtonState(true);

        window.setTimeout(() => {
          const firstFocusable = getFocusableElements()[0];

          if (firstFocusable) {
            firstFocusable.focus();
          } else if (dialog) {
            dialog.setAttribute("tabindex", "-1");
            dialog.focus();
          }
        }, 80);
      };

      const closeModal = () => {
        modal.classList.remove(CLASS_NAMES.active);
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove(CLASS_NAMES.addressModalOpen);
        setOpenButtonState(false);

        if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
          lastFocusedElement.focus();
        }
      };

      const trapFocus = (event) => {
        if (!modal.classList.contains(CLASS_NAMES.active)) return;
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
        button.setAttribute("aria-expanded", "false");

        button.addEventListener("click", () => {
          openModal(button);
        });
      });

      closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
      });

      modal.addEventListener("click", (event) => {
        const closeTarget = event.target.closest(SELECTORS.addressModalClose);

        if (closeTarget) {
          closeModal();
        }
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains(CLASS_NAMES.active)) {
          closeModal();
        }

        trapFocus(event);
      });
    }

  /* =========================================================
   Checkout Page
========================================================= */

function initCheckoutChoices() {
  const choices = $all(SELECTORS.checkoutChoice);

  if (choices.length === 0) return;

  const getInput = (choice) => {
    return $(SELECTORS.checkoutChoiceInput, choice);
  };

  const getGroupChoices = (input) => {
    if (!input || !input.name) return [];

    return choices.filter((choice) => {
      const choiceInput = getInput(choice);

      return choiceInput && choiceInput.name === input.name;
    });
  };

  const activateChoice = (choice, shouldFocus = false) => {
    const input = getInput(choice);

    if (!input || input.disabled) return;

    const groupChoices = getGroupChoices(input);

    input.checked = true;

    groupChoices.forEach((groupChoice) => {
      const groupInput = getInput(groupChoice);
      const isActive = groupChoice === choice;

      groupChoice.classList.toggle(CLASS_NAMES.active, isActive);
      groupChoice.setAttribute("aria-checked", isActive ? "true" : "false");
      groupChoice.setAttribute("tabindex", isActive ? "0" : "-1");

      if (groupInput) {
        groupInput.checked = isActive;
      }
    });

    input.dispatchEvent(new Event("change", { bubbles: true }));

    if (shouldFocus) {
      choice.focus();
    }
  };

  const activateCheckedChoices = () => {
    const groupedNames = new Set();

    choices.forEach((choice) => {
      const input = getInput(choice);

      if (!input || !input.name || groupedNames.has(input.name)) return;

      groupedNames.add(input.name);

      const groupChoices = getGroupChoices(input);
      const checkedChoice = groupChoices.find((item) => {
        const itemInput = getInput(item);

        return itemInput && itemInput.checked;
      });

      if (checkedChoice) {
        activateChoice(checkedChoice);
        return;
      }

      if (groupChoices[0]) {
        activateChoice(groupChoices[0]);
      }
    });
  };

  const moveChoice = (choice, direction) => {
    const input = getInput(choice);
    const groupChoices = getGroupChoices(input);

    if (groupChoices.length <= 1) return;

    const currentIndex = groupChoices.indexOf(choice);
    const nextIndex = (currentIndex + direction + groupChoices.length) % groupChoices.length;
    const nextChoice = groupChoices[nextIndex];

    if (nextChoice) {
      activateChoice(nextChoice, true);
    }
  };

  choices.forEach((choice) => {
    const input = getInput(choice);

    if (!input) return;

    choice.setAttribute("role", "radio");
    choice.setAttribute("aria-checked", input.checked ? "true" : "false");
    choice.setAttribute("tabindex", input.checked ? "0" : "-1");

    input.setAttribute("tabindex", "-1");

    choice.addEventListener("click", (event) => {
      const editButton = event.target.closest(SELECTORS.addressModalOpen);

      if (editButton) return;

      activateChoice(choice);
    });

    choice.addEventListener("keydown", (event) => {
      const key = event.key;

      if (key === "Enter" || key === " ") {
        event.preventDefault();
        activateChoice(choice);
        return;
      }

      if (key === "ArrowDown" || key === "ArrowLeft") {
        event.preventDefault();
        moveChoice(choice, 1);
        return;
      }

      if (key === "ArrowUp" || key === "ArrowRight") {
        event.preventDefault();
        moveChoice(choice, -1);
      }
    });

    input.addEventListener("change", () => {
      if (input.checked) {
        activateChoice(choice);
      }
    });
  });

  $all(SELECTORS.addressModalOpen).forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
    });
  });

  activateCheckedChoices();
}


function initCheckoutSubmitState() {
  const form = $(SELECTORS.checkoutForm);

  if (!form) return;

  const submitButton = $(SELECTORS.checkoutSubmitButton, form);

  if (!submitButton) return;

  const originalText = submitButton.textContent.trim();

  form.addEventListener("submit", () => {
    if (typeof form.checkValidity === "function" && !form.checkValidity()) {
      return;
    }

    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");
    submitButton.textContent = "در حال انتقال به پرداخت...";
  });

  window.addEventListener("pageshow", () => {
    submitButton.disabled = false;
    submitButton.removeAttribute("aria-busy");
    submitButton.textContent = originalText;
  });
}


function initCheckoutCouponMock() {
  const coupon = $(SELECTORS.checkoutCoupon);

  if (!coupon) return;

  const input = $(SELECTORS.checkoutCouponInput, coupon);
  const applyButton = $(SELECTORS.checkoutCouponApply, coupon);
  const message = $(SELECTORS.checkoutCouponMessage, coupon);
  const discountRow = $(SELECTORS.checkoutDiscountRow);
  const discountAmount = $(SELECTORS.checkoutDiscountAmount);
  const finalTotal = $(SELECTORS.checkoutFinalTotal);

  if (!input || !applyButton || !message || !discountRow || !discountAmount || !finalTotal) return;

  const formatPersianNumber = (number) => {
    return new Intl.NumberFormat("fa-IR").format(number);
  };

  const baseTotal = Number(finalTotal.dataset.baseTotal || 0);

  const coupons = {
    WARM10: {
      discount: 220000,
      message: "کد تخفیف با موفقیت اعمال شد."
    },
    COFFEE10: {
      discount: 220000,
      message: "کد تخفیف قهوه با موفقیت اعمال شد."
    }
  };

  const setMessage = (text, type) => {
    message.textContent = text;
    message.classList.remove("is-success", "is-error");

    if (type) {
      message.classList.add(type);
    }
  };

  const applyCoupon = () => {
    const code = input.value.trim().toUpperCase();

    if (!code) {
      discountRow.classList.add(CLASS_NAMES.hidden);
      discountAmount.textContent = "- ۰ تومان";
      finalTotal.textContent = `${formatPersianNumber(baseTotal)} تومان`;
      setMessage("لطفاً کد تخفیف را وارد کنید.", "is-error");
      return;
    }

    const couponData = coupons[code];

    if (!couponData) {
      discountRow.classList.add(CLASS_NAMES.hidden);
      discountAmount.textContent = "- ۰ تومان";
      finalTotal.textContent = `${formatPersianNumber(baseTotal)} تومان`;
      setMessage("کد تخفیف واردشده معتبر نیست.", "is-error");
      return;
    }

    const nextTotal = Math.max(baseTotal - couponData.discount, 0);

    discountRow.classList.remove(CLASS_NAMES.hidden);
    discountAmount.textContent = `- ${formatPersianNumber(couponData.discount)} تومان`;
    finalTotal.textContent = `${formatPersianNumber(nextTotal)} تومان`;

    setMessage(couponData.message, "is-success");
  };

  applyButton.addEventListener("click", applyCoupon);

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      applyCoupon();
    }
  });

  input.addEventListener("input", () => {
    input.value = input.value.toUpperCase();
  });
}


function initProductVariants() {
  const root = $(SELECTORS.productVariants);

  if (!root) return;

  const options = $all(SELECTORS.variantOption, root);
  const selectedLabel = $(SELECTORS.selectedVariantLabel, root);
  const selectedInput = $(SELECTORS.selectedVariantInput, root);
  const selectedWeightAttribute = $(SELECTORS.selectedWeightAttribute);
  const priceEl = $(SELECTORS.productPrice, root);
  const stockStatus = $(SELECTORS.productStockStatus, root);
  const unavailableNote = $(SELECTORS.productUnavailableNote, root);
  const addToCartButton = $(SELECTORS.addToCartButton, root);

  if (options.length === 0) return;

  function setButtonAvailability(isAvailable) {
    if (!addToCartButton) return;

    addToCartButton.disabled = !isAvailable;
    addToCartButton.classList.toggle("is-disabled", !isAvailable);

    if (isAvailable) {
      addToCartButton.textContent = "افزودن به سبد خرید";
      addToCartButton.setAttribute("aria-disabled", "false");
    } else {
      addToCartButton.textContent = "ناموجود";
      addToCartButton.setAttribute("aria-disabled", "true");
    }
  }

  function setStockStatus(isAvailable) {
    if (!stockStatus) return;

    stockStatus.classList.toggle("is-available", isAvailable);
    stockStatus.classList.toggle("is-unavailable", !isAvailable);
    stockStatus.textContent = isAvailable ? "آماده ارسال" : "فعلاً ناموجود";
  }

  function updateVariant(option) {
    if (!option) return;

    const variantId = option.dataset.variantId || "";
    const variantTitle = option.dataset.variantTitle || "";
    const variantPrice = option.dataset.variantPrice || "";
    const isAvailable = option.dataset.variantAvailable === "true";

    options.forEach((item) => {
      const isActive = item === option;

      item.classList.toggle(CLASS_NAMES.active, isActive);
      item.setAttribute("aria-checked", isActive ? "true" : "false");
    });

    if (selectedLabel) {
      selectedLabel.textContent = variantTitle;
    }

    if (selectedInput) {
      selectedInput.value = variantId;
    }

    if (selectedWeightAttribute) {
      selectedWeightAttribute.textContent = variantTitle;
    }

    if (priceEl) {
      priceEl.textContent = variantPrice;
    }

    if (unavailableNote) {
      unavailableNote.classList.toggle("hidden", isAvailable);
    }

    setStockStatus(isAvailable);
    setButtonAvailability(isAvailable);
  }

  const activeOption =
    options.find((option) => option.classList.contains(CLASS_NAMES.active)) ||
    options.find((option) => option.dataset.variantId === root.dataset.defaultVariant) ||
    options[0];

  updateVariant(activeOption);

  options.forEach((option) => {
    option.addEventListener("click", () => {
      updateVariant(option);
    });

    option.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;

      event.preventDefault();
      updateVariant(option);
    });
  });
}

function initCommentModal() {
  const modal = $(SELECTORS.commentModal);
  const overlay = $(SELECTORS.commentModalOverlay);
  const openButtons = $all(SELECTORS.commentModalOpen);
  const closeButtons = $all(SELECTORS.commentModalClose);
  const form = $(SELECTORS.commentForm);

  if (!modal || !overlay || openButtons.length === 0) return;

  let lastFocusedElement = null;

  const focusableSelector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled])",
    "textarea:not([disabled])",
    "select:not([disabled])",
    "[tabindex]:not([tabindex='-1'])"
  ].join(",");

  function getFocusableElements() {
    return $all(focusableSelector, modal);
  }

  function openModal() {
    lastFocusedElement = document.activeElement;

    modal.classList.add(CLASS_NAMES.active);
    overlay.classList.add(CLASS_NAMES.active);
    document.body.classList.add(CLASS_NAMES.commentModalOpen);

    modal.setAttribute("aria-hidden", "false");
    overlay.setAttribute("aria-hidden", "false");

    const focusableElements = getFocusableElements();

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }

  function closeModal() {
    modal.classList.remove(CLASS_NAMES.active);
    overlay.classList.remove(CLASS_NAMES.active);
    document.body.classList.remove(CLASS_NAMES.commentModalOpen);

    modal.setAttribute("aria-hidden", "true");
    overlay.setAttribute("aria-hidden", "true");

    if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
      lastFocusedElement.focus();
    }
  }

  function trapFocus(event) {
    if (!modal.classList.contains(CLASS_NAMES.active)) return;
    if (event.key !== "Tab") return;

    const focusableElements = getFocusableElements();

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    }

    if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  }

  function getPersianToday() {
    try {
      return new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
      }).format(new Date());
    } catch (error) {
      return "";
    }
  }

  function createCommentCard(firstName, lastName, text) {
    const commentsList = $(SELECTORS.commentsList);
    const commentsEmpty = $(SELECTORS.commentsEmpty);

    if (!commentsList) return;

    const fullName = `${firstName} ${lastName}`.trim();
    const avatarText = firstName.trim().charAt(0) || "ک";
    const today = getPersianToday();

    const card = document.createElement("article");
    card.className = "product-comment-card";

    card.innerHTML = `
      <header class="product-comment-head">
        <div class="product-comment-avatar" aria-hidden="true">${avatarText}</div>

        <div>
          <h3 class="product-comment-name"></h3>
          <time class="product-comment-date"></time>
        </div>
      </header>

      <p class="product-comment-text"></p>
    `;

    const nameEl = $(".product-comment-name", card);
    const dateEl = $(".product-comment-date", card);
    const textEl = $(".product-comment-text", card);

    if (nameEl) nameEl.textContent = fullName;
    if (dateEl) dateEl.textContent = today;
    if (textEl) textEl.textContent = text;

    commentsList.prepend(card);
    commentsList.classList.remove("hidden");

    if (commentsEmpty) {
      commentsEmpty.classList.add("hidden");
    }
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", openModal);
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  overlay.addEventListener("click", closeModal);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains(CLASS_NAMES.active)) {
      closeModal();
    }

    trapFocus(event);
  });

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();

      const firstNameInput = form.querySelector("[name='first_name']");
      const lastNameInput = form.querySelector("[name='last_name']");
      const textInput = form.querySelector("[name='text']");

      const firstName = firstNameInput ? firstNameInput.value.trim() : "";
      const lastName = lastNameInput ? lastNameInput.value.trim() : "";
      const text = textInput ? textInput.value.trim() : "";

      if (!firstName || !lastName || !text) {
        form.reportValidity();
        return;
      }

      createCommentCard(firstName, lastName, text);
      form.reset();
      closeModal();
    });
  }
}


function initOtpLogin() {
  const roots = document.querySelectorAll("[data-otp-login]");

  if (roots.length === 0) return;

  const OTP_TIMER_SECONDS = 45;

  const toEnglishDigits = (value) => {
    if (!value) return "";

    const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
    const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

    return String(value).replace(/[۰-۹٠-٩]/g, (digit) => {
      const persianIndex = persianDigits.indexOf(digit);
      if (persianIndex > -1) return String(persianIndex);

      const arabicIndex = arabicDigits.indexOf(digit);
      if (arabicIndex > -1) return String(arabicIndex);

      return digit;
    });
  };

  const normalizePhone = (value) => {
    return toEnglishDigits(value).replace(/[^\d]/g, "");
  };

  const normalizeCode = (value) => {
    return toEnglishDigits(value).replace(/[^\d]/g, "").slice(0, 6);
  };

  const isValidPhone = (phone) => {
    return /^09\d{9}$/.test(phone);
  };

  roots.forEach((root) => {
    const form = root.querySelector("[data-otp-form]");
    const phoneStep = root.querySelector('[data-otp-step="phone"]');
    const codeStep = root.querySelector('[data-otp-step="code"]');

    const phoneInput = root.querySelector("[data-otp-phone]");
    const phoneHelp = root.querySelector("[data-otp-phone-help]");
    const sendButton = root.querySelector("[data-otp-send]");

    const codeInput = root.querySelector("[data-otp-code]");
    const codeHelp = root.querySelector("[data-otp-code-help]");
    const phonePreview = root.querySelector("[data-otp-phone-preview]");
    const changePhoneButton = root.querySelector("[data-otp-change-phone]");

    const resendButton = root.querySelector("[data-otp-resend]");
    const timerText = root.querySelector("[data-otp-timer-text]");
    const message = root.querySelector("[data-otp-message]");

    if (!form || !phoneStep || !codeStep || !phoneInput || !sendButton || !codeInput) {
      return;
    }

    let timerId = null;
    let secondsLeft = OTP_TIMER_SECONDS;

    const clearMessage = () => {
      if (!message) return;

      message.textContent = "";
      message.classList.remove("is-error", "is-success", "is-info");
    };

    const setMessage = (text, type) => {
      if (!message) return;

      message.textContent = text;
      message.classList.remove("is-error", "is-success", "is-info");

      if (type) {
        message.classList.add(`is-${type}`);
      }
    };

    const setHelpState = (element, type) => {
      if (!element) return;

      element.classList.remove("is-error", "is-success");

      if (type) {
        element.classList.add(`is-${type}`);
      }
    };

    const setStep = (stepName) => {
      const isPhoneStep = stepName === "phone";

      phoneStep.hidden = !isPhoneStep;
      phoneStep.setAttribute("aria-hidden", isPhoneStep ? "false" : "true");
      phoneStep.classList.toggle("is-active", isPhoneStep);

      codeStep.hidden = isPhoneStep;
      codeStep.setAttribute("aria-hidden", isPhoneStep ? "true" : "false");
      codeStep.classList.toggle("is-active", !isPhoneStep);
    };

    const stopTimer = () => {
      if (timerId) {
        window.clearInterval(timerId);
        timerId = null;
      }
    };

    const updateTimerText = () => {
      if (!timerText || !resendButton) return;

      if (secondsLeft > 0) {
        timerText.textContent = `ارسال دوباره کد تا ${secondsLeft} ثانیه دیگر فعال می‌شود.`;
        resendButton.disabled = true;
        return;
      }

      timerText.textContent = "اگر کدی دریافت نکردید، می‌توانید دوباره درخواست دهید.";
      resendButton.disabled = false;
    };

    const startTimer = () => {
      stopTimer();

      secondsLeft = OTP_TIMER_SECONDS;
      updateTimerText();

      timerId = window.setInterval(() => {
        secondsLeft -= 1;
        updateTimerText();

        if (secondsLeft <= 0) {
          stopTimer();
        }
      }, 1000);
    };

    const showCodeStep = () => {
      const phone = normalizePhone(phoneInput.value);

      if (!isValidPhone(phone)) {
        phoneInput.focus();

        if (phoneHelp) {
          phoneHelp.textContent = "شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد.";
        }

        setHelpState(phoneHelp, "error");
        setMessage("لطفا شماره موبایل را درست وارد کنید.", "error");
        return;
      }

      phoneInput.value = phone;

      if (phonePreview) {
        phonePreview.textContent = phone;
      }

      if (phoneHelp) {
        phoneHelp.textContent = "شماره موبایل تایید شد.";
      }

      setHelpState(phoneHelp, "success");
      setHelpState(codeHelp, null);
      clearMessage();

      setStep("code");
      startTimer();

      window.setTimeout(() => {
        codeInput.focus();
      }, 80);
    };

    const resetToPhoneStep = () => {
      stopTimer();

      codeInput.value = "";

      if (codeHelp) {
        codeHelp.textContent = "کد ارسال‌شده را وارد کنید.";
      }

      setHelpState(codeHelp, null);
      clearMessage();
      setStep("phone");

      window.setTimeout(() => {
        phoneInput.focus();
      }, 80);
    };

    const resendCode = () => {
      codeInput.value = "";

      if (codeHelp) {
        codeHelp.textContent = "کد جدید را وارد کنید.";
      }

      setHelpState(codeHelp, null);
      setMessage("کد ورود دوباره آماده شد.", "info");
      startTimer();

      window.setTimeout(() => {
        codeInput.focus();
      }, 80);
    };

    phoneInput.addEventListener("input", () => {
      phoneInput.value = normalizePhone(phoneInput.value).slice(0, 11);

      if (phoneHelp) {
        phoneHelp.textContent = "شماره موبایل را با ۰۹ وارد کنید.";
      }

      setHelpState(phoneHelp, null);
      clearMessage();
    });

    codeInput.addEventListener("input", () => {
      codeInput.value = normalizeCode(codeInput.value);

      if (codeHelp) {
        codeHelp.textContent = "کد ارسال‌شده را وارد کنید.";
      }

      setHelpState(codeHelp, null);
      clearMessage();
    });

    sendButton.addEventListener("click", showCodeStep);

    phoneInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        showCodeStep();
      }
    });

    if (changePhoneButton) {
      changePhoneButton.addEventListener("click", resetToPhoneStep);
    }

    if (resendButton) {
      resendButton.addEventListener("click", resendCode);
    }

    form.addEventListener("submit", (event) => {
      const phone = normalizePhone(phoneInput.value);
      const code = normalizeCode(codeInput.value);

      phoneInput.value = phone;
      codeInput.value = code;

      if (!isValidPhone(phone)) {
        event.preventDefault();
        resetToPhoneStep();
        setMessage("لطفا شماره موبایل را دوباره بررسی کنید.", "error");
        return;
      }

      if (!/^\d{6}$/.test(code)) {
        event.preventDefault();

        if (codeHelp) {
          codeHelp.textContent = "کد تایید باید ۶ رقم باشد.";
        }

        setHelpState(codeHelp, "error");
        setMessage("کد تایید کامل نیست.", "error");
        codeInput.focus();
        return;
      }

      /*
       * Static-template mock:
       * Remove event.preventDefault() later when backend OTP verification is ready.
       */
      event.preventDefault();

      setHelpState(codeHelp, "success");
      setMessage("ورود با موفقیت انجام شد. در نسخه نهایی، کاربر وارد حساب می‌شود.", "success");
    });

    setStep("phone");
  });
}






  ready(function () {
    initHeaderScroll();
    initMobileMenu();
    initHeroSlider();
    initProfileMenu();
    initAddressModal();
    initCheckoutChoices();
    initCheckoutSubmitState();
    initCheckoutCouponMock();
    initOrderTabs();
    initReveal();
    initQuantityControls();
    initOtpLogin();
    initProductVariants();
    initCommentModal();
    initCartPage();
    initProductGallery();
    initAccordions();
    initSearchOverlay();
    initCurrentYear();
  });
})();