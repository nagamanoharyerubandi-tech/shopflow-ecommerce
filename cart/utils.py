from .models import Cart, CartItem


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Check if user already has an active cart
        user_cart = Cart.objects.filter(user=request.user).first()
        if not user_cart:
            user_cart = Cart.objects.create(user=request.user)

        # Check if there is an anonymous session cart to merge
        if session_key:
            anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if anon_cart and anon_cart.id != user_cart.id:
                for anon_item in anon_cart.items.all():
                    existing_item = user_cart.items.filter(product=anon_item.product).first()
                    if existing_item:
                        # Cap at product stock
                        new_qty = min(existing_item.quantity + anon_item.quantity, anon_item.product.stock)
                        existing_item.quantity = new_qty
                        existing_item.save()
                    else:
                        CartItem.objects.create(
                            cart=user_cart,
                            product=anon_item.product,
                            quantity=min(anon_item.quantity, anon_item.product.stock)
                        )
                # Delete anonymous cart after merge
                anon_cart.delete()
        return user_cart
    else:
        # Anonymous user cart by session key
        anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
        if not anon_cart:
            anon_cart = Cart.objects.create(session_key=session_key)
        return anon_cart
