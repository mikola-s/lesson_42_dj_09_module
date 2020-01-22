from django.urls import path, include
from .views import IndexView, UserCreate, UserLogin, UserLogout, ProductCreate, ProductUpdate
from .views import PurchaseCreate

app_name = 'shop'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('user_create/', UserCreate.as_view(), name='user_create'),
    path('user_login/', UserLogin.as_view(), name='user_login'),
    path('user_logout/', UserLogout.as_view(), name='user_logout'),
    path('product_create/', ProductCreate.as_view(), name='product_create'),
    path('product_update/<int:pk>', ProductUpdate.as_view(), name='product_update'),
    path('purchase_create/<int:pk>', PurchaseCreate.as_view(), name='purchase_create'),
]

