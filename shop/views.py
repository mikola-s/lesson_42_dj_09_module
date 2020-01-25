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


class IndexView(ListView):
    template_name = 'shop/product/index.html'
    model = models.Product
    queryset = model.objects.all()
    context_object_name = 'products'
    paginate_by = 8
    ordering = 'price'

    # def get_context_data(self, **kwargs): # todo for debug (delete)
    #     context = super().get_context_data(**kwargs)
    #     context.update({'purchase_create_form': forms.PurchaseCreateForm})
    #     return context


class UserCreate(SuccessMessageMixin, CreateView):
    template_name = 'shop/user/user_create.html'
    form_class = UserCreationForm
    success_url = '/'

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
    success_message = '%(username)s logged in successfully'


class UserLogout(SuccessMessageMixin, LogoutView):
    template_name = 'shop/user/user_logout.html'
    next_page = '/'
    success_message = 'success logout'


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


class PurchaseCreate(DynamicSuccessUrlMixin, SuccessMessageMixin, CreateView):
    template_name = 'shop/purchase/create.html'
    form_class = forms.PurchaseCreateForm
    model = models.Purchase
    success_url = '/'
    success_message = 'successfully buy -- %(count)s %(product)s'

    def purchase_validator(self, form):
        error_check = False
        user = models.Profile.objects.get(pk=self.request.user.pk)
        product = models.Product.objects.get(pk=self.kwargs['pk'])
        ordered_product = form.cleaned_data.get('count')
        total_cost = ordered_product * product.price

        if product.count < ordered_product:
            error_check = True
            messages.add_message(self.request, messages.WARNING, 'So much product is not in stock')

        if total_cost >= user.cache:
            error_check = True
            messages.add_message(self.request, messages.WARNING, 'You don’t have enough money to buy')

        if error_check:
            return redirect(reverse_lazy('shop:purchase_list_with_mixin'))

        return {'total_cost': total_cost, 'user': user, 'product': product}

    def form_valid(self, form):
        valid_data = self.purchase_validator(form)

        valid_data['user'].cash -= valid_data['total_cost']
        valid_data['user'].save()
        valid_data['product'].count -= valid_data['total_cost']
        valid_data['product'].save()

        messages.add_message(
            self.request, messages.SUCCESS,
            f'Success purchase {valid_data["product"].name} ({valid_data["total_cost"]})')

        form_add = form.save(commit=False)
        form_add.buyer_id = self.request.user.pk
        form_add.product_id = self.kwargs['pk']
        form.cleaned_data.update({'product': form.instance.product.name})
        return super().form_valid(form)


class PurchaseListWithMixin(FormMixin, ListView):
    template_name = 'shop/purchase/list_with_mixin.html'
    model = models.Purchase
    context_object_name = 'purchases'
    paginate_by = 6
    ordering = '-time'
    page_kwarg = 'page'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list_with_mixin/'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(post_time=F('purchase__post_time'))
        return qs

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     qs = self.model.objects.filter(pos)


class ReturnCreateWithMixin(CreateView):
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
            messages.add_message(self.request, messages.WARNING, 'So much product is not in stock')

        if total_cost >= user.cache:
            error_check = True
            messages.add_message(self.request, messages.WARNING, 'You don’t have enough money to buy')

        if error_check:
            return redirect(reverse_lazy('shop:purchase_list_with_mixin'))

        return {'total_cost': total_cost, 'user': user, 'product': product}

    def form_valid(self, form):
        valid_data = self.purchase_validator(form)

        valid_data['user'].cash -= valid_data['total_cost']
        valid_data['user'].save()
        valid_data['product'].count -= valid_data['total_cost']
        valid_data['product'].save()

        messages.add_message(
            self.request, messages.SUCCESS,
            f'Success purchase {valid_data["product"].name} ({valid_data["total_cost"]})')

        form_add = form.save(commit=False)
        form_add.buyer_id = self.request.user.pk
        form_add.product_id = self.kwargs['pk']
        form.cleaned_data.update({'product': form.instance.product.name})
        return super().form_valid(form)


class PurchaseList(ListView):
    template_name = 'shop/purchase/list.html'
    model = models.Purchase
    context_object_name = 'purchases'
    paginate_by = 6
    ordering = '-time'
    page_kwarg = 'page'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.get_queryset()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(buyer_id=self.request.user.pk)
        qs = qs.annotate(total=ExpressionWrapper(
            F('count') * F('product__price'), output_field=DecimalField()))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update({'form': forms.ReturnCreateForm})
        return context


class PurchaseDelete(SuccessMessageMixin, DeleteView):  # return accept
    model = models.Purchase
    template_name = 'shop/purchase/delete.html'
    success_url = '/return_list/'
    success_message = 'return the product'

    # queryset = model.objects.filter(product__price=) # todo for debug (delete)

    def delete(self, request, *args, **kwargs):
        qs = self.model.objects.get(pk=kwargs['pk']).product
        self.success_message = f'return {qs.count} {qs.name} confirmed'
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ReturnCreate(SuccessMessageMixin, CreateView):
    template_name = 'shop/return/create.html'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'
    success_message = 'You have return %(purchase)s '

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):  # todo for debug (delete)
        # form_add = form.save(commit=False)
        # form_add.buyer_id = self.request.user.pk
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, "Request has already been sent")
        return redirect(reverse_lazy('shop:purchase_list'))


class ReturnList(ListView):
    template_name = 'shop/return/list.html'
    model = models.Return
    context_object_name = 'returns'
    paginate_by = 6
    ordering = 'post_time'
    page_kwarg = 'page'

    # queryset = model.objects.filter(purchase__product__price=) # todo for debug (delete)

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


class ReturnDelete(SuccessMessageMixin, DeleteView):  # return reject
    model = models.Return
    template_name = 'shop/return/delete.html'
    success_url = '/return_list/'
    success_message = 'The product is left with the buyer'

    # queryset = models.Return.objects.filter(purchase__product__name=) #

    def delete(self, request, *args, **kwargs):
        qs = self.model.objects.get(pk=kwargs['pk']).purchase.product
        self.success_message = f'{qs.count} {qs.name} left with the buyer'
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
