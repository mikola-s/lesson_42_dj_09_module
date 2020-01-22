from django.forms import ModelForm
from django import forms
from .models import Product


class ProductCreateForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


