from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product
from cart.models import Cart, CartItem
from decimal import Decimal


class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Gadgets')
        self.product = Product.objects.create(
            category=self.category,
            name='Smart Watch',
            price=Decimal('5000.00'),
            discount_price=Decimal('4000.00'),
            stock=5,
            is_available=True
        )

    def test_add_to_cart(self):
        response = self.client.get(reverse('cart:cart_add', kwargs={'product_id': self.product.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.total_items, 1)
        self.assertEqual(cart.subtotal, Decimal('4000.00'))

    def test_cart_quantity_controls(self):
        # Add item
        self.client.get(reverse('cart:cart_add', kwargs={'product_id': self.product.id}))
        cart = Cart.objects.first()
        item = cart.items.first()

        # Increase
        self.client.get(f"{reverse('cart:cart_update', kwargs={'item_id': item.id})}?action=increase")
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        # Decrease
        self.client.get(f"{reverse('cart:cart_update', kwargs={'item_id': item.id})}?action=decrease")
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_cannot_exceed_stock(self):
        # Add 10 when stock is 5
        response = self.client.post(
            reverse('cart:cart_add', kwargs={'product_id': self.product.id}),
            {'quantity': 10},
            follow=True
        )
        cart = Cart.objects.first()
        item = cart.items.first()
        self.assertEqual(item.quantity, 5)  # Capped at stock
