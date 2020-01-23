from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, TemplateView, LogoutView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import FormView
from django.db.models import Sum, F, Func, Value

from . import models
from . import forms


class IndexView(ListView):
    template_name = 'shop/product/index.html'
    model = models.Product
    queryset = model.objects.all()
    context_object_name = 'products'
    paginate_by = 8
    ordering = 'price'

    # def dispatch(self, request, *args, **kwargs):
    #    # for debug
    #     data = super().dispatch(request, *args, **kwargs)
    #     return data
    #

    # def get_context_data(self, **kwargs):
    #     # for debug
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


class ProductUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'shop/product/update_form.html'
    form_class = forms.ProductCreateForm
    model = models.Product
    success_url = '/'
    success_message = 'success update product %(name)s'

    # todo: прописать картинки

    def get_success_url(self):
        url = super().get_success_url()
        success_url = self.request.POST.get('success_url')
        return success_url if success_url else url


class PurchaseCreate(SuccessMessageMixin, CreateView):
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

    def get_success_url(self):
        url = super().get_success_url()
        success_url = self.request.POST.get('success_url')
        return success_url if success_url else url


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
        qs = qs.annotate(image_path_for_static=Func(F('product__photo'), Value(8), function='substr'))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context = context.update({'return_create': forms.ReturnCreateForm})
        return context


class PurchaseDelete(SuccessMessageMixin, DeleteView):
    pass


class ReturnCreate(SuccessMessageMixin, CreateView):
    template_name = 'shop/return/create.html'
    form_class = forms.ReturnCreateForm
    success_url = '/purchase_list/'
    success_message = 'success create return request %(purchase)s '


class ReturnList(ListView):
    pass


class ReturnDelete(SuccessMessageMixin, DeleteView):
    pass
