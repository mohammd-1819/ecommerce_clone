from django.shortcuts import render, redirect
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
from django.views.generic import TemplateView, ListView, UpdateView
from .forms import UserAddressForm, UserProfileEditForm
from .models import UserAddress, UserProfile
from product.models import ProductReview
import secrets
from datetime import timedelta
from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from .forms import OTPPhoneForm, OTPVerifyForm
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.utils import timezone
import string
import math
from django.contrib.auth import logout


User = get_user_model()

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





class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileEditForm
    template_name = "accounts/profile_edit.html"
    context_object_name = "profile"
    success_url = reverse_lazy("accounts:profile-edit")

    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = self.object
        full_name = profile.get_full_name()
        username = self.request.user.username

        context["full_name"] = full_name or "کاربر عزیز"
        context["username"] = username or "user_name"
        context["phone_number"] = str(self.request.user.phone_number)

        context["avatar_letter"] = (
            full_name[0]
            if full_name
            else "ک"
        )

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "اطلاعات حساب کاربری با موفقیت ذخیره شد."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "لطفاً خطاهای فرم را بررسی و اصلاح کنید."
        )
        return super().form_invalid(form)




OTP_LENGTH = 5
OTP_EXPIRY_MINUTES = 5
OTP_REQUEST_LIMIT = 3
OTP_BAN_MINUTES = 20

OTP_SESSION_USER_ID = "otp_login_user_id"
OTP_SESSION_PHONE = "otp_login_phone"


def generate_otp_code(length=OTP_LENGTH):
    return "".join(secrets.choice(string.digits) for _ in range(length))

def phone_to_local(phone_number):
    phone = str(phone_number)

    if phone.startswith("+98"):
        return "0" + phone[3:]

    return phone


OTP_LENGTH = 5
OTP_EXPIRY_MINUTES = 5
OTP_REQUEST_LIMIT = 3
OTP_BAN_MINUTES = 20

OTP_SESSION_USER_ID = "otp_login_user_id"
OTP_SESSION_PHONE = "otp_login_phone"


def generate_otp_code(length=OTP_LENGTH):
    return "".join(secrets.choice(string.digits) for _ in range(length))


def phone_to_local(phone_number):
    """
    Convert saved PhoneNumberField values such as +989030313808
    back to local display format: 09030313808
    """
    phone = str(phone_number or "").strip()

    if phone.startswith("+98"):
        return "0" + phone[3:]

    if phone.startswith("98") and len(phone) == 12:
        return "0" + phone[2:]

    return phone


class OTPLoginView(TemplateView):
    template_name = "accounts/login.html"
    success_url = reverse_lazy("accounts:profile-dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")

        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url

        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session_phone = self.request.session.get(OTP_SESSION_PHONE, "")

        context.setdefault(
            "phone_form",
            OTPPhoneForm(initial={"phone": session_phone}) if session_phone else OTPPhoneForm(),
        )
        context.setdefault("verify_form", OTPVerifyForm())
        context.setdefault("step", "phone")
        context.setdefault("phone_preview", session_phone)
        context.setdefault("debug_otp_code", None)
        context.setdefault("otp_message", "")
        context.setdefault("otp_message_type", "")
        context.setdefault(
            "next_url",
            self.request.GET.get("next") or self.request.POST.get("next") or "",
        )

        return context

    def render_login(self, **context):
        return self.render_to_response(self.get_context_data(**context))

    def post(self, request, *args, **kwargs):
        action = request.POST.get("otp_action", "").strip()

        if action == "change_phone":
            return self.change_phone()

        if action in ("send", "resend"):
            return self.send_otp()

        if action == "verify":
            return self.verify_otp()

        # Fallback for old templates.
        if request.POST.get("otp_code"):
            return self.verify_otp()

        return self.send_otp()

    def change_phone(self):
        self.request.session.pop(OTP_SESSION_USER_ID, None)
        self.request.session.pop(OTP_SESSION_PHONE, None)

        return self.render_login(
            step="phone",
            phone_form=OTPPhoneForm(),
            verify_form=OTPVerifyForm(),
            phone_preview="",
            debug_otp_code=None,
            otp_message="شماره موبایل را دوباره وارد کنید.",
            otp_message_type="info",
        )

    def get_phone_form_from_request(self):
        """
        For send/resend:
        - first use POST phone
        - if empty, fallback to session phone
        This avoids the 'phone required' problem on resend.
        """
        raw_phone = self.request.POST.get("phone") or self.request.session.get(OTP_SESSION_PHONE, "")
        return OTPPhoneForm(data={"phone": raw_phone})

    def get_or_create_user_by_phone(self, phone):
        """
        phone must be local format: 09xxxxxxxxx
        PhoneNumberField(region='IR') can store it normalized internally.
        """
        user = User.objects.filter(phone_number=phone).first()

        if user:
            return user, False

        user = User.objects.create_user(phone_number=phone)
        return user, True

    def normalize_otp_request_state(self, user, now):
        """
        Your model default is otp_max_try=5,
        but login rule says only 3 OTP requests.
        """
        update_fields = []

        if user.otp_max_out and user.otp_max_out <= now:
            user.otp_max_out = None
            user.otp_max_try = OTP_REQUEST_LIMIT
            update_fields.extend(["otp_max_out", "otp_max_try"])

        if user.otp_max_try is None or user.otp_max_try > OTP_REQUEST_LIMIT:
            user.otp_max_try = OTP_REQUEST_LIMIT
            update_fields.append("otp_max_try")

        if update_fields:
            user.save(update_fields=list(set(update_fields)))

    def get_ban_remaining_minutes(self, user, now):
        if not user.otp_max_out:
            return 0

        remaining_seconds = max(0, int((user.otp_max_out - now).total_seconds()))
        return max(1, math.ceil(remaining_seconds / 60))

    def should_show_code_step(self, user, now):
        return bool(user.otp_code and user.otp_expiry and user.otp_expiry > now)

    def send_otp(self):
        phone_form = self.get_phone_form_from_request()

        if not phone_form.is_valid():
            return self.render_login(
                step="phone",
                phone_form=phone_form,
                verify_form=OTPVerifyForm(),
                phone_preview="",
                debug_otp_code=None,
                otp_message="شماره موبایل را به‌درستی وارد کنید.",
                otp_message_type="error",
            )

        phone = phone_form.cleaned_data["phone"]  # Example: 09030313808
        now = timezone.now()

        user, created = self.get_or_create_user_by_phone(phone)

        if not user.is_active:
            return self.render_login(
                step="phone",
                phone_form=phone_form,
                verify_form=OTPVerifyForm(),
                phone_preview=phone,
                debug_otp_code=None,
                otp_message="حساب کاربری شما غیرفعال است.",
                otp_message_type="error",
            )

        self.normalize_otp_request_state(user, now)

        local_phone = phone_to_local(user.phone_number)

        self.request.session[OTP_SESSION_USER_ID] = user.pk
        self.request.session[OTP_SESSION_PHONE] = local_phone

        # User is currently banned from requesting a new OTP.
        if user.otp_max_out and user.otp_max_out > now:
            remaining_minutes = self.get_ban_remaining_minutes(user, now)
            show_code_step = self.should_show_code_step(user, now)

            return self.render_login(
                step="code" if show_code_step else "phone",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=OTPVerifyForm(),
                phone_preview=local_phone,
                debug_otp_code=user.otp_code if show_code_step else None,
                otp_message=f"تعداد درخواست‌های کد بیش از حد مجاز است. حدود {remaining_minutes} دقیقه دیگر دوباره تلاش کنید.",
                otp_message_type="error",
            )

        # No request chance left; start ban.
        if user.otp_max_try <= 0:
            user.otp_max_out = now + timedelta(minutes=OTP_BAN_MINUTES)
            user.save(update_fields=["otp_max_out"])

            show_code_step = self.should_show_code_step(user, now)

            return self.render_login(
                step="code" if show_code_step else "phone",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=OTPVerifyForm(),
                phone_preview=local_phone,
                debug_otp_code=user.otp_code if show_code_step else None,
                otp_message="تعداد درخواست‌های کد بیش از حد مجاز است. ۲۰ دقیقه دیگر دوباره تلاش کنید.",
                otp_message_type="error",
            )

        otp_code = generate_otp_code()

        user.otp_code = otp_code
        user.otp_expiry = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
        user.otp_max_try -= 1

        # After the third request, user cannot request another OTP for 20 minutes.
        # The current OTP can still be verified.
        if user.otp_max_try <= 0:
            user.otp_max_out = now + timedelta(minutes=OTP_BAN_MINUTES)

        user.save(
            update_fields=[
                "otp_code",
                "otp_expiry",
                "otp_max_try",
                "otp_max_out",
            ]
        )

        return self.render_login(
            step="code",
            phone_form=OTPPhoneForm(initial={"phone": local_phone}),
            verify_form=OTPVerifyForm(),
            phone_preview=local_phone,
            debug_otp_code=otp_code,
            otp_message="کد تایید ساخته شد.",
            otp_message_type="success",
            remaining_otp_requests=user.otp_max_try,
        )

    def verify_otp(self):
        verify_form = OTPVerifyForm(self.request.POST)
        user_id = self.request.session.get(OTP_SESSION_USER_ID)

        if not user_id:
            return self.render_login(
                step="phone",
                phone_form=OTPPhoneForm(),
                verify_form=verify_form,
                phone_preview="",
                debug_otp_code=None,
                otp_message="ابتدا شماره موبایل را وارد کنید.",
                otp_message_type="error",
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.request.session.pop(OTP_SESSION_USER_ID, None)
            self.request.session.pop(OTP_SESSION_PHONE, None)

            return self.render_login(
                step="phone",
                phone_form=OTPPhoneForm(),
                verify_form=OTPVerifyForm(),
                phone_preview="",
                debug_otp_code=None,
                otp_message="کاربر پیدا نشد. دوباره شماره موبایل را وارد کنید.",
                otp_message_type="error",
            )

        local_phone = phone_to_local(user.phone_number)

        if not verify_form.is_valid():
            return self.render_login(
                step="code",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=verify_form,
                phone_preview=local_phone,
                debug_otp_code=user.otp_code,
                otp_message="کد تایید را به‌درستی وارد کنید.",
                otp_message_type="error",
            )

        otp_code = verify_form.cleaned_data["otp_code"]
        now = timezone.now()

        if not user.otp_code or not user.otp_expiry:
            return self.render_login(
                step="code",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=verify_form,
                phone_preview=local_phone,
                debug_otp_code=None,
                otp_message="کد تایید موجود نیست. دوباره کد دریافت کنید.",
                otp_message_type="error",
            )

        if user.otp_expiry < now:
            user.otp_code = None
            user.otp_expiry = None
            user.save(update_fields=["otp_code", "otp_expiry"])

            return self.render_login(
                step="code",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=verify_form,
                phone_preview=local_phone,
                debug_otp_code=None,
                otp_message="کد تایید منقضی شده است. دوباره کد دریافت کنید.",
                otp_message_type="error",
            )

        if user.otp_code != otp_code:
            return self.render_login(
                step="code",
                phone_form=OTPPhoneForm(initial={"phone": local_phone}),
                verify_form=verify_form,
                phone_preview=local_phone,
                debug_otp_code=user.otp_code,
                otp_message="کد تایید اشتباه است.",
                otp_message_type="error",
            )

        # Successful login.
        user.otp_code = None
        user.otp_expiry = None
        user.otp_max_try = OTP_REQUEST_LIMIT
        user.otp_max_out = None
        user.save(
            update_fields=[
                "otp_code",
                "otp_expiry",
                "otp_max_try",
                "otp_max_out",
            ]
        )

        backend = settings.AUTHENTICATION_BACKENDS[0]
        login(self.request, user, backend=backend)

        self.request.session.pop(OTP_SESSION_USER_ID, None)
        self.request.session.pop(OTP_SESSION_PHONE, None)

        return redirect(self.get_success_url())


class ProfileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_dashboard.html"
    login_url = reverse_lazy("accounts:login")
    redirect_field_name = "next"



class LogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy("accounts:login")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("accounts:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("accounts:login")