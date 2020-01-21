from django.contrib import admin
from .models import Profile, Purchase, Product, Return

admin.site.register(Profile)
admin.site.register(Purchase)
admin.site.register(Product)
admin.site.register(Return)