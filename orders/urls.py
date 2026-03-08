from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('process/', views.process_checkout, name='process_checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('history/', views.order_history, name='order_history'),
    path('quick-payment/', views.quick_payment, name='quick_payment'),
]

