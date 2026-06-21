from django import forms
from .models import UserAddress, UserProfile
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
import re


class UserAddressForm(forms.Form):
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
            raise ValueError("UserAddressForm requires user.")

        self.user = user
        self.instance = instance

        if instance is not None and not self.is_bound:
            self.initial.update(
                {
                    "address_id": instance.pk,
                    "recipient_name": instance.full_name or "",
                    "recipient_phone": instance.phone_number or "",
                    "province": instance.province or "",
                    "city": instance.city or "",
                    "postal_code": instance.zip_code or "",
                    "address_line": instance.postal_address or "",
                }
            )

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




class UserProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=200,
        required=True,
        label="نام و نام خانوادگی",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "id": "profile-full-name",
            "placeholder": "نام و نام خانوادگی خود را وارد کنید",
            "autocomplete": "name",
        })
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        label="نام کاربری",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "id": "profile-username",
            "placeholder": "نام کاربری",
            "autocomplete": "username",
        })
    )

    email = forms.EmailField(
        required=False,
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "id": "profile-email",
            "placeholder": "example@email.com",
            "autocomplete": "email",
        })
    )

    class Meta:
        model = UserProfile
        fields = ["full_name", "username", "email"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        profile = self.instance

        self.fields["full_name"].initial = profile.get_full_name()
        self.fields["username"].initial = self.user.username
        self.fields["email"].initial = profile.email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if not username:
            raise forms.ValidationError("نام کاربری نمی‌تواند خالی باشد.")

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()

        if not full_name:
            raise forms.ValidationError("نام و نام خانوادگی نمی‌تواند خالی باشد.")

        return full_name

    def save(self, commit=True):
        profile = super().save(commit=False)

        full_name = self.cleaned_data["full_name"]
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]

        name_parts = full_name.split(maxsplit=1)
        profile.first_name = name_parts[0]
        profile.last_name = name_parts[1] if len(name_parts) > 1 else ""
        profile.email = email

        self.user.username = username

        if commit:
            self.user.save(update_fields=["username"])
            profile.save()

        return profile




def to_english_digits(value):
    if not value:
        return ""

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"

    value = str(value)

    for index, digit in enumerate(persian_digits):
        value = value.replace(digit, str(index))

    for index, digit in enumerate(arabic_digits):
        value = value.replace(digit, str(index))

    return value


def to_english_digits(value):
    if not value:
        return ""

    value = str(value)

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"

    for index, digit in enumerate(persian_digits):
        value = value.replace(digit, str(index))

    for index, digit in enumerate(arabic_digits):
        value = value.replace(digit, str(index))

    return value


def normalize_iran_mobile(value):
    """
    Accept:
    09030313808
    989030313808
    +989030313808
    9030313808

    Return:
    09030313808
    """
    phone = to_english_digits(value)
    phone = phone.strip()
    phone = phone.replace(" ", "")
    phone = phone.replace("-", "")

    # Remove leading +
    if phone.startswith("+"):
        phone = phone[1:]

    # +989030313808 or 989030313808 -> 09030313808
    if phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]

    # 9030313808 -> 09030313808
    elif phone.startswith("9") and len(phone) == 10:
        phone = "0" + phone

    # Keep only digits after normalization
    phone = re.sub(r"\D", "", phone)

    if not re.fullmatch(r"09\d{9}", phone):
        raise forms.ValidationError(
            "شماره موبایل باید کامل و معتبر باشد. مثال: 09030313808"
        )

    return phone


class OTPPhoneForm(forms.Form):
    phone = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            "required": "شماره موبایل الزامی است.",
        },
    )

    def clean_phone(self):
        return normalize_iran_mobile(self.cleaned_data["phone"])


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        required=True,
        min_length=5,
        max_length=5,
        error_messages={
            "required": "کد تایید الزامی است.",
            "min_length": "کد تایید باید ۵ رقم باشد.",
            "max_length": "کد تایید باید ۵ رقم باشد.",
        },
    )

    def clean_otp_code(self):
        otp_code = to_english_digits(self.cleaned_data["otp_code"])
        otp_code = re.sub(r"\D", "", otp_code)

        if not re.fullmatch(r"\d{5}", otp_code):
            raise forms.ValidationError("کد تایید باید ۵ رقم باشد.")

        return otp_code