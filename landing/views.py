from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import ContactRequestForm
from .models import ContactRequest



class HomeView(View):
    template_name = 'landing/home.html'

    def get(self, request):
        return render(request, self.template_name)



class AboutView(View):
    template_name = 'landing/about.html'

    def get(self, request):
        return render(request, self.template_name)



class ContactRequestCreateView(CreateView):
    model = ContactRequest
    form_class = ContactRequestForm
    template_name = "landing/contact.html"
    success_url = reverse_lazy("landing:contact")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "پیام شما با موفقیت ثبت شد. در اولین فرصت با شما تماس می‌گیریم.",
        )

        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "لطفاً خطاهای فرم را بررسی و دوباره ارسال کنید.",
        )

        return super().form_invalid(form)