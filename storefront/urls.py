from django.urls import path
from .views import index, add_to_cart, cart_cancel, cart_checkout
from .views import checkout_pay, checkout_cancel, payment_verify, payment_cancel

urlpatterns = [
    path('', index, name='home'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('cart-checkout/', cart_checkout, name='cart-checkout'),
    path('cart-cancel/', cart_cancel, name='cart-cancel'),
    path('checkout-pay/', checkout_pay, name='checkout-pay'),
    path('checkout-cancel/', checkout_cancel, name='checkout-cancel'),
    path('payment-verify/', payment_verify, name='payment-verify'),
    path('payment-cancel/', payment_cancel, name='payment-cancel'),

]
