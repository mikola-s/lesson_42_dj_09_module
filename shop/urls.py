from django.urls import path, include
from .views import IndexView

app_name = 'shop'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
