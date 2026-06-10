from django.shortcuts import render
from django.views import View




class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        return render(request, self.template_name)


class CechkoutView(View):
    template_name = 'cart/checkout.html'

    def get(self, request):
        return render(request, self.template_name)
