from django.forms import ModelForm
from django import forms
from .models import Product, Purchase


class ProductCreateForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseCreateForm(ModelForm):
    class Meta:
        model = Purchase
        fields = ['count', ]
