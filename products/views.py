from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    """Display all products"""
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def product_detail(request, product_id):
    """Display product details"""
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'products/product_detail.html', {'product': product})
