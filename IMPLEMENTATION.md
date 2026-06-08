# Implementation — Django Static Templates First

## Technical Direction

This is a Django project, but templates should be built as static templates first.

The current goal is to create polished front-end templates that can later be connected to Django views, models, forms, cart logic, checkout, and payment.

---

## Core Rules

1. The entire visible site must be Persian and RTL.
2. Use Vazir font from local static files.
3. Use plain CSS in one file: `static/css/main.css`.
4. Use plain JavaScript in one file: `static/js/main.js`.
5. Do not use external CDNs.
6. Do not create separate CSS files per page.
7. Do not create separate JS files per page.
8. Use static placeholder content now; keep HTML ready for backend integration later.
9. Keep pages minimal and not crowded.
10. Reuse shared components across all pages.

---

## Static Directory

Canonical static directory:

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

The user mentioned the static structure as:

```text
static/css
statics/js
statics/fonts
statics/images
```

For Django consistency, use one root directory named `static/` unless the existing project settings already use `statics/`. If the actual project uses `statics/`, keep the project setting and mirror the same subfolders there. The logical structure stays the same:

```text
css/main.css
js/main.js
fonts/
images/
```

---

## Template Directory

Recommended template structure:

```text
templates/
  base.html
  partials/
    header.html
    footer.html
    mobile_drawer.html
    search_panel.html
    product_card.html
    empty_state.html
    breadcrumbs.html
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

All templates can be static at first. Later, partials can be converted to accept context data.

---

## Django Apps Planned Later

Recommended apps when backend is added:

```text
core        site settings, static pages, shared context
products    categories, products, product images
cart        session cart or user cart
orders      checkout, orders, order items, payment records
accounts    login, OTP, profile, addresses
inquiries   wholesale/contact forms
```

Do not overbuild backend now. The current front-end should simply anticipate these features.

---

## Base Template Requirements

`templates/base.html` should contain:

- `{% load static %}`
- HTML `lang="fa"` and `dir="rtl"`
- Meta viewport
- SEO title block
- Link to `static/css/main.css`
- Header include
- Main content block
- Footer include
- Mobile drawer include if needed
- Script link to `static/js/main.js`

Recommended skeleton:

```django
{% load static %}
<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}نام برند{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
  {% include 'partials/header.html' %}

  <main id="main-content">
    {% block content %}{% endblock %}
  </main>

  {% include 'partials/footer.html' %}
  {% include 'partials/mobile_drawer.html' %}

  <script src="{% static 'js/main.js' %}" defer></script>
</body>
</html>
```

---

## Header Requirements

Header should be shared across all pages.

Navigation links:

```text
صفحه اصلی
محصولات
قهوه
هات‌چاکلت
درباره ما
تماس با ما
```

Actions:

```text
جستجو
حساب کاربری
سبد خرید
```

For static templates, links can be placeholder `href="#"` or static paths. Later they become `{% url %}` tags.

Use accessible buttons:

```html
<button class="icon-btn mobile-menu-toggle" type="button" aria-label="باز کردن منو" aria-expanded="false">
```

---

## Main CSS Requirement

All CSS goes here:

```text
static/css/main.css
```

This file must contain all global styles, components, and page styles.

Do not create:

```text
home.css
products.css
cart.css
checkout.css
```

When a new page is created, add its styles to the relevant section inside `main.css`.

Recommended section comments:

```css
/* ===============================
   01. Font Face
================================ */

/* ===============================
   02. Tokens
================================ */

/* ===============================
   03. Base / Reset
================================ */

/* ===============================
   04. Layout Utilities
================================ */

/* Continue... */
```

---

## Main JS Requirement

All JavaScript goes here:

```text
static/js/main.js
```

This file should initialize only the behavior that exists on the current page.

Use defensive selectors:

```js
const drawer = document.querySelector('[data-mobile-drawer]');
if (!drawer) return;
```

Do not throw errors on pages that do not have a specific component.

Recommended JS modules/functions inside the same file:

```text
initHeaderScroll()
initMobileDrawer()
initSearchPanel()
initProductGallery()
initQuantityControls()
initCartItemRemoveMock()
initCheckoutSteps()
initAccordions()
initTabs()
initFormValidationMock()
```

No external libraries unless later approved.

---

## Static-to-Dynamic Template Strategy

Write static HTML now in a way that is easy to replace later.

Static product card now:

```html
<article class="product-card">
  <a class="product-card-image" href="#">
    <img src="{% static 'images/products/coffee-01.png' %}" alt="بسته قهوه عربیکا">
  </a>
  <div class="product-card-body">
    <p class="product-card-meta">قهوه • ۲۵۰ گرم</p>
    <h3 class="product-card-title">قهوه عربیکا ویژه</h3>
    <div class="product-card-price-row">
      <span class="product-price">۳۲۰٬۰۰۰ تومان</span>
      <a class="btn btn-sm btn-primary" href="#">مشاهده</a>
    </div>
  </div>
</article>
```

Later dynamic version:

```django
{% for product in products %}
  {% include 'partials/product_card.html' with product=product %}
{% endfor %}
```

Keep class names identical between static and dynamic versions.

---

## Page Build Order

Recommended implementation order:

1. `base.html`
2. `partials/header.html`
3. `partials/footer.html`
4. `partials/mobile_drawer.html`
5. `pages/home.html`
6. `products/product_list.html`
7. `products/product_detail.html`
8. `cart/cart.html`
9. `checkout/checkout.html`
10. `checkout/payment_success.html`
11. `checkout/payment_failed.html`
12. `accounts/login.html`
13. `accounts/profile.html`
14. `pages/about.html`
15. `pages/contact.html`
16. `pages/faq.html`

---

## Home Page Static Sections

`pages/home.html` should include:

```text
1. Hero
2. Category highlights
3. Featured products
4. About/brand teaser
5. Wholesale/contact form teaser
```

Keep it compact.

Do not add a large video section in the first version.

---

## Product List Static Sections

`products/product_list.html` should include:

```text
1. Page title
2. Short intro
3. Search/filter row
4. Category chips
5. Product grid
6. Pagination placeholder
```

Filters can be static buttons for now.

---

## Product Detail Static Sections

`products/product_detail.html` should include:

```text
1. Breadcrumbs
2. Gallery
3. Product title and price
4. Short description
5. Quantity selector
6. Add to cart button
7. Product details
8. Related products
```

Gallery behavior can be handled by `main.js`.

---

## Cart Static Sections

`cart/cart.html` should include:

```text
1. Page title
2. Cart item list
3. Quantity controls
4. Summary card
5. Checkout CTA
6. Empty cart state markup hidden or separate
```

Use static quantities and totals for now.

---

## Checkout Static Sections

`checkout/checkout.html` should include:

```text
1. Contact information
2. Shipping address
3. Shipping method
4. Payment method
5. Order summary
6. Submit button
```

No backend validation yet, but HTML labels and required attributes should be present.

---

## Payment Pages

Create separate static templates:

```text
checkout/payment_success.html
checkout/payment_failed.html
```

Each should include:

- Result icon/visual
- Clear title
- Short explanation
- Order number placeholder
- CTA back to products or orders

---

## Account Pages

Static account pages can be simple.

### Login

- Phone number field
- Submit button
- Small trust/help text

### OTP

- OTP input boxes or one input
- Resend placeholder

### Profile

- User info card
- Address list placeholder
- Recent orders placeholder

---

## Forms and Backend Readiness

All forms should use semantic HTML now.

Even before backend connection:

- Add `method="post"` only if the form is meant to submit later.
- Use `name` attributes.
- Use labels.
- Use `required` where appropriate.
- Leave `{% csrf_token %}` commented or included if the template will soon become functional.

Example:

```django
<form class="form-card" method="post" action="#">
  {# {% csrf_token %} #}
  <div class="form-field">
    <label class="form-label" for="full_name">نام و نام خانوادگی</label>
    <input class="form-input" id="full_name" name="full_name" type="text" required>
  </div>
</form>
```

---

## Accessibility Checklist

Every template should check:

- `<html lang="fa" dir="rtl">`
- Images have Persian `alt` text.
- Buttons have text or `aria-label`.
- Mobile menu button uses `aria-expanded`.
- Drawer can be closed with Escape.
- Form inputs have labels.
- Focus states are visible.
- Links have meaningful text.
- No empty clickable divs.

---

## Naming Convention

Use readable kebab-case CSS class names.

Good:

```text
product-card
cart-summary
checkout-section
mobile-drawer
```

Avoid:

```text
box1
right-side
my-style
page-new-final
```

Use `is-` and `has-` states:

```text
is-active
is-open
is-loading
has-error
```

Use `data-*` attributes for JavaScript hooks:

```html
<button data-quantity-plus>
<div data-mobile-drawer>
```

Do not use CSS class names only as JS hooks if avoidable.

---

## Sample Static URLs

During static stage, links can be simple:

```html
<a href="/products/">محصولات</a>
<a href="/products/sample-product/">مشاهده محصول</a>
<a href="/cart/">سبد خرید</a>
<a href="/checkout/">تکمیل خرید</a>
```

Later replace with:

```django
{% url 'products:list' %}
{% url 'products:detail' product.slug %}
{% url 'cart:detail' %}
{% url 'checkout:start' %}
```

---

## Development Standard

Before creating any new page:

1. Read `PRODUCT.md`.
2. Read `DESIGN.md`.
3. Read `IMPLEMENTATION.md`.
4. Follow `HANDOFF.md` rules.
5. Add CSS only to `main.css`.
6. Add JS only to `main.js`.
7. Keep page Persian and RTL.
8. Keep page minimal.
