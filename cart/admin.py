from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'get_total_price', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price', 'added_at')
    search_fields = ('product__name', 'cart__user__username')
    list_filter = ('added_at',)
    readonly_fields = ('added_at',)
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }

