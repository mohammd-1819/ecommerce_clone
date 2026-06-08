# Handoff — Persian RTL Coffee Store

## Purpose of This Document

This file is the complete working brief for future sessions. Whenever another page is created, read this file together with `PRODUCT.md`, `DESIGN.md`, and `IMPLEMENTATION.md` before writing templates, CSS, or JavaScript.

---

## Project Summary

Django storefront for a Persian/RTL coffee, tea, and hot chocolate brand.

Current stage:

```text
Static Django templates first. Backend connection later.
```

The website should be minimal, warm, premium, and product-focused. It is inspired by Danidor only as a mood reference, not as something to copy exactly.

---

## Non-Negotiable User Requirements

1. Whole site must be Persian and RTL.
2. Use Vazir font.
3. Use the provided warm luxury palette.
4. Keep pages minimal and not crowded.
5. Do not make sections too large.
6. Templates are static first; backend comes later.
7. Cart, checkout, payment, and account pages are part of the planned structure.
8. All CSS for the entire site must be in `static/css/main.css`.
9. All JS for the entire site must be in `static/js/main.js`.
10. When adding new page styles, extend `main.css`; do not create another CSS file.
11. When adding new behavior, extend `main.js`; do not create another JS file.
12. Use local static assets, not external CDNs.
13. Documentation must contain enough context so future sessions know exactly what to build.

---

## Color Palette

```css
:root {
  --color-bg: #F6F2EC;       /* شیری گرم */
  --color-surface: #FFFFFF;  /* سفید خالص */
  --color-text: #181512;     /* شکلاتی خیلی تیره */
  --color-primary: #3A2A21;  /* کاکائویی تیره */
  --color-accent: #D6A95F;   /* طلایی ملایم */
}
```

Feeling:

```text
لوکس، مرتب، مناسب بسته‌بندی‌های قهوه و هات‌چاکلت
```

Use this palette so product photography is emphasized and the background does not become visually noisy.

---

## Visual Direction

The design should feel:

- Minimal
- Warm
- Ordered
- Premium
- Calm
- Trustworthy

The product should be the main visual element.

Avoid:

- Crowded layouts
- Large noisy sections
- Too many banners
- Too many colors
- Heavy dark luxury look
- Exact copying of Danidor
- Generic marketplace templates

---

## Static Directory

Preferred structure:

```text
static/
  css/
    main.css
  js/
    main.js
  fonts/
    Vazir.woff2
  images/
    logo.svg
    hero-product.png
    products/
    categories/
    icons/
```

The user mentioned `static/css`, `statics/js`, `statics/fonts`, and `statics/images`. If the existing Django settings already use `statics/`, preserve that root name. Otherwise standardize to `static/`.

In every case, the logical rule remains:

```text
one CSS file: css/main.css
one JS file: js/main.js
fonts folder
images folder
```

---

## Template Structure

Recommended full template tree:

```text
templates/
  base.html
  partials/
    header.html
    footer.html
    mobile_drawer.html
    search_panel.html
    product_card.html
    breadcrumbs.html
    empty_state.html
  pages/
    home.html
    about.html
    contact.html
    faq.html
    terms.html
  products/
    product_list.html
    product_detail.html
    category.html
  cart/
    cart.html
  checkout/
    checkout.html
    payment_redirect.html
    payment_success.html
    payment_failed.html
  accounts/
    login.html
    otp.html
    profile.html
    addresses.html
    orders.html
    order_detail.html
```

---

## Planned Django Apps Later

When backend is added, likely apps:

```text
core
products
cart
orders
checkout/payment
accounts
inquiries
```

Do not let static templates block backend integration. Use clear class names, semantic markup, and replaceable static data.

---

## Required Global CSS File

All styles go in:

```text
static/css/main.css
```

`main.css` must include:

```text
1. Font face
2. Variables/tokens
3. Reset/base
4. Typography
5. Layout utilities
6. Buttons
7. Forms
8. Header
9. Mobile drawer
10. Footer
11. Shared cards/components
12. Home page
13. Product list page
14. Product detail page
15. Cart page
16. Checkout page
17. Payment pages
18. Account pages
19. Responsive rules
20. Reduced motion
```

Do not create page CSS files.

---

## Required Global JS File

All JavaScript goes in:

```text
static/js/main.js
```

`main.js` should contain reusable initializers:

```text
initHeaderScroll()
initMobileDrawer()
initSearchPanel()
initProductGallery()
initQuantityControls()
initAccordions()
initTabs()
initCheckoutSteps()
initFormValidationMock()
```

Rules:

- Use vanilla JavaScript.
- Use defensive selectors.
- No page should break because a component does not exist on that page.
- Use `data-*` attributes for JS hooks.
- Keep animation subtle.

---

## Homepage Plan

Build `templates/pages/home.html` with:

```text
1. Hero
2. Category highlights
3. Featured products
4. About teaser
5. Wholesale/contact request section
6. Footer from partial
```

Hero should be compact:

```text
Right/text: headline, short text, CTA buttons
Left/media: product image/card
```

Suggested Persian copy:

```text
قهوه‌ای برای لحظه‌های آرام‌تر
طعم گرم، بسته‌بندی مرتب، انتخابی ساده برای خانه و محل کار.
```

Suggested CTA labels:

```text
مشاهده محصولات
درخواست خرید عمده
```

Do not add a huge video section in the first version.

---

## Product List Plan

Create `templates/products/product_list.html` with:

```text
1. Page hero/title
2. Category chips
3. Search/sort row
4. Product grid
5. Pagination placeholder
```

Keep filters simple and static first.

---

## Product Detail Plan

Create `templates/products/product_detail.html` with:

```text
1. Breadcrumbs
2. Product gallery
3. Product info
4. Price
5. Quantity selector
6. Add to cart
7. Description/details section
8. Related products
```

Use `main.js` for gallery thumbnail switching and quantity controls.

---

## Cart Plan

Create `templates/cart/cart.html` with:

```text
1. Cart item list
2. Quantity controls
3. Item remove button mock
4. Cart summary
5. Checkout CTA
6. Empty cart state markup
```

Cart should be clear and practical, not decorative.

---

## Checkout Plan

Create `templates/checkout/checkout.html` with:

```text
1. Customer information
2. Address information
3. Shipping method
4. Payment method
5. Order summary
6. Final submit button
```

Use real form labels and `name` attributes even while static.

---

## Payment Plan

Create:

```text
templates/checkout/payment_success.html
templates/checkout/payment_failed.html
```

Each payment page should have:

- Clear status message
- Order number placeholder
- Short explanation
- CTA to products or orders

---

## Account Plan

Static pages later:

```text
login.html
otp.html
profile.html
addresses.html
orders.html
order_detail.html
```

Keep them simple, clean, and form-focused.

---

## Persian Copy Rules

Use short natural Persian.

Good:

```text
محصولات منتخب
چند انتخاب محبوب برای شروع یک روز گرم و خوش‌طعم.
```

Good:

```text
درخواست خرید عمده یا مشاوره
فرم را تکمیل کنید تا برای انتخاب محصول مناسب با شما تماس بگیریم.
```

Avoid:

- Long marketing paragraphs
- Overly formal bureaucratic language
- English labels in visible UI
- Mixed LTR/RTL layout issues

---

## Component Class Names to Reuse

Shared:

```text
container
section
section-header
section-eyebrow
section-title
section-text
btn
btn-primary
btn-secondary
btn-ghost
btn-sm
btn-lg
card
badge
```

Header:

```text
site-header
header-inner
brand-link
main-nav
nav-link
header-actions
icon-btn
cart-count
mobile-menu-toggle
mobile-drawer
mobile-drawer-backdrop
```

Products:

```text
product-grid
product-card
product-card-image
product-card-body
product-card-meta
product-card-title
product-card-price-row
product-price
product-old-price
product-card-actions
```

Forms:

```text
form-card
form-grid
form-field
form-label
form-input
form-select
form-textarea
form-help
form-error
```

Cart:

```text
cart-layout
cart-items
cart-item
cart-item-image
cart-item-info
cart-item-title
cart-item-price
cart-item-actions
cart-summary
summary-row
summary-total
```

Checkout:

```text
checkout-layout
checkout-form
checkout-section
checkout-summary
payment-methods
shipping-methods
```

Payment:

```text
payment-result
payment-icon
payment-title
payment-message
payment-actions
```

---

## Backend Readiness Rules

While writing static templates:

- Use realistic product card markup.
- Keep repeated items easy to wrap in `{% for %}` later.
- Use `name` attributes in forms.
- Use semantic elements: `header`, `main`, `section`, `article`, `footer`.
- Keep partials reusable.
- Do not hard-code styles inline.
- Do not rely on JavaScript for core content visibility.

---

## Design Density Rules

Because the user does not want large or crowded pages:

- Homepage hero must not be full-screen.
- Use 3–4 category cards, not more.
- Use 4 featured products, not more, unless requested.
- Keep paragraphs short.
- Use whitespace but not oversized empty areas.
- Use one primary CTA per section.
- Avoid decorative illustrations unless subtle.

---

## Accessibility Rules

Before finishing any template, check:

```text
HTML lang="fa" dir="rtl"
Buttons have accessible names
Images have Persian alt text
Inputs have labels
Focus states are visible
Mobile drawer uses aria-expanded
Keyboard escape closes drawer/modal
Reduced motion is respected
```

---

## When Creating a New Page

Always follow this process:

1. Check which template file is needed.
2. Read the relevant page plan in this handoff.
3. Use existing shared components/classes.
4. Add only necessary new CSS to `main.css`.
5. Add only necessary new JS to `main.js`.
6. Keep copy Persian and concise.
7. Keep layout compact and minimal.
8. Make static content easy to replace with backend data later.

---

## First Recommended Build Task

Start with:

```text
templates/base.html
templates/partials/header.html
templates/partials/footer.html
templates/partials/mobile_drawer.html
templates/pages/home.html
static/css/main.css
static/js/main.js
```

After homepage approval, continue with:

```text
products/product_list.html
products/product_detail.html
cart/cart.html
checkout/checkout.html
checkout/payment_success.html
checkout/payment_failed.html
```
