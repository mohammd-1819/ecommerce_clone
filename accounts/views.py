from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Sum, Value, IntegerField
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from order.models import Order, OrderItem




class UserOrderListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_orders.html"

    current_statuses = [
        Order.Status.PENDING_PAYMENT,
        Order.Status.PAID,
        Order.Status.PREPARING,
        Order.Status.SHIPPED,
    ]

    completed_statuses = [
        Order.Status.DELIVERED,
        Order.Status.CANCELLED,
        Order.Status.REFUNDED,
    ]

    def get_base_queryset(self):
        order_items_queryset = (
            OrderItem.objects
            .select_related("product", "variant")
            .order_by("id")
        )

        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related(
                "payment_method",
                "coupon",
                "address",
            )
            .prefetch_related(
                Prefetch("items", queryset=order_items_queryset)
            )
            .annotate(
                items_count=Coalesce(
                    Sum("items__quantity"),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = self.get_base_queryset()

        context["current_orders"] = orders.filter(
            status__in=self.current_statuses
        )

        context["completed_orders"] = orders.filter(
            status__in=self.completed_statuses
        )

        return context



class ProfileDashboardView(View):
    template_name = 'accounts/profile_dashboard.html'

    def get(self, request):
        return render(request, self.template_name)



class ProfileAddressView(View):
    template_name = 'accounts/profile_address.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileCommentsView(View):
    template_name = 'accounts/profile_comments.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileEditView(View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        return render(request, self.template_name)
