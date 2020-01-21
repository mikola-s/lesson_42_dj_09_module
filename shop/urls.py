from django.urls import path, include
from .views import IndexViews

app_name = 'shop'

urlpatterns = [
    path('', IndexViews.as_view(), name='index'),
]
