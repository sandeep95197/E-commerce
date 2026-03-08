from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import uuid
from cart.models import Cart, CartItem
from .models import Order, OrderItem


@login_required(login_url='login')
def checkout(request):
    """Display checkout form"""
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')
    
    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required(login_url='login')
def process_checkout(request):
    """Process checkout and redirect to payment"""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            
            # Generate unique order number
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate totals
            subtotal = cart.get_total_price()
            shipping_cost = 0 if subtotal > 50 else 5.99
            tax = subtotal * 0.08  # 8% tax
            total = subtotal + shipping_cost + tax
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                street_address=request.POST.get('street_address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                country=request.POST.get('country'),
                total_amount=total,
                shipping_cost=shipping_cost,
                tax_amount=tax,
            )
            
            # Create order items from cart
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity
                )
            
            # NOTE: Cart will be cleared AFTER successful payment in process_payment view
            # This allows users to go back to cart if they want to modify their order
            
            # Redirect to payment
            return redirect('payment', order_id=order.id)
        except Exception as e:
            messages.error(request, f'Error processing checkout: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')


@login_required(login_url='login')
def payment(request, order_id):
    """Display payment form"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment.html', {'order': order})


@login_required(login_url='login')
def process_payment(request, order_id):
    """Process payment for an order"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Simulate payment processing
        # In a real application, you would integrate with a payment gateway like Stripe, PayPal, etc.
        
        # For demo purposes, we'll mark the order as paid
        order.payment_status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # Clear the cart AFTER successful payment
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        
        messages.success(request, f'Payment successful! Your order {order.order_number} has been placed.')
        return redirect('order_history')
    
    return redirect('payment', order_id=order_id)


@login_required(login_url='login')
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required(login_url='login')
def quick_payment(request):
    """Quick payment - creates order and goes directly to payment page"""
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')
    
    try:
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate totals
        subtotal = cart.get_total_price()
        shipping_cost = 0 if subtotal > 50 else 5.99
        tax = subtotal * 0.08  # 8% tax
        total = subtotal + shipping_cost + tax
        
        # Get user's last order for default shipping info
        last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        
        # Create order with default or empty shipping info
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            first_name=last_order.first_name if last_order else request.user.first_name or '',
            last_name=last_order.last_name if last_order else request.user.last_name or '',
            email=last_order.email if last_order else request.user.email or '',
            phone=last_order.phone if last_order else '',
            street_address=last_order.street_address if last_order else '',
            city=last_order.city if last_order else '',
            state=last_order.state if last_order else '',
            postal_code=last_order.postal_code if last_order else '',
            country=last_order.country if last_order else 'US',
            total_amount=total,
            shipping_cost=shipping_cost,
            tax_amount=tax,
        )
        
        # Create order items from cart
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity
            )
        
        # Redirect to payment page
        messages.info(request, 'Please complete your payment for order ' + order_number)
        return redirect('payment', order_id=order.id)
        
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('cart')

