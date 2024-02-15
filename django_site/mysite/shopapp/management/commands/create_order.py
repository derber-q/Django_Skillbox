from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from shopapp.models import Order, Product
from typing import Sequence


class Command(BaseCommand):
    '''
    Creates order
    '''
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Create order with products')
        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.only('id').all()
        order, created = Order.objects.get_or_create(
            delivery_adress='ul Gorkogo, d106',
            promocode='Osen',
            user=user
        )
        for product in products:
            order.products.add(product)
        self.stdout.write(self.style.SUCCESS('Create order'))