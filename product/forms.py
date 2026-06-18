from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["first_name", "last_name", "body"]

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def clean_body(self):
        body = self.cleaned_data["body"].strip()

        if len(body) < 5:
            raise forms.ValidationError("متن دیدگاه خیلی کوتاه است.")

        return body