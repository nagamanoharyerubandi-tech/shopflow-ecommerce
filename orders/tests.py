from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order
from decimal import Decimal


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testbuyer', password='password123', email='buyer@test.com')
        self.category = Category.objects.create(name='Audio')
        self.product = Product.objects.create(
            category=self.category,
            name='Earbuds',
            price=Decimal('1000.00'),
            stock=10,
            is_available=True
        )

    def test_place_order_and_stock_deduction(self):
        self.client.login(username='testbuyer', password='password123')
        
        # Add to cart
        self.client.get(reverse('cart:cart_add', kwargs={'product_id': self.product.id}))

        # Place Order
        order_data = {
            'use_new_address': '1',
            'full_name': 'Test Buyer',
            'phone': '9876543210',
            'address_line_1': '123 Main Street',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'postal_code': '400001',
            'country': 'India',
            'payment_method': 'COD',
        }
        response = self.client.post(reverse('orders:place_order'), order_data, follow=True)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.items.count(), 1)

        # Stock should be decremented from 10 to 9
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

        # Cart should be empty
        cart = Cart.objects.filter(user=self.user).first()
        self.assertEqual(cart.items.count(), 0)

    def test_order_cancellation_restores_stock(self):
        self.client.login(username='testbuyer', password='password123')
        
        # Add to cart & place order
        self.client.get(reverse('cart:cart_add', kwargs={'product_id': self.product.id}))
        order_data = {
            'use_new_address': '1',
            'full_name': 'Test Buyer',
            'phone': '9876543210',
            'address_line_1': '123 Main Street',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'postal_code': '400001',
            'payment_method': 'COD',
        }
        self.client.post(reverse('orders:place_order'), order_data)
        
        order = Order.objects.filter(user=self.user).first()
        self.assertEqual(order.status, 'Pending')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

        # Cancel Order
        cancel_url = reverse('orders:order_cancel', kwargs={'order_number': order.order_number})
        self.client.post(cancel_url, {'reason': 'Changed my mind'}, follow=True)

        order.refresh_from_db()
        self.assertEqual(order.status, 'Cancelled')
        
        # Stock should be restored to 10
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
