from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'email')
    list_filter = ('status', 'payment_status', 'created_at')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('Shipping Address', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'street_address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_id', 'total_amount', 'shipping_cost', 'tax_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'product_price', 'get_total_price')
    search_fields = ('product_name', 'order__order_number')
    list_filter = ('order__created_at',)
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }

