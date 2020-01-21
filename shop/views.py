from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, TemplateView, LogoutView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import FormView

from . import models
from . import forms


class IndexView(ListView):
    template_name = 'shop/index.html'
    model = models.Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserCreate(CreateView):
    template_name = 'shop/user_create.html'
    form_class = UserCreationForm
    success_url = '/'

    def form_valid(self, form):
        data = super().form_valid(form)
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return data


class UserLogin(LoginView):
    template_name = 'shop/user_login.html'
    success_url = '/'


class UserLogout(LogoutView):
    template_name = 'shop/user_logout.html'
    next_page = '/'


class ProductCreate(CreateView):
    http_method_names = ['post', 'get']
    template_name = 'shop/product_create_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/'

