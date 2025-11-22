from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('buy/<int:id>/', views.create_checkout_session, name='create_checkout_session'),
    path('order/<int:order_id>/buy/', views.create_order_checkout_session, name='create_order_checkout_session'),
    path('payment-intent/<int:id>/', views.create_payment_intent, name='create_payment_intent'),
]