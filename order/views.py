from django.shortcuts import render
from django.views import View




class OrderDetailView(View):
    template_name = 'order/order_detail.html'

    def get(self, request):
        return render(request, self.template_name)
