from django.urls import path, include
from .views import IndexView, UserCreate, UserLogin, UserLogout, ProductCreate, ProductUpdate
from .views import PurchaseCreate, PurchaseList, PurchaseDelete
from .views import ReturnCreate, ReturnList, ReturnDelete


app_name = 'shop'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('user_create/', UserCreate.as_view(), name='user_create'),
    path('user_login/', UserLogin.as_view(), name='user_login'),
    path('user_logout/', UserLogout.as_view(), name='user_logout'),
    path('product_create/', ProductCreate.as_view(), name='product_create'),
    path('product_update/<int:pk>/', ProductUpdate.as_view(), name='product_update'),
    path('purchase_create/<int:pk>/', PurchaseCreate.as_view(), name='purchase_create'),
    path('purchase_list/', PurchaseList.as_view(), name='purchase_list'),
    path('purchase_delete/<int:pk>/', PurchaseDelete.as_view(), name='purchase_delete'),
    path('return_list/', ReturnList.as_view(), name='return_list'),
    path('return_create/', ReturnCreate.as_view(), name='return_create'),
    path('return_delete/<int:pk>/', ReturnDelete.as_view(), name='return_delete'),
]

