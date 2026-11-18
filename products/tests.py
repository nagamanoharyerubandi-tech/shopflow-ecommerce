from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product
from decimal import Decimal


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', icon='bi-laptop')
        self.product = Product.objects.create(
            category=self.category,
            name='Wireless Headphones',
            price=Decimal('2000.00'),
            discount_price=Decimal('1500.00'),
            stock=10,
            is_available=True
        )

    def test_product_current_price_and_discount(self):
        self.assertEqual(self.product.current_price, Decimal('1500.00'))
        self.assertEqual(self.product.discount_percentage, 25)
        self.assertEqual(self.product.savings, Decimal('500.00'))
        self.assertTrue(self.product.in_stock)

    def test_home_page_loads(self):
        response = self.client.get(reverse('products:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ShopFlow')

    def test_product_list_loads(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wireless Headphones')

    def test_product_detail_loads(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wireless Headphones')
