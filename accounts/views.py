from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Sum, Value, IntegerField
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from order.models import Order, OrderItem
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from .forms import UserAddressForm
from .models import UserAddress
from product.models import ProductReview



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




class ProfileAddressView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_address.html"
    success_url = reverse_lazy("accounts:profile-address")
    # login_url = reverse_lazy("account:login")  # adjust if needed

    def get_queryset(self):
        return UserAddress.objects.filter(
            user=self.request.user,
        ).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        addresses = self.get_queryset()
        last_address = addresses.first()

        context.update(
            {
                "addresses": addresses,
                "address_form": UserAddressForm(user=self.request.user),
                "addresses_count": addresses.count(),
                "last_city": last_address.city if last_address else None,
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "save")

        if action == "delete":
            return self._delete_address(request)

        return self._save_address(request)

    def _save_address(self, request):
        address_id = request.POST.get("address_id")
        instance = None
        is_create = True

        if address_id:
            instance = get_object_or_404(
                UserAddress,
                pk=address_id,
                user=request.user,
            )
            is_create = False

        form = UserAddressForm(
            request.POST,
            user=request.user,
            instance=instance,
        )

        if not form.is_valid():
            return self._respond_invalid(request, form=form)

        address = form.save()

        return self._respond_save_success(
            request=request,
            address=address,
            is_create=is_create,
        )

    def _delete_address(self, request):
        address_id = request.POST.get("address_id")

        if not address_id:
            return self._respond_invalid(
                request,
                message="آدرس موردنظر برای حذف مشخص نیست.",
            )

        address = get_object_or_404(
            UserAddress,
            pk=address_id,
            user=request.user,
        )

        deleted_id = address.pk
        address.delete()

        return self._respond_delete_success(
            request=request,
            deleted_id=deleted_id,
        )

    def _wants_json(self, request):
        return (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("accept", "")
        )

    def _get_first_form_error(self, form):
        first_error = "لطفاً اطلاعات آدرس را بررسی کنید."

        for field_errors in form.errors.values():
            if field_errors:
                first_error = field_errors[0]
                break

        return first_error

    def _respond_invalid(self, request, form=None, message=None):
        error_message = message or self._get_first_form_error(form)

        if self._wants_json(request):
            response_data = {
                "ok": False,
                "message": error_message,
            }

            if form is not None:
                response_data["errors"] = form.errors.get_json_data()

            return JsonResponse(response_data, status=400)

        messages.error(request, error_message)
        return redirect(self.success_url)

    def _respond_save_success(self, request, address, is_create):
        message = "آدرس با موفقیت ذخیره شد."

        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "address": self._serialize_address(address),
                    "is_create": is_create,
                }
            )

        messages.success(request, message)
        return redirect(self.success_url)

    def _respond_delete_success(self, request, deleted_id):
        message = "آدرس با موفقیت حذف شد."

        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "deleted_id": deleted_id,
                }
            )

        messages.success(request, message)
        return redirect(self.success_url)

    def _serialize_address(self, address):
        return {
            "id": address.pk,
            "title": address.title or "آدرس من",
            "recipient_name": address.full_name or "",
            "recipient_phone": address.phone_number or "",
            "province": address.province or "",
            "city": address.city or "",
            "postal_code": address.zip_code or "",
            "address_line": address.postal_address or "",

            # Existing model fields, included for display compatibility.
            # This form does not edit them because checkout form does not edit them.
            "plaque_number": address.plaque_number or "",
            "unit": address.unit or "",
        }




class ProfileProductReviewListView(LoginRequiredMixin, ListView):
    model = ProductReview
    template_name = "accounts/profile_comments.html" 
    context_object_name = "reviews"

    def get_queryset(self):
        return (
            ProductReview.objects
            .filter(
                user=self.request.user,
                status=ProductReview.Status.APPROVED,
            )
            .select_related("product")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = self.object_list

        context["reviews_count"] = reviews.count()
        context["reviewed_products_count"] = (
            reviews.values("product_id").distinct().count()
        )
        context["latest_review"] = reviews.first()

        return context



class ProfileDashboardView(View):
    template_name = 'accounts/profile_dashboard.html'

    def get(self, request):
        return render(request, self.template_name)



class ProfileEditView(View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        return render(request, self.template_name)
