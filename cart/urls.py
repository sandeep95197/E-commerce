from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-ajax/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    # Guest cart URLs
    path('update-guest/<int:item_id>/', views.update_guest_cart, name='update_guest_cart'),
    path('remove-guest/<int:item_id>/', views.remove_guest_cart, name='remove_guest_cart'),
    path('clear-guest/', views.clear_guest_cart, name='clear_guest_cart'),
]

