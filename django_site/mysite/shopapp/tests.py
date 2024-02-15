from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client

from mysite import settings
from shopapp.models import Product, Order
from .utils import add_two_numbers
from django.urls import reverse
from string import ascii_letters
from random import choices

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(3, 3)
        self.assertEquals(result, 6)

# class ProductCreateViewTestCase(TestCase):
#     def setup(self) -> None:
#         # product_name = ''.join(choices(ascii_letters, k=10))
#         self.product.name = ''.join(choices(ascii_letters, k=10))
#         Product.objects.filter(name=self.product.name).delete()
#
#     def test_create_product(self):
#         print(self.__dict__)
#         response = self.client.post(
#             reverse('shopapp:create_product'),
#             {
#                 'name': self.product.name,
#                 'prise': "123.45",
#                 'description': "A good table",
#                 'discount': "10"
#
#             }
#         )
#         self.assertRedirects(response, reverse("shopapp:products_list"))
#         self.assertTrue(
#             Product.objects.filter(name=self.product.name).exists()
#         )

class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")
    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
    def test_get_product_and_chek_content(self):
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk})
        )
        self.assertEquals(response.status_code, 200)
    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)

class ProductsListViewTestVase(TestCase):
    fixtures = [
        'products-fixtures.json',
        ]
    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/prodoucts-list.html')



class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'users-fixtures.json',
        'products-fixtures.json'
    ]
    def test_get_poducts_view(self):
        response = self.client.get(
            reverse('shopapp:products-export')
        )
        self.assertEquals(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "prise": str(product.prise),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEquals(
            products_data['products'],
            expected_data,
        )

class OrderListView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='test')
    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
    def setUp(self) -> None:
        self.client.force_login(self.user)
    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')
    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertIn(str(settings.LOGIN_URL), response.url)
        self.assertEquals(response.status_code, 302)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='QWE123asdAdfbe22')
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()


    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_adress='Kolotiy 34',
            promocode="66",
            user=self.user,
        )
    def tearDown(self) -> None:
        self.order.delete()
    def test_order_details(self):
        response = self.client.get(reverse('shopapp:order_details', kwargs={'pk': self.order.pk}))
        self.assertContains(response, self.order.delivery_adress)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, self.order.pk)

class OrdersExportViewTestCase(TestCase):
    fixtures = [
        'orders-fixtures.json',
        'users-fixtures.json',
        'products-fixtures.json'
    ]
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='QWE123asdAdfbe22')
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()


    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(
            reverse('shopapp:orders-export'),
        )
        self.assertEquals(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
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
        order_data = response.json()
        self.assertEquals(
            order_data["orders"],
            expected_data,
        )

