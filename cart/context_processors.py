from .models import Cart


def cart_context(request):
    """Context processor to make cart available in all templates"""
    cart_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.get_total_items()
            cart_total = cart.get_total_price()
        except Cart.DoesNotExist:
            pass
    else:
        # Guest user - get cart from session
        cart = request.session.get('cart', {})
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
        cart_total = sum(float(item.get('price', 0)) * item.get('quantity', 0) for item in cart.values())
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }

