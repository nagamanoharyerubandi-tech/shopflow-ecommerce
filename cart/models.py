from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username} ({self.id})"
        return f"Anonymous Cart ({self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_savings(self):
        return sum(item.total_savings for item in self.items.all())

    @property
    def shipping_fee(self):
        # Free delivery if subtotal >= 499, else 49.00
        if self.subtotal >= Decimal('499.00') or self.subtotal == Decimal('0.00'):
            return Decimal('0.00')
        return Decimal('49.00')

    @property
    def tax(self):
        # 5% standard tax
        return round(self.subtotal * Decimal('0.05'), 2)

    @property
    def grand_total(self):
        return self.subtotal + self.shipping_fee + self.tax


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.current_price * self.quantity

    @property
    def original_total_price(self):
        return self.product.price * self.quantity

    @property
    def total_savings(self):
        return self.product.savings * self.quantity

    @property
    def is_stock_available(self):
        return self.product.stock >= self.quantity
