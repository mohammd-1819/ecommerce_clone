from django import forms

from .models import PaymentMethod
from accounts.models import UserAddress  # adjust this import to your project


class CheckoutForm(forms.Form):
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.none(),
        required=True,
        empty_label=None,
        label="آدرس ارسال",
    )

    shipping_method = forms.ChoiceField(
        choices=(
            ("post", "ارسال با پست"),
            ("courier", "ارسال سریع شهری"),
        ),
        required=True,
        label="روش ارسال",
    )

    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        required=True,
        empty_label=None,
        to_field_name="code",
        label="روش پرداخت",
    )

    order_note = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="توضیحات سفارش",
    )

    def __init__(self, *args, user=None, checkout_session=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            raise ValueError("CheckoutForm requires user.")

        self.user = user
        self.checkout_session = checkout_session

        self.fields["shipping_address"].queryset = UserAddress.objects.filter(
            user=user
        ).order_by("-id")

        self.fields["payment_method"].queryset = PaymentMethod.objects.filter(
            is_active=True
        ).order_by("id")

    def save(self):
        if self.checkout_session is None:
            raise ValueError("CheckoutForm requires checkout_session.")

        self.checkout_session.selected_address = self.cleaned_data["shipping_address"]
        self.checkout_session.payment_method = self.cleaned_data["payment_method"]
        self.checkout_session.note = self.cleaned_data.get("order_note", "")
        self.checkout_session.save(
            update_fields=[
                "selected_address",
                "payment_method",
                "note",
                "updated_at",
            ]
        )
        return self.checkout_session


class CouponApplyForm(forms.Form):
    coupon_code = forms.CharField(
        required=False,
        max_length=40,
        label="کد تخفیف",
    )

    def clean_coupon_code(self):
        return self.cleaned_data["coupon_code"].strip()




class CheckoutAddressForm(forms.Form):
    address_id = forms.IntegerField(required=False)

    recipient_name = forms.CharField(
        max_length=255,
        required=True,
        label="نام گیرنده",
    )

    recipient_phone = forms.CharField(
        max_length=11,
        required=True,
        label="شماره تماس گیرنده",
    )

    province = forms.CharField(
        max_length=255,
        required=True,
        label="استان",
    )

    city = forms.CharField(
        max_length=255,
        required=True,
        label="شهر",
    )

    postal_code = forms.CharField(
        max_length=10,
        required=False,
        label="کد پستی",
    )

    address_line = forms.CharField(
        max_length=255,
        required=True,
        label="آدرس کامل",
    )

    def __init__(self, *args, user=None, instance=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            raise ValueError("CheckoutAddressForm requires user.")

        self.user = user
        self.instance = instance

    def clean_recipient_phone(self):
        phone = self.cleaned_data["recipient_phone"].strip()

        if not phone.isdigit():
            raise forms.ValidationError("شماره تماس باید فقط شامل عدد باشد.")

        if len(phone) > 11:
            raise forms.ValidationError("شماره تماس نمی‌تواند بیشتر از ۱۱ رقم باشد.")

        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code", "").strip()

        if postal_code and not postal_code.isdigit():
            raise forms.ValidationError("کد پستی باید فقط شامل عدد باشد.")

        if postal_code and len(postal_code) > 10:
            raise forms.ValidationError("کد پستی نمی‌تواند بیشتر از ۱۰ رقم باشد.")

        return postal_code

    def save(self):
        address = self.instance or UserAddress(user=self.user)

        address.full_name = self.cleaned_data["recipient_name"].strip()
        address.phone_number = self.cleaned_data["recipient_phone"].strip()
        address.province = self.cleaned_data["province"].strip()
        address.city = self.cleaned_data["city"].strip()
        address.zip_code = self.cleaned_data.get("postal_code", "").strip()
        address.postal_address = self.cleaned_data["address_line"].strip()

        if not address.title:
            address.title = "آدرس من"

        address.save()
        return address