from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, TemplateView, LogoutView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView

from . import models
from . import forms


class IndexView(ListView):
    template_name = 'shop/index.html'
    model = models.Product
    queryset = model.objects.all()
    context_object_name = 'products'

    # def dispatch(self, request, *args, **kwargs):
    #     data = super().dispatch(request, *args, **kwargs)
    #     return data
    #
    # def get_context_data(self, **kwargs):
    #     # for debug
    #     context = super().get_context_data(**kwargs)
    #     return context


class UserCreate(SuccessMessageMixin, CreateView):
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


class UserLogin(SuccessMessageMixin, LoginView):
    template_name = 'shop/user_login.html'
    success_url = '/'
    success_message = '%(username)s logged in successfully'


class UserLogout(SuccessMessageMixin, LogoutView):
    template_name = 'shop/user_logout.html'
    next_page = '/'
    success_message = 'success logout'


class ProductCreate(SuccessMessageMixin, CreateView):
    http_method_names = ['post', 'get']
    template_name = 'shop/product_create_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/product_create/'
    success_message = 'success crate product %(name)s'

    # def form_valid(self, form):
    #     # for debug
    #     self.get_success_message()
    #     data = super().form_valid(form)
    #     return data

    # def form_invalid(self, form):
    #     # for debug
    #     data = super().form_invalid(form)
    #     return data

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
