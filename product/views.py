from django.db.models import Exists, OuterRef, Prefetch, Subquery
from django.views.generic import ListView, View

from .filters import ProductFilter
from .models import Product, ProductCategory, ProductVariant


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
                "categories": ProductCategory.objects.filter(is_active=True).order_by("title"),
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


class ProductDetailView(View):
    template_name = 'product/product_detail.html'

    def get(self, request):
        return render(request, self.template_name)