from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'price', 'stock', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }


# Register LogEntry to show history in admin
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('action_flag', 'action_time', 'content_type')
    search_fields = ('user__username', 'object_repr', 'change_message')
    readonly_fields = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message', 'object_id')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }
