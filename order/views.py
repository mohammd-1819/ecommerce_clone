from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from .forms import CheckoutForm, CouponApplyForm, CheckoutAddressForm
from .models import PaymentMethod
from accounts.models import UserAddress  # adjust this import to your project
from .services import (
    build_checkout_summary,
    cart_is_checkout_ready,
    get_active_cart_for_request,
    get_or_create_active_checkout_session,
    summary_to_json,
    validate_coupon_for_cart,
)
from django.db.models import Prefetch, Sum, Value, IntegerField
from django.db.models.functions import Coalesce
from django.http import Http404
from django.views.generic import DetailView
from .models import Order, OrderItem



class CheckoutDetailView(LoginRequiredMixin, FormView):
    template_name = "order/checkout.html"
    form_class = CheckoutForm
    login_url = reverse_lazy("account:login")  # adjust to your auth URL name

    def dispatch(self, request, *args, **kwargs):
        self.cart = get_active_cart_for_request(request)

        if not cart_is_checkout_ready(self.cart):
            messages.warning(request, "سبد خرید شما خالی است.")
            return redirect("cart:cart-detail")

        self.checkout_session = get_or_create_active_checkout_session(
            request=request,
            cart=self.cart,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        This should point to your next payment/order creation step.
        Example:
        return reverse("checkout:payment-start")
        """
        return reverse("checkout:payment-start")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["checkout_session"] = self.checkout_session
        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        if self.checkout_session.selected_address_id:
            initial["shipping_address"] = self.checkout_session.selected_address_id
        else:
            first_address = (
                UserAddress.objects.filter(user=self.request.user)
                .order_by("-id")
                .first()
            )
            if first_address:
                initial["shipping_address"] = first_address.pk

        if self.checkout_session.payment_method_id:
            initial["payment_method"] = self.checkout_session.payment_method.code
        else:
            first_payment_method = (
                PaymentMethod.objects.filter(is_active=True)
                .order_by("id")
                .first()
            )
            if first_payment_method:
                initial["payment_method"] = first_payment_method.code

        initial["shipping_method"] = "post"
        initial["order_note"] = self.checkout_session.note

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        coupon = self.checkout_session.coupon
        summary = build_checkout_summary(self.cart, coupon=coupon)

        context.update(
            {
                "cart": self.cart,
                "checkout_session": self.checkout_session,
                "cart_items": self.cart.items.select_related(
                    "variant",
                    "variant__product",
                    "variant__weight",
                ),
                "addresses": UserAddress.objects.filter(
                    user=self.request.user
                ).order_by("-id"),
                "payment_methods": PaymentMethod.objects.filter(
                    is_active=True
                ).order_by("id"),
                "summary": summary,
                "coupon_form": CouponApplyForm(
                    initial={
                        "coupon_code": coupon.code if coupon else "",
                    }
                ),
            }
        )

        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "اطلاعات ارسال ذخیره شد.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً اطلاعات تکمیل خرید را بررسی کنید.")
        return super().form_invalid(form)


class CouponApplyView(LoginRequiredMixin, View):
    login_url = reverse_lazy("account:login")  # adjust to your auth URL name

    def post(self, request, *args, **kwargs):
        cart = get_active_cart_for_request(request)

        if not cart_is_checkout_ready(cart):
            return self._respond(
                request,
                ok=False,
                message="سبد خرید شما خالی است.",
                status=400,
            )

        checkout_session = get_or_create_active_checkout_session(
            request=request,
            cart=cart,
        )

        form = CouponApplyForm(request.POST)

        if not form.is_valid():
            return self._respond(
                request,
                ok=False,
                message="کد تخفیف نامعتبر است.",
                status=400,
            )

        code = form.cleaned_data["coupon_code"]

        if not code:
            checkout_session.coupon = None
            checkout_session.save(update_fields=["coupon", "updated_at"])

            summary = build_checkout_summary(cart, coupon=None)

            return self._respond(
                request,
                ok=True,
                message="کد تخفیف حذف شد.",
                summary=summary,
            )

        coupon, error_message = validate_coupon_for_cart(code, cart)

        if error_message:
            summary = build_checkout_summary(cart, coupon=checkout_session.coupon)

            return self._respond(
                request,
                ok=False,
                message=error_message,
                summary=summary,
                status=400,
            )

        checkout_session.coupon = coupon
        checkout_session.save(update_fields=["coupon", "updated_at"])

        summary = build_checkout_summary(cart, coupon=coupon)

        return self._respond(
            request,
            ok=True,
            message="کد تخفیف با موفقیت اعمال شد.",
            summary=summary,
            coupon=coupon,
        )

    def _respond(
        self,
        request,
        *,
        ok: bool,
        message: str,
        status: int = 200,
        summary=None,
        coupon=None,
    ):
        wants_json = (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("accept", "")
        )

        if wants_json:
            payload = {
                "ok": ok,
                "message": message,
            }

            if coupon:
                payload["coupon"] = {
                    "id": coupon.pk,
                    "code": coupon.code,
                    "discount_type": coupon.discount_type,
                    "value": coupon.value,
                }
            else:
                payload["coupon"] = None

            if summary:
                payload["summary"] = summary_to_json(summary)

            return JsonResponse(payload, status=status)

        if ok:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("checkout:checkout-detail")



class CheckoutAddressSaveView(LoginRequiredMixin, View):
    # login_url = reverse_lazy("account:login")  # adjust if needed

    def post(self, request, *args, **kwargs):
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

        form = CheckoutAddressForm(
            request.POST,
            user=request.user,
            instance=instance,
        )

        if not form.is_valid():
            return self._respond_invalid(request, form)

        address = form.save()

        cart = get_active_cart_for_request(request)

        if cart_is_checkout_ready(cart):
            checkout_session = get_or_create_active_checkout_session(
                request=request,
                cart=cart,
            )

            if is_create:
                checkout_session.selected_address = address
                checkout_session.save(
                    update_fields=["selected_address", "updated_at"]
                )

        return self._respond_success(
            request=request,
            address=address,
            is_create=is_create,
        )

    def _wants_json(self, request):
        return (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("accept", "")
        )

    def _respond_invalid(self, request, form):
        first_error = "لطفاً اطلاعات آدرس را بررسی کنید."

        for field_errors in form.errors.values():
            if field_errors:
                first_error = field_errors[0]
                break

        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": False,
                    "message": first_error,
                    "errors": form.errors,
                },
                status=400,
            )

        messages.error(request, first_error)
        return redirect("order:checkout-detail")

    def _respond_success(self, request, address, is_create):
        message = "آدرس با موفقیت ذخیره شد."

        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "address": {
                        "id": address.pk,
                        "title": address.title,
                        "recipient_name": address.full_name,
                        "recipient_phone": address.phone_number,
                        "province": address.province,
                        "city": address.city,
                        "postal_code": address.zip_code,
                        "address_line": address.postal_address,
                        "is_create": is_create,
                    },
                }
            )

        messages.success(request, message)
        return redirect("order:checkout-detail")




class UserOrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
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
                "checkout_session",
                "cart",
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
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()

        order_code = self.kwargs.get("order_code")
        pk = self.kwargs.get("pk")

        if order_code:
            return get_object_or_404(queryset, code=order_code)

        if pk:
            return get_object_or_404(queryset, pk=pk)

        raise Http404("Order not found.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.object

        context["timeline_steps"] = self.get_timeline_steps(order)
        context["order_status_badge_class"] = self.get_order_status_badge_class(order)
        context["payment_status_class"] = self.get_payment_status_class(order)

        return context

    def get_order_status_badge_class(self, order):
        status_class_map = {
            Order.Status.PENDING_PAYMENT: "order-status-pending",
            Order.Status.PAID: "order-status-paid",
            Order.Status.PREPARING: "order-status-processing",
            Order.Status.SHIPPED: "order-status-shipped",
            Order.Status.DELIVERED: "order-status-delivered",
            Order.Status.CANCELLED: "order-status-cancelled",
            Order.Status.REFUNDED: "order-status-refunded",
        }

        return status_class_map.get(order.status, "order-status-processing")

    def get_payment_status_class(self, order):
        status_class_map = {
            Order.PaymentStatus.UNPAID: "text-muted",
            Order.PaymentStatus.PENDING: "text-warning",
            Order.PaymentStatus.PAID: "text-success",
            Order.PaymentStatus.FAILED: "text-danger",
            Order.PaymentStatus.REFUNDED: "text-muted",
        }

        return status_class_map.get(order.payment_status, "")

    def get_timeline_steps(self, order):
        if order.status == Order.Status.CANCELLED:
            return [
                {
                    "title": "ثبت سفارش",
                    "description": "سفارش شما در سیستم ثبت شد.",
                    "state_class": "is-complete",
                },
                {
                    "title": "لغو سفارش",
                    "description": "این سفارش لغو شده است.",
                    "state_class": "is-active",
                },
            ]

        if order.status == Order.Status.REFUNDED:
            return [
                {
                    "title": "ثبت سفارش",
                    "description": "سفارش شما در سیستم ثبت شد.",
                    "state_class": "is-complete",
                },
                {
                    "title": "پرداخت موفق",
                    "description": "پرداخت سفارش تایید شده بود.",
                    "state_class": "is-complete",
                },
                {
                    "title": "بازگشت وجه",
                    "description": "مبلغ سفارش بازگشت داده شده است.",
                    "state_class": "is-active",
                },
            ]

        steps = [
            {
                "status": Order.Status.PENDING_PAYMENT,
                "title": "ثبت سفارش",
                "description": "سفارش شما با موفقیت ثبت شد.",
            },
            {
                "status": Order.Status.PAID,
                "title": "پرداخت موفق",
                "description": "پرداخت سفارش تایید شده است.",
            },
            {
                "status": Order.Status.PREPARING,
                "title": "در حال آماده‌سازی",
                "description": "محصولات در حال بسته‌بندی و آماده‌سازی هستند.",
            },
            {
                "status": Order.Status.SHIPPED,
                "title": "ارسال سفارش",
                "description": "سفارش به واحد ارسال یا پیک تحویل داده شده است.",
            },
            {
                "status": Order.Status.DELIVERED,
                "title": "تحویل شده",
                "description": "سفارش در مقصد تحویل داده شده است.",
            },
        ]

        current_index_map = {
            Order.Status.PENDING_PAYMENT: 0,
            Order.Status.PAID: 1,
            Order.Status.PREPARING: 2,
            Order.Status.SHIPPED: 3,
            Order.Status.DELIVERED: 4,
        }

        current_index = current_index_map.get(order.status, 0)
        timeline_steps = []

        for index, step in enumerate(steps):
            if order.status == Order.Status.DELIVERED:
                state_class = "is-complete"
            elif index < current_index:
                state_class = "is-complete"
            elif index == current_index:
                state_class = "is-active"
            else:
                state_class = ""

            timeline_steps.append(
                {
                    "title": step["title"],
                    "description": step["description"],
                    "state_class": state_class,
                }
            )

        return timeline_steps
