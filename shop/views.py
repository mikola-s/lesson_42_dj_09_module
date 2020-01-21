from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, TemplateView, LogoutView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import FormView

from . import models
from . import forms


class IndexView(ListView):
    template_name = 'shop/index.html'
    model = models.Product
