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
  };

  const CLASS_NAMES = {
    scrolled: "is-scrolled",
    active: "is-active",
    visible: "is-visible",
    menuOpen: "menu-open",
    addressModalOpen: "address-modal-open"
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
    initCartPage();
    initProductGallery();
    initAccordions();
    initSearchOverlay();
    initCurrentYear();
  });
})();