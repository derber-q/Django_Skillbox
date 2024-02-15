from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from shopapp.models import Order, Product
from typing import Sequence
from django.contrib.auth.models import User


class Command(BaseCommand):
    '''
    Creates order
    '''
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Start demo bulk actions')

        Product.objects.filter(
            name__contains="Smartphone"
        ).update(discount=10)


        # info = [
        #     ('Smartphone 1', 199),
        #     ('Smartphone 2', 299),
        #     ('Smartphone 3', 399),
        # ]
        # products = [
        #     Product(name=name, prise=prise)
        #     for name, prise in info
        # ]
        # result = Product.objects.bulk_create(products)
        # for obj in result:
        #     print(obj)

        self.stdout.write('Done')