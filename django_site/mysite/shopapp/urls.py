from django.urls import path,include
from django.views.decorators.cache import cache_page

from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductsListView,
    OrdersListView,
    OrderUpdateView,
    OrderDeleteView,
    ProductCreateView,
    create_order,
    ProductDetailsView,
    OrderDetailView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    OrderDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrderDataExportView,

)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path('api/', include(routers.urls)),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', UserOrderDataExportView.as_view(), name='orders-export'),
    path('shopindex', cache_page(60 * 2)(ShopIndexView.as_view()), name='index'),
    path('groups/', GroupsListView.as_view(), name='groups_list'),
    path('', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsDataExportView.as_view(), name='products-export'),
    path('products/<int:pk>', ProductDetailsView.as_view(), name='products_details'),
    path('products/create/', ProductCreateView.as_view(), name='create_product'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='update_product'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete_product'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/export/', OrderDataExportView.as_view(), name='orders-export'),
    path('products/latest/feed/', LatestProductsFeed(), name='products-feed'),
]