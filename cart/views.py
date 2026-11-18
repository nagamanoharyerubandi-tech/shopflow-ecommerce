from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__category').all()
    
    # Check if any item in cart exceeds current stock
    stock_warning = False
    for item in cart_items:
        if item.quantity > item.product.stock:
            stock_warning = True
            break

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'stock_warning': stock_warning,
    }
    return render(request, 'cart/cart.html', context)


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_or_create_cart(request)

    # Quantity from request
    try:
        quantity = int(request.POST.get('quantity', request.GET.get('quantity', 1)))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    # Check if product is in stock
    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'"{product.name}" is currently out of stock.'}, status=400)
        messages.error(request, f'Sorry, "{product.name}" is out of stock.')
        return redirect('products:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        if quantity > product.stock:
            cart_item.quantity = product.stock
            cart_item.save()
            msg = f'Added {product.stock} of "{product.name}" (maximum available in stock).'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            msg = f'"{product.name}" has been added to your shopping cart.'
    else:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            cart_item.quantity = product.stock
            cart_item.save()
            msg = f'Updated quantity to {product.stock} for "{product.name}" (max available stock).'
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            msg = f'Updated "{product.name}" quantity in your cart.'

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'cart_grand_total': str(cart.grand_total),
        })

    messages.success(request, msg)
    next_url = request.POST.get('next', request.GET.get('next'))
    if next_url == 'checkout':
        return redirect('orders:checkout')
    if next_url:
        return redirect(next_url)
    return redirect('cart:cart_detail')


def cart_update(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action', request.GET.get('action'))
    qty_val = request.POST.get('quantity', request.GET.get('quantity'))

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
            msg = "Quantity updated."
        else:
            msg = f"Cannot add more. Only {cart_item.product.stock} items in stock."
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg, 'current_quantity': cart_item.quantity}, status=400)
            messages.warning(request, msg)
            return redirect('cart:cart_detail')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            msg = "Quantity updated."
        else:
            cart_item.delete()
            msg = f'"{cart_item.product.name}" removed from cart.'
    elif qty_val is not None:
        try:
            qty = int(qty_val)
            if qty <= 0:
                cart_item.delete()
                msg = f'"{cart_item.product.name}" removed from cart.'
            elif qty > cart_item.product.stock:
                cart_item.quantity = cart_item.product.stock
                cart_item.save()
                msg = f"Set to maximum available stock ({cart_item.product.stock})."
            else:
                cart_item.quantity = qty
                cart_item.save()
                msg = "Quantity updated."
        except ValueError:
            msg = "Invalid quantity provided."

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': msg,
            'item_quantity': cart_item.quantity if cart_item.pk else 0,
            'item_total': str(cart_item.total_price) if cart_item.pk else '0.00',
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'cart_tax': str(cart.tax),
            'cart_shipping': str(cart.shipping_fee),
            'cart_grand_total': str(cart.grand_total),
        })

    messages.info(request, msg)
    return redirect('cart:cart_detail')


def cart_remove(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product_name}" removed from cart.',
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'cart_grand_total': str(cart.grand_total),
        })

    messages.info(request, f'"{product_name}" was removed from your cart.')
    return redirect('cart:cart_detail')


def cart_clear(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.info(request, "Your shopping cart has been cleared.")
    return redirect('cart:cart_detail')
