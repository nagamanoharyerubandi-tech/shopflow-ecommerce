from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import uuid

from cart.utils import get_or_create_cart
from accounts.models import Address
from products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm, OrderCancelForm


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is currently empty. Add items before proceeding to checkout.")
        return redirect('products:home')

    # Check stock for all items
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Insufficient stock for "{item.product.name}". Available: {item.product.stock}. Please adjust your cart quantity.')
            return redirect('cart:cart_detail')

    addresses = Address.objects.filter(user=request.user)
    form = CheckoutForm(user=request.user)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def place_order_view(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('products:home')

    form = CheckoutForm(request.user, request.POST)
    if not form.is_valid():
        messages.error(request, "Please check the delivery and payment information.")
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'cart_items': cart_items,
            'addresses': addresses,
            'form': form,
        })

    cd = form.cleaned_data
    selected_address = cd.get('selected_address')
    use_new_address = cd.get('use_new_address')

    # Determine shipping address details
    if selected_address and not use_new_address:
        full_name = selected_address.full_name
        phone = selected_address.phone
        address_line_1 = selected_address.address_line_1
        address_line_2 = selected_address.address_line_2
        city = selected_address.city
        state = selected_address.state
        postal_code = selected_address.postal_code
        country = selected_address.country
    else:
        full_name = cd.get('full_name')
        phone = cd.get('phone')
        address_line_1 = cd.get('address_line_1')
        address_line_2 = cd.get('address_line_2')
        city = cd.get('city')
        state = cd.get('state')
        postal_code = cd.get('postal_code')
        country = cd.get('country') or 'India'

        # Save address if checked
        if cd.get('save_address'):
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                is_default=not Address.objects.filter(user=request.user).exists()
            )

    payment_method = cd.get('payment_method')
    notes = cd.get('order_notes')

    try:
        with transaction.atomic():
            # Validate stock again in transaction
            for item in cart_items:
                product = Product.objects.select_for_update().get(id=item.product.id)
                if item.quantity > product.stock:
                    messages.error(request, f'Sorry, "{product.name}" has only {product.stock} items remaining.')
                    return redirect('cart:cart_detail')

            # Create Order
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=request.user.email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                subtotal=cart.subtotal,
                shipping_fee=cart.shipping_fee,
                tax=cart.tax,
                discount=cart.total_savings,
                grand_total=cart.grand_total,
                payment_method=payment_method,
                payment_status='Paid' if payment_method == 'ONLINE' else 'Pending',
                payment_id=f"TXN-{uuid.uuid4().hex[:10].upper()}" if payment_method == 'ONLINE' else None,
                status='Processing' if payment_method == 'ONLINE' else 'Pending',
                notes=notes,
            )

            # Create OrderItems and decrement stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_image=item.product.display_image,
                    price=item.product.current_price,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                # Decrement stock
                item.product.stock -= item.quantity
                item.product.save()

            # Clear cart
            cart.items.all().delete()

        messages.success(request, f"Order #{order.order_number} has been placed successfully!")
        return redirect('orders:order_confirmation', order_number=order.order_number)

    except Exception as e:
        messages.error(request, f"An error occurred while placing your order: {str(e)}")
        return redirect('orders:checkout')


@login_required
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    status_filter = request.GET.get('status', 'all')
    orders = Order.objects.filter(user=request.user).prefetch_related('items')

    if status_filter != 'all':
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    cancel_form = OrderCancelForm()
    
    context = {
        'order': order,
        'cancel_form': cancel_form,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_cancel_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if not order.can_cancel:
        messages.error(request, f"Order #{order.order_number} cannot be cancelled at this stage ({order.status}).")
        return redirect('orders:order_detail', order_number=order.order_number)

    if request.method == 'POST':
        form = OrderCancelForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Restore stock
                for item in order.items.all():
                    if item.product:
                        item.product.stock += item.quantity
                        item.product.save()

                order.status = 'Cancelled'
                order.cancellation_reason = form.cleaned_data.get('reason')
                if order.payment_status == 'Paid':
                    order.payment_status = 'Refunded'
                order.save()

            messages.success(request, f"Order #{order.order_number} has been cancelled successfully.")
            return redirect('orders:order_detail', order_number=order.order_number)

    return redirect('orders:order_detail', order_number=order.order_number)


@login_required
def order_invoice_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_invoice.html', {'order': order})
