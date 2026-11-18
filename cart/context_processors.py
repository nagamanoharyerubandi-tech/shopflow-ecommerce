from .utils import get_or_create_cart


def cart_context(request):
    try:
        cart = get_or_create_cart(request)
        total_items = cart.total_items
        subtotal = cart.subtotal
    except Exception:
        cart = None
        total_items = 0
        subtotal = 0
    return {
        'cart': cart,
        'cart_total_items': total_items,
        'cart_subtotal': subtotal,
    }
