from django.db.models import Exists, OuterRef, Prefetch, Subquery
from django.views.generic import ListView, DetailView, CreateView
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductAttribute,
    ProductReview,
    ProductCategory,
)
from .filters import ProductFilter
from .forms import ProductReviewForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .cache import get_cached_active_product_categories


class ProductListView(ListView):
    model = Product
    template_name = "product/product_list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_base_queryset(self):
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
            .order_by("-created_at")
        )

    def get_queryset(self):
        queryset = self.get_base_queryset()

        self.filterset = ProductFilter(
            data=self.request.GET or None,
            queryset=queryset,
        )

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        filter_params = self.request.GET.copy()
        for key in ["page", "sort"]:
            filter_params.pop(key, None)

        total_count = context["paginator"].count

        if total_count:
            page_start_index = context["page_obj"].start_index()
            page_end_index = context["page_obj"].end_index()
        else:
            page_start_index = 0
            page_end_index = 0

        context.update(
            {
                "filterset": self.filterset,

                # Cached with Redis
                "categories": get_cached_active_product_categories(),

                "selected_category_slugs": self.request.GET.getlist("category"),
                "available_selected": self.request.GET.get("available") in ["1", "true", "True", "on"],
                "price_min_value": self.request.GET.get("price_min", ""),
                "price_max_value": self.request.GET.get("price_max", ""),
                "current_sort": self.request.GET.get("sort", "newest"),
                "querystring": query_params.urlencode(),
                "has_filter_values": bool(filter_params),
                "total_count": total_count,
                "page_start_index": page_start_index,
                "page_end_index": page_end_index,
            }
        )

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "product/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        active_variants = (
            ProductVariant.objects
            .filter(is_active=True)
            .select_related("weight")
            .order_by("weight__value_grams")
        )

        product_images = (
            ProductImage.objects
            .select_related("variant")
            .order_by("-is_main", "created_at")
        )

        approved_reviews = (
            ProductReview.objects
            .filter(status=ProductReview.Status.APPROVED)
            .select_related("user")
            .order_by("-created_at")
        )

        return (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                Prefetch("variants", queryset=active_variants),
                Prefetch("images", queryset=product_images),
                Prefetch(
                    "attributes",
                    queryset=ProductAttribute.objects.order_by("created_at"),
                ),
                Prefetch(
                    "reviews",
                    queryset=approved_reviews,
                    to_attr="approved_reviews",
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.object

        variants = list(product.variants.all())

        default_variant = (
            next((variant for variant in variants if variant.is_default), None)
            or variants[0] if variants else None
        )

        gallery_images = list(product.images.all())

        related_products = (
            Product.objects
            .filter(
                is_active=True,
                category=product.category,
            )
            .exclude(pk=product.pk)
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects
                    .filter(is_active=True)
                    .select_related("weight"),
                )
            )
            .order_by("-is_featured", "-created_at")[:4]
        )

        approved_reviews = getattr(product, "approved_reviews", [])

        context.update(
            {
                "variants": variants,
                "default_variant": default_variant,
                "gallery_images": gallery_images,
                "attributes": product.attributes.all(),
                "reviews": approved_reviews,
                "review_count": len(approved_reviews),
                "related_products": related_products,
            }
        )

        return context


class ProductReviewCreateView(CreateView):
    model = ProductReview
    form_class = ProductReviewForm
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product,
            slug=kwargs["slug"],
            is_active=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product = self.product
        review.status = ProductReview.Status.PENDING

        if self.request.user.is_authenticated:
            review.user = self.request.user

        review.save()

        messages.success(
            self.request,
            "دیدگاه شما ثبت شد و پس از تأیید نمایش داده می‌شود."
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            "ثبت دیدگاه انجام نشد. لطفاً نام، نام خانوادگی و متن دیدگاه را درست وارد کنید."
        )

        return redirect(self.get_success_url())

    def get_success_url(self):
        return (
            reverse(
                "product:product-detail",
                kwargs={"slug": self.product.slug},
            )
            + "#product-comments"
        )