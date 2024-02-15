"""
В этом мудуле лежат различные наборы представлений.

Разные view интернет магазина: по товарам, заказам и т.д
"""
import logging

from timeit import default_timer
from csv import DictReader, DictWriter

from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.core import cache
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth.models import User

from .common import save_csv_products
from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer


log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD дл сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "prise",
        "archived",
    ]
    ordering_fields = [
        "name",
        "prise",
        "discount",
    ]
    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)
    @extend_schema(
        summary="Get one product by id",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            404: OpenApiResponse(description="Empty response, product by id not found"),
            200: ProductSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = "products-export.csv"
        response['Content-Disposition'] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "prise",
            "discount",
            "created_by",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response
    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)



class ShopIndexView(View):
    def get(self, request: HttpRequest):
        film_list = [
            ('The Shawhenk Redemption', 1994),
            ('The green mile', 1999),
            ('Rain man', 1988),
        ]
        context = {
            'time': default_timer(),
            'film_list': film_list,
        }
        log.debug('Products in shop index: %s', film_list)
        log.info('Rendering shop index')
        return render(request, 'shopapp/app_index.html', context=context)


# def shop_index(request: HttpRequest):
#     film_list = [
#         ('The Shawhenk Redemption', 1994),
#         ('The green mile', 1999),
#         ('Rain man', 1988),
#     ]
#     context = {
#         'time': default_timer(),
#         'film_list': film_list,
#     }
#     return render(request, 'shopapp/app_index.html', context=context)

class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"
    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     product = get_object_or_404(Product, pk=pk)
    #     context = {
    #         "product": product,
    #     }
    #     return render(request, 'shopapp/products-details.html', context=context)


class ProductsListView(ListView):
    template_name = 'shopapp/prodoucts-list.html'
    queryset = Product.objects.filter(archived=False)
    context_object_name = 'products'
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['products'] = Product.objects.all()
    #     return context


# def products_list(request: HttpRequest):
#     context = {
#         'products': Product.objects.all()
#     }
#     return render(request, 'shopapp/prodoucts-list.html', context=context)

class LatestProductsFeed(Feed):
    title = "Products (latest)"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
        Product.objects[:5]
    )

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description[:20]



class ProductUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_product'
    model = Product
    # fields = 'name', 'prise', 'description', 'discount', 'preview'
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().created_by


class ProductCreateView(UserPassesTestMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_product'

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        resource = super().form_valid(form)
        form.instance.created_by = self.request.user
        return resource

    success_url = reverse_lazy('shopapp:products_list')
    model = Product
    fields = 'name', 'prise', 'description', 'discount', 'preview'


# def create_product(request: HttpRequest):
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # Product.objects.create(**form.cleaned_data)
#             form.save()
#             url = reverse('shopapp:products_list')
#             return redirect(url)
#     else:
#         form = ProductForm()
#         context = {
#             'form': form
#         }
#         return render(request, 'shopapp/create-product.html', context=context)


class ProductDeleteView(DeleteView):
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "user",
        "delivery_adress",
        "promocode",
        "created_at",
    ]
    ordering_fields = [
        "user",
        "delivery_adress",
        "products",
    ]


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    context_object_name = 'orders'


class UserOrdersListView(UserPassesTestMixin, ListView):
    model = Order
    context_object_name = 'orders'
    def get_queryset(self):
        user_url = self.kwargs['user_id']
        self.owner = user_url
        return Order.objects.filter(user=user_url)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UserOrdersListView, self).get_context_data(**kwargs)
        context['owner'] = User.objects.get(pk=self.owner)
        return context

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.pk == self.kwargs['user_id']


# def orders_list(request: HttpRequest):
#     context = {
#         'orders': Order.objects.select_related('user').prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)

class OrderDetailView(UserPassesTestMixin, DetailView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user

    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    context_object_name = 'order'
def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user

class OrderUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user

    model = Order
    fields = 'delivery_adress', 'promocode', 'user', 'products'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class OrderDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user

    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


@login_required
def create_order(request: HttpRequest):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse('shopapp:orders_list')
            return redirect(url)
    else:
        form = OrderForm()
        context = {
            'form': form
        }
        return render(request, 'shopapp/create-order.html', context=context)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products = Product.objects.order_by("pk").all()
        products_data = cache.get(cache_key)
        if products_data in None:
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "prise": product.prise,
                    "archived": product.archived
                }
                for product in products
            ]
            elem = products_data[0]
            name = elem["name"]
            print("name:", name)
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class OrderDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_adress": order.delivery_adress,
                "promocode": order.promocode,
                "created_at": str(order.created_at),
                "user": order.user.pk,
                "products": [x.pk for x in order.products.all()]

            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})

class UserOrderDataExportView(UserPassesTestMixin, View):
    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        cache_key = f"orders_data_export_{user_id}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.filter(user=user_id)
            orders_data = [
                {
                    "pk": order.pk,
                    "delivery_adress": order.delivery_adress,
                    "promocode": order.promocode,
                    "created_at": str(order.created_at),
                    "user": order.user.pk,
                    "products": [x.pk for x in order.products.all()]

                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 60*10)
        return JsonResponse({"orders": orders_data})

    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user

    # orders = Order.objects.filter(user=self.request.user.pk)