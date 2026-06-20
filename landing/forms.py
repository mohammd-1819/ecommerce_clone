from django import forms

from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    request_type = forms.ChoiceField(
        choices=[("", "انتخاب کنید")] + list(ContactRequest.RequestType.choices),
        label="نوع درخواست",
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "contact-type",
        }),
    )

    class Meta:
        model = ContactRequest
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "request_type",
            "subject",
            "message",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-input",
                "id": "contact-first-name",
                "placeholder": "مثلاً علی",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-input",
                "id": "contact-last-name",
                "placeholder": "مثلاً رضایی",
                "autocomplete": "family-name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "id": "contact-phone",
                "placeholder": "۰۹۱۲۳۴۵۶۷۸۹",
                "autocomplete": "tel",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "id": "contact-email",
                "placeholder": "example@email.com",
                "autocomplete": "email",
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-input",
                "id": "contact-subject",
                "placeholder": "مثلاً خرید عمده",
            }),
            "message": forms.Textarea(attrs={
                "class": "form-textarea",
                "id": "contact-message",
                "placeholder": "درخواست یا سوال خود را بنویسید...",
                "rows": 6,
            }),
        }

        error_messages = {
            "first_name": {
                "required": "لطفاً نام خود را وارد کنید.",
            },
            "last_name": {
                "required": "لطفاً نام خانوادگی خود را وارد کنید.",
            },
            "phone": {
                "required": "لطفاً شماره تماس خود را وارد کنید.",
            },
            "subject": {
                "required": "لطفاً موضوع پیام را وارد کنید.",
            },
            "message": {
                "required": "لطفاً متن پیام را وارد کنید.",
            },
            "email": {
                "invalid": "لطفاً ایمیل معتبر وارد کنید.",
            },
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"

        for fa_digit, en_digit in zip(persian_digits, english_digits):
            phone = phone.replace(fa_digit, en_digit)

        allowed_chars = set("0123456789+ -()")
        if not all(char in allowed_chars for char in phone):
            raise forms.ValidationError("شماره تماس فقط می‌تواند شامل عدد، فاصله، خط تیره یا + باشد.")

        return phone