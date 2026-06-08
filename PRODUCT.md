# Product — Persian RTL Coffee & Hot Chocolate Shop

## Project in One Sentence

A minimal Persian/RTL Django storefront for coffee, tea, hot chocolate, and related packaged products. The first implementation uses static Django templates, plain CSS, and plain JavaScript; later it will be connected to backend models, cart, checkout, and payment.

---

## Current Stage

This project is currently a **static-template practice project**.

That means:

- Templates should look like the final website, but product data can be hard-coded placeholder content for now.
- The HTML should be written in a way that can later be converted to Django loops and dynamic context variables.
- Cart, checkout, payment, account, and order pages are part of the planned structure even if they are not connected to backend yet.
- All styling belongs in `static/css/main.css`.
- All JavaScript behavior belongs in `static/js/main.js`.
- Do not create page-specific CSS or page-specific JS unless the user explicitly changes this rule later.

---

## Brand Status

The final brand name is not fixed yet.

Use neutral placeholder naming in templates and copy when needed:

- فارسی: `نام برند`
- English/internal: `Coffee Brand`

Do not invent a permanent brand name unless the user asks for one.

---

## Product Category

The website sells packaged warm-drink products, mainly:

- قهوه
- چای
- هات‌چاکلت
- پودرهای فوری
- بسته‌های هدیه
- محصولات ویژه یا پرفروش

The visual identity should suit premium packaging, especially coffee bags, coffee cans, hot chocolate boxes, and gift packs.

---

## Product Purpose

The website should help users:

1. Quickly understand the brand feeling.
2. Browse products without visual noise.
3. View product details clearly.
4. Add products to cart.
5. Continue to checkout.
6. Complete payment or see payment result.
7. Contact the brand for wholesale or consultation requests.

The project should feel like a real e-commerce website, but stay simple enough for a clean Django practice implementation.

---

## Main Users

Primary users:

- Persian-speaking customers browsing from mobile.
- People buying coffee or hot chocolate for home, work, or gifts.
- Customers who care about packaging, taste, trust, and price clarity.
- Potential wholesale buyers who may want to submit a form.

Assume mobile-first behavior. Many users may arrive from Instagram, ads, or direct links.

---

## Register

The website register is:

```text
brand + product clarity
```

Landing and about pages can be more emotional and brand-led.

Catalog, product detail, cart, checkout, and payment pages must prioritize clarity, speed, and trust.

---

## Brand Personality

The personality should be:

- Minimal
- Warm
- Premium
- Ordered
- Trustworthy
- Calm

It should not feel loud, crowded, cheap, or like a generic marketplace.

---

## Visual Reference

The Danidor website is a **mood reference**, not a layout to copy.

Use the reference for:

- Coffee/tea product mood
- Warm visual identity
- Product-focused sections
- Persian RTL interface
- Landing page structure inspiration

Do not copy:

- Exact layout
- Exact proportions
- Exact images
- Exact text
- Crowded product blocks
- Oversized sections
- Video-heavy layout unless requested later

The target project should be simpler, cleaner, smaller, and more minimal.

---

## Core Experience Principle

```text
Let the product packaging stand out. Keep everything else calm.
```

The background should be warm and quiet. Cards should be white. Text should be dark chocolate. CTAs should be strong but compact. Accent gold should be used lightly.

---

## Anti-References

Avoid these directions:

- Crowded homepage with too many competing sections.
- Large oversized hero that dominates the whole experience.
- Excessive sliders, banners, badges, and decorations.
- Heavy black-and-gold luxury cliché.
- Marketplace-style product grid with too much metadata.
- Cold corporate minimalism with no warmth.
- External CDN dependencies.
- Separate CSS files for each page.
- Separate JS files for each page.

---

## Content Language Rules

The entire visible website must be:

- Persian
- RTL
- Natural-sounding, not translated word-for-word
- Concise
- Calm and confident

Use Persian numerals where appropriate, especially for prices and quantities.

Examples of suitable copy tone:

```text
طعمی گرم برای لحظه‌های آرام‌تر
قهوه، چای و هات‌چاکلت با بسته‌بندی مرتب و انتخابی ساده برای خانه و محل کار.
```

```text
محصولات منتخب
چند انتخاب محبوب برای شروع یک روز گرم و خوش‌طعم.
```

```text
درخواست خرید عمده یا مشاوره
فرم را تکمیل کنید تا برای انتخاب محصول مناسب با شما تماس بگیریم.
```

---

## Primary User Journeys

### Journey 1 — Browse and Buy

1. User lands on homepage.
2. Sees hero and featured products.
3. Opens products page.
4. Filters or selects category.
5. Opens product detail.
6. Adds product to cart.
7. Goes to cart.
8. Continues to checkout.
9. Enters information.
10. Goes to payment.
11. Sees payment result.

### Journey 2 — Product Detail First

1. User arrives from direct product link.
2. Reviews images, price, weight, and short details.
3. Adds to cart.
4. Completes checkout.

### Journey 3 — Wholesale / Consultation

1. User scrolls to inquiry section or contact page.
2. Completes form.
3. Sees confirmation message.

---

## Required Pages

The full planned structure includes:

### Public Pages

- Home / Landing
- Products List
- Product Detail
- Category Page
- About
- Contact
- FAQ
- Terms / Privacy

### Commerce Pages

- Cart
- Checkout
- Payment Gateway Redirect Placeholder
- Payment Success
- Payment Failed
- Order Tracking / Order Detail

### Account Pages

- Login / Register
- OTP Verification
- Profile
- Addresses
- Orders

The first design implementation may start with Home, Products, Product Detail, Cart, Checkout, and Payment Result as static templates.

---

## Homepage Structure

Keep the homepage compact and minimal.

Recommended order:

1. Header
2. Hero
3. Category highlights
4. Featured products
5. About / brand teaser
6. Wholesale or consultation form
7. Footer

Optional later sections:

- Best sellers
- New products
- Gift packs
- Short video/story section
- Blog/education teaser

Do not add optional sections unless the page still feels calm and spacious.

---

## Product Data Needed Later

Each product should eventually support:

- Name
- Slug
- Category
- Main image
- Gallery images
- Short description
- Full description
- Price
- Weight
- SKU
- Stock status
- Featured flag
- Active flag
- Optional tags: پرفروش، جدید، ویژه

For static templates, hard-code sample values but structure the HTML so later replacement is easy.

---

## Product Card Rules

Product cards should show only essential information:

- Product image
- Product name
- Short category or weight
- Price
- Compact CTA

Avoid overloading product cards with too many labels, ratings, descriptions, or icons.

---

## Trust Signals

Use subtle trust signals, not noisy badges.

Good examples:

- ارسال مطمئن
- پرداخت امن
- بسته‌بندی مرتب
- پشتیبانی خرید
- مناسب مصرف روزانه و هدیه

Place them as small cards or a quiet row, not loud banners.

---

## Accessibility and Usability

Minimum expectations:

- RTL everywhere.
- Keyboard navigable menus and forms.
- Buttons and links have clear focus states.
- Sufficient contrast between text and background.
- Product images have Persian `alt` text.
- Forms have labels, not only placeholders.
- Motion respects `prefers-reduced-motion`.
- Mobile navigation must be easy to use with one hand.

---

## Success Criteria

A page is successful when:

- It feels premium but simple.
- The product image is the visual focus.
- The user can understand the next action quickly.
- The layout is not crowded.
- The page works well on mobile.
- It can later be connected to Django backend without rewriting the whole template.
