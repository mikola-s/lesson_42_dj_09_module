from django.urls import path, include
from .views import IndexView, UserCreate, UserLogin, UserLogout

app_name = 'shop'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('user_create/', UserCreate.as_view(), name='user_create'),
    path('user_login/', UserLogin.as_view(), name='user_login'),
    path('user_logout/', UserLogout.as_view(), name='user_logout'),
]
