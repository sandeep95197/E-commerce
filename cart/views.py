from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem


def get_cart_count(request):
    """Get cart count for session or user"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return cart.get_total_items()
        except Cart.DoesNotExist:
            return 0
    else:
        cart = request.session.get('cart', {})
        return sum(item.get('quantity', 0) for item in cart.values())


def cart_view(request):
    """Display user's cart"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
    else:
        # Guest user - get cart from session
        cart_data = request.session.get('cart', {})
        # Create a mock cart object for template rendering
        class GuestCart:
            def __init__(self, items):
                self.items = items
                self.is_guest = True
            
            def get_total_items(self):
                return sum(item.get('quantity', 0) for item in self.items.values())
            
            def get_total_price(self):
                return sum(float(item.get('price', 0)) * item.get('quantity', 0) for item in self.items.values())
        
        cart = GuestCart(cart_data)
    
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Stock validation
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock!')
        return redirect('product_list')
    
    if request.user.is_authenticated:
        # Logged-in user - use database cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
        
        # Check if item already in cart and validate total quantity
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                available = product.stock - cart_item.quantity
                if available <= 0:
                    messages.error(request, f'Sorry, you already have all available {product.stock} items in cart!')
                else:
                    messages.error(request, f'Sorry, only {available} more items available!')
                return redirect('product_list')
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'{product.name} quantity updated in cart!')
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            messages.success(request, f'{product.name} added to cart!')
    else:
        # Guest user - use session-based cart
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            new_quantity = cart[product_id_str]['quantity'] + quantity
            if new_quantity > product.stock:
                available = product.stock - cart[product_id_str]['quantity']
                if available <= 0:
                    messages.error(request, f'Sorry, you already have all available {product.stock} items in cart!')
                else:
                    messages.error(request, f'Sorry, only {available} more items available!')
                return redirect('product_list')
            cart[product_id_str]['quantity'] = new_quantity
            messages.success(request, f'{product.name} quantity updated in cart!')
        else:
            cart[product_id_str] = {
                'product_id': product_id,
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else None
            }
            messages.success(request, f'{product.name} added to cart!')
        
        request.session['cart'] = cart
    
    return redirect('product_list')


@login_required(login_url='login')
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        messages.success(request, 'Cart updated!')
    
    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('cart')


@login_required(login_url='login')
def clear_cart(request):
    """Clear entire cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        messages.success(request, 'Cart cleared!')
    except Cart.DoesNotExist:
        pass
    
    return redirect('cart')


@require_POST
def add_to_cart_ajax(request, product_id):
    """AJAX add product to cart"""
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Stock validation
    if quantity > product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Sorry, only {product.stock} items available in stock!'
        })
    
    if request.user.is_authenticated:
        # Logged-in user - use database cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
        
        # Check if item already in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                available = product.stock - cart_item.quantity
                return JsonResponse({
                    'success': False,
                    'message': f'Sorry, only {available} more items available!'
                })
            cart_item.quantity = new_quantity
            cart_item.save()
            message = f'{product.name} quantity updated in cart!'
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            message = f'{product.name} added to cart!'
        
        cart_count = cart.get_total_items()
        cart_total = float(cart.get_total_price())
    else:
        # Guest user - use session-based cart
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            new_quantity = cart[product_id_str]['quantity'] + quantity
            if new_quantity > product.stock:
                available = product.stock - cart[product_id_str]['quantity']
                return JsonResponse({
                    'success': False,
                    'message': f'Sorry, only {available} more items available!'
                })
            cart[product_id_str]['quantity'] = new_quantity
            message = f'{product.name} quantity updated in cart!'
        else:
            cart[product_id_str] = {
                'product_id': product_id,
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else None
            }
            message = f'{product.name} added to cart!'
        
        request.session['cart'] = cart
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
        cart_total = sum(float(item.get('price', 0)) * item.get('quantity', 0) for item in cart.values())
    
    return JsonResponse({
        'success': True,
        'message': message,
        'cart_count': cart_count,
        'cart_total': cart_total
    })


def update_guest_cart(request, item_id):
    """Update guest cart item"""
    if request.user.is_authenticated:
        return redirect('cart')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        item_id_str = str(item_id)
        
        if item_id_str in cart:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[item_id_str]['quantity'] = quantity
                messages.success(request, 'Cart updated!')
            else:
                del cart[item_id_str]
                messages.success(request, 'Item removed from cart!')
            
            request.session['cart'] = cart
    
    return redirect('cart')


def remove_guest_cart(request, item_id):
    """Remove item from guest cart"""
    if request.user.is_authenticated:
        return redirect('cart')
    
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        del cart[item_id_str]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart!')
    
    return redirect('cart')


def clear_guest_cart(request):
    """Clear entire guest cart"""
    if request.user.is_authenticated:
        return redirect('cart')
    
    if 'cart' in request.session:
        del request.session['cart']
        messages.success(request, 'Cart cleared!')
    
    return redirect('cart')

