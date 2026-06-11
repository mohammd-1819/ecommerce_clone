from django.shortcuts import render
from django.views import View



class ProductListView(View):
    template_name = 'product/product_list.html'

    def get(self, request):
        return render(request, self.template_name)


class ProductDetailView(View):
    template_name = 'product/product_detail.html'

    def get(self, request):
        return render(request, self.template_name)