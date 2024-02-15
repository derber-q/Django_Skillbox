from csv import DictReader
from io import TextIOWrapper

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .common import save_csv_products, save_csv_orders, convert_str_to_int_list
from .forms import CSVImportForm

from .models import Product, Order, ProductImage


class OrderiInline(admin.TabularInline):
    model = Product.orders.through

class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Archive products')
def merk_archived(modladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)

@admin.action(description='Unarchive products')
def merk_unarchived(modladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"

    actions = [
        merk_archived,
        merk_unarchived,
        'export_csv'
    ]
    inlines = [
        OrderiInline,
        ProductInline,
    ]
    list_display = 'pk', 'name', 'description_short', 'prise', 'discount', 'archived', 'get_created_by'

    def get_created_by(self, instance):
        return instance.pk

    list_display_links = 'pk', 'name'
    ordering = '-pk',
    search_fields = 'name', 'description'
    fieldsets = [
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Price options', {
            'fields': ('prise', 'discount'),
            'classes': ('collapse', 'wide'),
        }),

        ('Images', {
            'fields': ('preview',)
        }),
        ('Extra options', {
            'fields': ('archived',),
            'classes': ('collapse',),
            'description': "Extra options. Field 'archived' is for soft delete"
        })
    ]

    def description_short(self,obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        scv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(scv_file)
        products = [Product(**row) for row in reader]
        Product.objects.bulk_create(products)
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")




    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


# class ProductInline(admin.StackedInline):
class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductInline
    ]
    list_display = 'pk', 'delivery_adress', 'promocode', 'created_at', 'user_verbose', 'get_products'
    search_fields = 'delivery_adress', 'created_at'

    def get_products(self, instance):
        return [product.name for product in instance.products.all()]

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        scv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(scv_file)
        orders = []
        for row in reader:
            order = Order(
                delivery_adress=row['delivery_adress'],
                promocode=row['promocode'],
                user_id=row['user'],
            )
            order.save()
            for product in convert_str_to_int_list(row['products']):
                order.products.add(product)
            orders.append(order)
        return orders


        # orders = [Order(**row) for row in reader]
        # Order.objects.bulk_create(orders)
        # self.message_user(request, "Data from CSV was imported")
        # return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            )
        ]
        return new_urls + urls
