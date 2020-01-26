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
from django.db.models import ExpressionWrapper, Sum, F, Func, Value, DecimalField
from django.urls import reverse_lazy, reverse

from . import models
from . import forms


class DynamicSuccessUrlMixin(View):

    def get_success_url(self):
        url = super().get_success_url()
        post = self.request.POST.get('success_url')
        get = self.request.GET.get('success_url')
        success_url = post if post else get
        return success_url if success_url else url


class YouCash:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.pk is not None:
            context.update({'cash': self.request.user.profile.cash})
        return context


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


class UserCreate(SuccessMessageMixin, CreateView):
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


class UserLogin(SuccessMessageMixin, LoginView):
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


class ProductCreate(SuccessMessageMixin, CreateView):
    template_name = 'shop/product/create_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/product_create/'
    success_message = 'success crate product %(name)s'


class ProductUpdate(DynamicSuccessUrlMixin, SuccessMessageMixin, UpdateView):
    template_name = 'shop/product/update_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/'
    success_message = 'success update product %(name)s'

    # todo: прописать картинки


class PurchaseCreate(CreateView):
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
                                 f'You need {total_cost.normalize()} ₴ for buy {product.name} ({ordered_product})')

        return {'error_check': error_check,
                'total_cost': total_cost,
                'user': user,
                'product': product,
                'ordered_product': ordered_product,
                }

    def form_valid(self, form):
        valid_data = self.purchase_validator(form)

        if valid_data['error_check']:
            return redirect(reverse_lazy('shop:index'))
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
    # qs = model.objects.filter(purchase__post_time=)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(post_time=F('purchase__post_time'))
        # qs = qs.annotate(total=ExpressionWrapper(
        #     F('count') * F('product__price'), output_field=DecimalField()))
        return qs


class PurchaseDelete(DeleteView):
    model = models.Purchase
    template_name = 'shop/purchase/delete.html'
    success_url = '/return_list/'

    def delete(self, request, *args, **kwargs):
        qs = self.model.objects.get(pk=kwargs['pk'])
        messages.add_message(self.request, messages.SUCCESS,
                             f'Return in store {qs.product.name} ({qs.count}) confirmed. '
                             f'Return {qs.buyer.username} {qs.count * qs.product.price} ₴')
        return super().delete(request, *args, **kwargs)


class ReturnCreate(CreateView):
    template_name = 'shop/return/create.html'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'

    def form_valid(self, form):
        purchase = form.cleaned_data["purchase"]
        messages.add_message(self.request, messages.SUCCESS,
                             f'You have return: {purchase.product.name} ({purchase.count}) '
                             f'buy: {purchase.time.strftime("%Y-%m-%d %H:%M:%S")}')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, "The return-form has already been submitted")
        return redirect(reverse_lazy('shop:purchase_list'))


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
        messages.add_message(self.request, messages.SUCCESS,
                             f'{qs.product.name} ({qs.count}) left with the buyer')
        return super().delete(request, *args, **kwargs)
