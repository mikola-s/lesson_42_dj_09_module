from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, TemplateView, LogoutView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import FormView
from django.db.models import ExpressionWrapper, Sum, Q, F, Func, Value, DecimalField
from django.urls import reverse_lazy, reverse
from datetime import timedelta
from django.utils import timezone

from . import models
from . import forms


class YouCash:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.pk is not None:
            context.update({'cash': self.request.user.profile.cash})
        return context


class CustomSuccessUrl:
    def get_success_url(self):
        self.success_url = self.request.META.get('HTTP_REFERER', False) or self.success_url
        return self.success_url


class IndexView(YouCash, ListView):
    template_name = 'shop/product/index.html'
    model = models.Product
    queryset = model.objects.all()
    context_object_name = 'products'
    paginate_by = 8
    ordering = 'price'

    def get_context_data(self, **kwargs):  # todo for debug (delete)
        context = super().get_context_data(**kwargs)
        context.update({'purchase_create_form': forms.PurchaseCreateForm})
        return context


class UserCreate(CreateView):
    template_name = 'shop/user/user_create.html'
    form_class = UserCreationForm
    success_url = '/'
    success_message = 'Create user %(username)s successful'

    def form_valid(self, form):
        data = super().form_valid(form)
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return data


class UserLogin(LoginView):
    template_name = 'shop/user/user_login.html'
    success_url = '/'
    success_message = '%(username)s login successfully'


class UserLogout(LogoutView):
    template_name = 'shop/user/user_logout.html'
    next_page = '/'

    def dispatch(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.SUCCESS,
                             f'{self.request.user.username} logout successfully')
        return super().dispatch(request, *args, **kwargs)


class ProductCreate(CreateView):
    template_name = 'shop/product/create_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/product_create/'
    success_message = 'success crate product %(name)s'


class ProductUpdate(UpdateView):
    template_name = 'shop/product/update_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/'
    success_message = 'success update product %(name)s'

    # todo custom success url

    # todo: прописать картинки


class PurchaseCreate(CustomSuccessUrl, CreateView):
    template_name = 'shop/purchase/create.html'
    form_class = forms.PurchaseCreateForm
    model = models.Purchase
    success_url = '/'

    def purchase_validator(self, form):
        error_check = False
        user = models.Profile.objects.get(pk=self.request.user.pk)
        product = models.Product.objects.get(pk=self.kwargs['pk'])
        ordered_product = form.cleaned_data.get('count')
        total_cost = ordered_product * product.price

        if product.count < ordered_product:
            error_check = True
            messages.add_message(self.request, messages.WARNING,
                                 f'{product.name} ({ordered_product}) is not in stock. '
                                 f'Now available {product.count}')

        if total_cost >= user.cash:
            error_check = True
            messages.add_message(self.request, messages.WARNING,
                                 f'You need {total_cost.normalize()} ₴ '
                                 f'for buy {product.name} ({ordered_product})')

        return {'error_check': error_check,
                'total_cost': total_cost,
                'user': user,
                'product': product,
                'ordered_product': ordered_product,
                }

    def form_valid(self, form):
        valid_data = self.purchase_validator(form)

        if valid_data['error_check']:
            return redirect(self.success_url)
        else:
            valid_data['user'].cash -= valid_data['total_cost']
            valid_data['user'].save()
            valid_data['product'].count -= valid_data['ordered_product']
            valid_data['product'].save()

            messages.add_message(
                self.request, messages.SUCCESS,
                f"Success purchase: {valid_data['product'].name} ({valid_data['ordered_product']}) "
                f"total cost {valid_data['total_cost']}")

            form_add = form.save(commit=False)
            form_add.buyer_id = self.request.user.pk
            form_add.product_id = self.kwargs['pk']
            form.cleaned_data.update({'product': form.instance.product.name})
            return super().form_valid(form)


class PurchaseList(YouCash, FormMixin, ListView):
    template_name = 'shop/purchase/list.html'
    model = models.Purchase
    context_object_name = 'purchases'
    paginate_by = 6
    ordering = '-time'
    page_kwarg = 'page'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(post_time=F('purchase__post_time'))
        return qs

    def get_context_data(self, **kwargs):
        time_over = timezone.now() - timedelta(minutes=3)
        context = super().get_context_data(**kwargs)
        context.update({'time_over': time_over})
        return context


class PurchaseDelete(DeleteView):
    model = models.Purchase
    template_name = 'shop/purchase/delete.html'
    success_url = '/return_list/'

    def delete(self, request, *args, **kwargs):
        purchase = self.model.objects.get(pk=kwargs['pk'])
        total_cost = purchase.product.price * purchase.count

        purchase.buyer.profile.cash += total_cost
        purchase.buyer.profile.save()
        purchase.product.count += purchase.count
        purchase.product.save()

        messages.add_message(self.request, messages.SUCCESS,
                             f'Return in store {purchase.product.name} ({purchase.count}) confirmed. '
                             f'Return {purchase.buyer.username} {purchase.count * purchase.product.price} ₴')
        return super().delete(request, *args, **kwargs)


class ReturnCreate(CustomSuccessUrl, CreateView):
    template_name = 'shop/return/create.html'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'

    @staticmethod
    def return_validator(form):
        time_over = form.cleaned_data['purchase'].time + timedelta(minutes=3)
        if time_over < timezone.now():
            return True
        return False

    def form_valid(self, form):

        if self.return_validator(form):
            messages.add_message(self.request, messages.WARNING, 'Return time is over')
            return redirect(self.get_success_url())

        purchase = form.cleaned_data["purchase"]
        messages.add_message(self.request, messages.SUCCESS,
                             f'You have return: {purchase.product.name} ({purchase.count}) '
                             f'buy: {purchase.time.strftime("%Y-%m-%d %H:%M:%S")}')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING,
                             "The return-form has already been submitted")
        return redirect(self.get_success_url())


class ReturnList(ListView):
    template_name = 'shop/return/list.html'
    model = models.Return
    context_object_name = 'returns'
    paginate_by = 6
    ordering = 'post_time'
    page_kwarg = 'page'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.get_queryset()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(total=ExpressionWrapper(
            F('purchase__count') * F('purchase__product__price'), output_field=DecimalField()))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        return context


class ReturnDelete(DeleteView):  # return reject
    model = models.Return
    template_name = 'shop/return/delete.html'
    success_url = '/return_list/'

    def delete(self, request, *args, **kwargs):
        qs = self.model.objects.get(pk=kwargs['pk']).purchase
        qs.return_status = False
        qs.save()
        messages.add_message(self.request, messages.SUCCESS,
                             f'{qs.product.name} ({qs.count}) left with the buyer')
        return super().delete(request, *args, **kwargs)
