from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, TemplateView, LogoutView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import FormView
from django.db.models import Sum, F, Func, Value

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
    success_message = 'successfully bought %(count)s %(product)s'

    def form_valid(self, form):
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

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.get_queryset()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(buyer_id=self.request.user.pk)
        qs = qs.annotate(total=F('count') * F('product__price'))
        qs = qs.annotate(path_for_static=Func(F('product__photo'), Value(8), function='substr'))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update({'return_create': forms.ReturnCreateForm})
        return context


class PurchaseDelete(SuccessMessageMixin, DeleteView):  # return accept
    model = models.Purchase
    template_name = 'shop/purchase/delete.html'
    success_url = '/return_list/'
    success_message = 'accept return product %()s'
    # queryset = model.objects.filter(product__price=) # todo for debug (delete)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ReturnCreate(DynamicSuccessUrlMixin, SuccessMessageMixin, CreateView):
    template_name = 'shop/return/create.html'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'
    success_message = 'success create return request %(purchase)s '

    # def form_valid(self, form):  # todo for debug (delete)
    #     # form_add = form.save(commit=False)
    #     # form_add.buyer_id = self.request.user.pk
    #     return super().form_valid(form)


class ReturnList(ListView):
    template_name = 'shop/return/list.html'
    model = models.Return
    context_object_name = 'returns'
    paginate_by = 6
    ordering = 'time'
    page_kwarg = 'page'

    # queryset = model.objects.filter(purchase__product__price=) # todo for debug (delete)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.get_queryset()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(total=F('purchase__count') * F('purchase__product__price'))
        qs = qs.annotate(path_for_static=Func(F('purchase__product__photo'), Value(8), function='substr'))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        return context


class ReturnDelete(SuccessMessageMixin, DeleteView):  # return reject
    model = models.Return
    template_name = 'shop/return/delete.html'
    success_url = '/return_list/'
    success_message = 'reject return product'

    # queryset = models.Return.objects.filter(purchase__product__name=) #

    def delete(self, request, *args, **kwargs):
        qs = models.Return.objects.get(pk=kwargs['pk']).purchase.product.name
        self.success_message = f'product {qs} return'
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
