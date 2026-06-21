from django import forms

from .models import UserAddress


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