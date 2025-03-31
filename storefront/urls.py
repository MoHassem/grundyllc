from django.urls import path
from .views import index, simulate_user_login, add_to_cart, cart_cancel, cart_checkout
from .views import checkout_pay, checkout_cancel, payment_verify, payment_complete

urlpatterns = [
    path('', index, name='home'),
    path('simlogin/', simulate_user_login, name='sim-login'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('cart-checkout/', cart_checkout, name='cart-checkout'),
    path('cart-cancel/', cart_cancel, name='cart-cancel'),
    path('checkout-pay/', checkout_pay, name='checkout-pay'),
    path('checkout-cancel/', checkout_cancel, name='checkout-cancel'),
    path('payment-complete/', payment_complete, name='payment-complete'),
    path('payment-verify/', payment_verify, name='payment-verify'),
]
