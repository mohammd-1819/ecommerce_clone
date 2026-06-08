# Design — Minimal Warm Coffee Store

## Design Direction

The website should feel:

```text
لوکس، مرتب، گرم، خلوت، مناسب بسته‌بندی‌های قهوه و هات‌چاکلت
```

The design should be product-focused. The warm cream background should make product photography stand out. White cards should keep the interface clean. Dark chocolate text and buttons should create a premium feeling. Soft gold should be an accent, not the main visual mass.

---

## Color System

Use this palette as the foundation of the entire project.

| Token | Name | Value | Usage |
|---|---|---:|---|
| `--color-bg` | شیری گرم | `#F6F2EC` | Main page background, warm empty space |
| `--color-surface` | سفید خالص | `#FFFFFF` | Cards, forms, dropdowns, header |
| `--color-text` | شکلاتی خیلی تیره | `#181512` | Main text, headings |
| `--color-primary` | کاکائویی تیره | `#3A2A21` | Primary buttons, footer, strong UI elements |
| `--color-accent` | طلایی ملایم | `#D6A95F` | Small accents, prices, lines, badges |

Extended tokens allowed in `main.css`:

```css
:root {
  --color-bg: #F6F2EC;
  --color-surface: #FFFFFF;
  --color-text: #181512;
  --color-primary: #3A2A21;
  --color-accent: #D6A95F;

  --color-primary-hover: #2B1F18;
  --color-muted: #6D625C;
  --color-muted-2: #8B817A;
  --color-border: #E7DED2;
  --color-border-strong: #D8C9B8;
  --color-accent-soft: #EFE1CA;
  --color-danger: #B84A3E;
  --color-success: #3B7C5C;

  --shadow-soft: 0 14px 35px rgba(24, 21, 18, 0.08);
  --shadow-hover: 0 18px 45px rgba(24, 21, 18, 0.12);
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-pill: 999px;

  --container: 1120px;
  --transition: 180ms ease;
  --font-main: 'Vazir', sans-serif;
}
```

### Color Rules

Do:

- Use `#F6F2EC` as the main quiet background.
- Use white cards for products and forms.
- Use `#3A2A21` for primary CTAs.
- Use `#D6A95F` for small highlights, price accents, dividers, active states, and small decorative marks.

Do not:

- Use gold as a large section background.
- Use many accent elements in the same viewport.
- Create heavy black/gold luxury sections.
- Add unrelated colors unless they are semantic states: success, error, warning.

---

## Typography

Use **Vazir** across the whole website.

The font must be self-hosted from `static/fonts`.

Recommended `@font-face`:

```css
@font-face {
  font-family: 'Vazir';
  src: url('../fonts/Vazir.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

If only separate font weights exist, define separate `@font-face` declarations for regular, medium, bold, and black.

### Type Scale

Keep text compact. Do not make sections oversized.

| Role | Weight | Desktop Size | Mobile Size | Notes |
|---|---:|---:|---:|---|
| Body | 400 | `0.95rem` | `0.92rem` | Line-height `1.9` |
| Small | 400 | `0.82rem` | `0.78rem` | Labels, meta |
| Nav | 500 | `0.9rem` | `0.9rem` | Compact |
| Card Title | 700 | `1rem` | `0.95rem` | No long lines |
| Section Eyebrow | 600 | `0.85rem` | `0.8rem` | Accent color |
| Section Title | 800 | `1.8rem` | `1.35rem` | Restrained |
| Hero Title | 900 | `2.45rem` max | `1.65rem` | Use `clamp()` |

Recommended CSS:

```css
body {
  font-family: var(--font-main);
  font-size: 15.5px;
  line-height: 1.9;
  color: var(--color-text);
  background: var(--color-bg);
  direction: rtl;
  text-align: right;
}
```

---

## Spacing System

Use consistent spacing and avoid large empty hero sections.

Spacing scale:

```text
4px · 8px · 12px · 16px · 20px · 24px · 32px · 40px · 56px · 72px
```

Recommended section padding:

```css
.section {
  padding: 56px 0;
}

@media (max-width: 768px) {
  .section {
    padding: 40px 0;
  }
}
```

Hero should be visually strong but not huge:

```css
.hero {
  min-height: 440px;
  padding: 56px 0 48px;
}
```

Mobile hero should stack cleanly and stay compact.

---

## Layout

Use one shared container class:

```css
.container {
  width: min(100% - 32px, var(--container));
  margin-inline: auto;
}
```

General layout rules:

- Use CSS Grid for product lists and cart/checkout layouts.
- Use Flexbox for header, buttons, and small rows.
- Avoid complex nested layouts unless necessary.
- Keep max-width under control so Persian text is readable.

---

## Border Radius

The design can be soft, but not bubbly.

| Element | Radius |
|---|---:|
| Small buttons | `999px` or `12px` depending context |
| Product cards | `18px` |
| Forms | `18px` |
| Inputs | `12px` |
| Hero media card | `28px` |
| Product image wrapper | `16px` |
| Modals/drawers | `22px` |

Use rounded corners to soften the warm premium feel, but keep card proportions clean.

---

## Shadows

Use shadows lightly.

```css
--shadow-soft: 0 14px 35px rgba(24, 21, 18, 0.08);
--shadow-hover: 0 18px 45px rgba(24, 21, 18, 0.12);
```

Rules:

- Product cards can lift slightly on hover.
- Header can get a subtle shadow after scroll.
- Do not use heavy black shadows.

---

## Header

Header should be minimal and sticky.

Desktop structure:

```text
[ Logo / Brand ] [ Nav links ] [ Search ] [ Account ] [ Cart ]
```

Mobile structure:

```text
[ Menu button ] [ Brand ] [ Cart ]
```

Required classes:

```text
.site-header
.header-inner
.brand-link
.main-nav
.nav-link
.header-actions
.icon-btn
.cart-count
.mobile-menu-toggle
.mobile-drawer
.mobile-drawer-backdrop
```

Header rules:

- Background: `var(--color-surface)` with slight transparency optional.
- Border-bottom: `1px solid var(--color-border)`.
- Height: compact, around `72px` desktop and `64px` mobile.
- Active nav link gets a small gold underline or dot.
- Do not add a crowded top bar unless later requested.

---

## Hero

Hero direction:

- Warm background.
- Text on one side, product image on the other.
- No full-screen height.
- No busy background.
- Product image should be the focus.

Recommended structure:

```text
[ Persian headline + short paragraph + CTA row ] [ Product image / package visual ]
```

Required classes:

```text
.hero
.hero-grid
.hero-content
.hero-eyebrow
hero-title
hero-text
hero-actions
hero-media
hero-image-card
hero-badge
```

Recommended copy style:

```text
قهوه‌ای برای لحظه‌های آرام‌تر
طعم گرم، بسته‌بندی مرتب، انتخابی ساده برای خانه و محل کار.
```

Hero button row:

- Primary: مشاهده محصولات
- Secondary: درخواست خرید عمده

---

## Category Section

Purpose: quick browsing.

Recommended categories:

- قهوه
- چای
- هات‌چاکلت
- بسته‌های هدیه

Required classes:

```text
.category-grid
.category-card
category-icon
category-title
category-text
```

Rules:

- Cards should be small and calm.
- Use line art or simple product images.
- No large icons.
- Four cards maximum on the homepage.

---

## Product Cards

Required classes:

```text
.product-grid
.product-card
product-card-image
product-card-body
product-card-meta
product-card-title
product-card-price-row
product-price
product-old-price
product-card-actions
```

Product card layout:

```text
[ Image ]
[ Category / weight ]
[ Product name ]
[ Price + CTA ]
```

Rules:

- Card background: white.
- Border: `1px solid var(--color-border)`.
- Image ratio: square or `4 / 3` depending product photos.
- Product image should not be cropped badly.
- Keep text short.
- Avoid many badges.
- Use at most one badge per card: جدید / پرفروش / ویژه.

---

## Product List Page

The product list page should prioritize browsing clarity.

Layout:

```text
[ Page title + short text ]
[ Filter/search row ]
[ Product grid ]
```

Optional desktop layout later:

```text
[ Sidebar filters ] [ Product grid ]
```

Keep the first version simple with top filters.

Required classes:

```text
.page-hero
.products-toolbar
filter-chip
sort-select
product-grid
pagination
```

---

## Product Detail Page

Recommended layout:

```text
[ Gallery ] [ Product info ]
```

Required classes:

```text
.product-detail
.product-gallery
.gallery-main
.gallery-thumbs
.product-info
product-title
product-meta-list
product-price-large
quantity-control
add-to-cart-form
product-tabs
```

Product detail must show:

- Name
- Category
- Weight/package size
- Price
- Short description
- Quantity selector
- Add to cart button
- Product details tab/section

---

## Cart Page

Required classes:

```text
.cart-layout
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

Rules:

- Cart page must be practical, not decorative.
- Summary box should be sticky on desktop if simple to implement.
- Quantity controls should be compact.
- Empty cart state should be designed.

---

## Checkout Page

Required classes:

```text
.checkout-layout
checkout-form
checkout-section
checkout-summary
payment-methods
shipping-methods
form-grid
form-field
```

Checkout sections:

1. اطلاعات گیرنده
2. آدرس ارسال
3. روش ارسال
4. روش پرداخت
5. خلاصه سفارش

Use clear labels. Do not rely only on placeholders.

---

## Payment Result Pages

Required classes:

```text
.payment-result
payment-icon
payment-title
payment-message
payment-actions
```

Payment success copy example:

```text
پرداخت با موفقیت انجام شد
سفارش شما ثبت شد و جزئیات آن از طریق پیامک ارسال می‌شود.
```

Payment failed copy example:

```text
پرداخت ناموفق بود
در صورت کسر مبلغ، وجه طبق قوانین بانکی بازگشت داده می‌شود.
```

---

## Forms

Required classes:

```text
.form-card
form-grid
form-field
form-label
form-input
form-select
form-textarea
form-help
form-error
```

Rules:

- Labels are required.
- Placeholders should be examples, not replacements for labels.
- Inputs use white or very light background.
- Focus state uses accent outline or border.
- Error state uses danger color.

---

## Buttons

Required classes:

```text
.btn
btn-primary
btn-secondary
btn-ghost
btn-link
btn-sm
btn-lg
btn-block
```

Button rules:

```css
.btn-primary {
  background: var(--color-primary);
  color: var(--color-surface);
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-primary);
  border: 1px solid var(--color-border-strong);
}
```

Use gold for small accent details, not full primary CTA background by default.

---

## Footer

Footer can use the dark cacao color.

Required classes:

```text
.site-footer
footer-grid
footer-brand
footer-links
footer-contact
footer-bottom
```

Footer rules:

- Background: `var(--color-primary)`.
- Text: white or soft cream.
- Accent: small gold lines or icons.
- Keep it compact.

---

## Image Rules

Use images from:

```text
static/images
```

Rules:

- Product image alt text must be Persian.
- Use warm and clean product photos.
- Avoid cluttered lifestyle photos unless used very sparingly.
- Do not stretch images.
- Use `object-fit: contain` for package/product cutouts.
- Use `object-fit: cover` for lifestyle photos.

---

## Motion and Interactions

Keep animations subtle.

Allowed:

- Header shadow on scroll.
- Mobile drawer slide.
- Product card slight hover lift.
- Gallery thumbnail change.
- Quantity button updates.
- Accordion open/close.

Avoid:

- Heavy scroll animations.
- Autoplay sliders unless requested.
- Multiple moving sections.
- Fast or flashy transitions.

Reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
}
```

---

## Responsive Rules

Breakpoints:

```css
--bp-sm: 480px;
--bp-md: 768px;
--bp-lg: 1024px;
--bp-xl: 1200px;
```

Practical media queries:

```css
@media (max-width: 1024px) { }
@media (max-width: 768px) { }
@media (max-width: 480px) { }
```

Rules:

- Mobile-first behavior must be clean.
- Header nav collapses to drawer.
- Product grids go to 2 columns, then 1 column when needed.
- Cart and checkout become single-column.
- Hero stacks with text first, image second unless design requires otherwise.

---

## Page Density Rules

The user specifically does not want large or crowded pages.

Therefore:

- Keep section padding moderate.
- Do not show more than 4 featured products in one homepage row.
- Do not show more than 4 category cards on homepage.
- Avoid long paragraphs.
- Avoid decorative clutter.
- Avoid large background patterns.
- One main CTA per section is enough.

---

## CSS Organization Requirement

All site CSS must live in:

```text
static/css/main.css
```

No page-specific CSS files.

Recommended order inside `main.css`:

```text
1. Font face
2. CSS variables
3. Reset/base
4. Typography
5. Layout utilities
6. Buttons
7. Forms
8. Header/mobile drawer
9. Footer
10. Shared cards/components
11. Home page
12. Product list
13. Product detail
14. Cart
15. Checkout
16. Payment result
17. Account pages
18. Responsive rules
19. Reduced motion
```

When adding new page styles, append them in the correct section of `main.css` and keep class names consistent.
