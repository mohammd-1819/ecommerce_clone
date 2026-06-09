from django.shortcuts import render
from django.views import View




class ProfileDashboardView(View):
    template_name = 'accounts/profile_dashboard.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileOrdersView(View):
    template_name = 'accounts/profile_orders.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileAddressView(View):
    template_name = 'accounts/profile_address.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileCommentsView(View):
    template_name = 'accounts/profile_comments.html'

    def get(self, request):
        return render(request, self.template_name)


class ProfileEditView(View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        return render(request, self.template_name)
