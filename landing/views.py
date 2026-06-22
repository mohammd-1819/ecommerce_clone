from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .forms import ContactRequestForm
from .models import ContactRequest
from urllib.parse import urlencode
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse
from django.db.models import (
    Q,
    Count,
    Case,
    When,
    Value,
    IntegerField,
    OuterRef,
    Subquery,
    Prefetch,
)


from product.models import Product, ProductVariant, ProductCategory




class LandingView(TemplateView):
    template_name = "landing/home.html"

    def get_popular_products_queryset(self):
        active_variants = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
        ).order_by(
            "-is_default",
            "weight__value_grams",
            "created_at",
        )

        prefetch_active_variants = Prefetch(
            "variants",
            queryset=ProductVariant.objects.filter(is_active=True)
            .select_related("weight")
            .order_by("-is_default", "weight__value_grams"),
        )

        return (
            Product.objects.filter(
                is_active=True,
                is_featured=True,
                category__is_active=True,
            )
            .select_related("category")
            .prefetch_related(prefetch_active_variants)
            .annotate(
                list_price_toman=Subquery(
                    active_variants.values("price_toman")[:1]
                ),
                list_weight_title=Subquery(
                    active_variants.values("weight__title")[:1]
                ),
            )
            .filter(list_price_toman__isnull=False)
            .order_by("-order_counter", "-created_at")[:4]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["popular_products"] = self.get_popular_products_queryset()

        return context



class AboutView(View):
    template_name = 'landing/about.html'

    def get(self, request):
        return render(request, self.template_name)



class ContactRequestCreateView(CreateView):
    model = ContactRequest
    form_class = ContactRequestForm
    template_name = "landing/contact.html"
    success_url = reverse_lazy("landing:contact")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "پیام شما با موفقیت ثبت شد. در اولین فرصت با شما تماس می‌گیریم.",
        )

        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "لطفاً خطاهای فرم را بررسی و دوباره ارسال کنید.",
        )

        return super().form_invalid(form)


PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def toman_label(value):
    if value is None:
        return ""
    return f"{format(value, ',').translate(PERSIAN_DIGITS)} تومان"


class ProductSearchModalView(View):
    """
    JSON endpoint for the existing header search modal.

    GET params:
      q: search text
      limit: product limit, optional
    """

    default_product_limit = 6
    max_product_limit = 12

    def get(self, request, *args, **kwargs):
        query = (request.GET.get("q") or request.GET.get("search") or "").strip()
        limit = self.get_limit()

        products = self.get_products(query)[:limit]
        categories = self.get_categories(query)

        return JsonResponse(
            {
                "query": query,
                "has_query": bool(query),
                "heading": "نتایج جستجو" if query else "پیشنهادهای محبوب",
                "empty_message": "محصولی با این عبارت پیدا نشد.",
                "categories": [self.serialize_category(category, query) for category in categories],
                "products": [self.serialize_product(product) for product in products],
            },
            json_dumps_params={"ensure_ascii": False},
        )

    def get_limit(self):
        try:
            limit = int(self.request.GET.get("limit", self.default_product_limit))
        except (TypeError, ValueError):
            limit = self.default_product_limit

        return min(max(limit, 1), self.max_product_limit)

    def get_active_variant_subquery(self):
        return ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            weight__is_active=True,
        ).order_by(
            "-is_default",
            "weight__value_grams",
            "created_at",
        )

    def get_base_products_queryset(self):
        active_variants = self.get_active_variant_subquery()

        return (
            Product.objects.filter(
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
            .annotate(
                search_price_toman=Subquery(
                    active_variants.values("price_toman")[:1]
                ),
                search_weight_title=Subquery(
                    active_variants.values("weight__title")[:1]
                ),
            )
            .filter(search_price_toman__isnull=False)
        )

    def get_products(self, query):
        queryset = self.get_base_products_queryset()

        if query:
            queryset = (
                queryset.filter(
                    Q(title__icontains=query)
                    | Q(short_description__icontains=query)
                    | Q(description__icontains=query)
                    | Q(base_sku__icontains=query)
                    | Q(category__title__icontains=query)
                    | Q(category__slug__icontains=query)
                    | Q(variants__sku__icontains=query, variants__is_active=True)
                    | Q(
                        variants__weight__title__icontains=query,
                        variants__is_active=True,
                        variants__weight__is_active=True,
                    )
                )
                .annotate(
                    search_priority=Case(
                        When(title__icontains=query, then=Value(0)),
                        When(category__title__icontains=query, then=Value(1)),
                        When(short_description__icontains=query, then=Value(2)),
                        default=Value(3),
                        output_field=IntegerField(),
                    )
                )
                .order_by(
                    "search_priority",
                    "-is_featured",
                    "-order_counter",
                    "-created_at",
                )
                .distinct()
            )
        else:
            queryset = queryset.order_by(
                "-is_featured",
                "-order_counter",
                "-created_at",
            )

        return queryset

    def get_categories(self, query):
        queryset = (
            ProductCategory.objects.filter(is_active=True)
            .annotate(
                active_product_count=Count(
                    "products",
                    filter=Q(
                        products__is_active=True,
                        products__variants__is_active=True,
                        products__variants__weight__is_active=True,
                    ),
                    distinct=True,
                )
            )
            .filter(active_product_count__gt=0)
        )

        if query:
            queryset = queryset.annotate(
                category_priority=Case(
                    When(title__icontains=query, then=Value(0)),
                    When(slug__icontains=query, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("category_priority", "title")
        else:
            queryset = queryset.order_by("title")

        return queryset

    def serialize_product(self, product):
        return {
            "id": product.id,
            "title": product.title,
            "slug": product.slug,
            "url": self.get_product_url(product),
            "image_url": self.get_product_image_url(product),
            "category": {
                "id": product.category_id,
                "title": product.category.title,
                "slug": product.category.slug,
            },
            "variant": {
                "weight_title": product.search_weight_title,
            },
            "meta_label": self.get_product_meta_label(product),
            "price_toman": product.search_price_toman,
            "price_label": toman_label(product.search_price_toman),
        }

    def serialize_category(self, category, query):
        return {
            "id": category.id,
            "title": category.title,
            "slug": category.slug,
            "url": self.get_category_url(category),
            "product_count": category.active_product_count,
            "is_match": bool(
                query
                and (
                    query in category.title
                    or query in category.slug
                )
            ),
        }

    def get_product_meta_label(self, product):
        parts = [
            product.category.title,
            product.search_weight_title,
        ]
        return "، ".join([part for part in parts if part])

    def get_product_image_url(self, product):
        if not product.main_image:
            return ""

        return self.request.build_absolute_uri(product.main_image.url)

    def get_product_url(self, product):
        if hasattr(product, "get_absolute_url"):
            return product.get_absolute_url()

        try:
            return reverse("product:product-detail", kwargs={"slug": product.slug})
        except NoReverseMatch:
            return "#"

    def get_category_url(self, category):
        try:
            product_list_url = reverse("product:product-list")
        except NoReverseMatch:
            product_list_url = "/products/"

        return f"{product_list_url}?{urlencode({'category': category.slug})}"