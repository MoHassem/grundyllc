import random

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

from config.models import StorefrontConfiguration, Store, DeliveryPartner
from paystack.payment import initialise_payment, verify_payment

users = {
    '1': {'name': 'John Doe', 'address': '123 Main St', 'email': 'john.doe@example.com',
          'cell': '555-123-4567', 'distance': 2.0},
    '2': {'name': 'Jane Smith', 'address': '456 Elm St', 'email': 'jane.smith@example.com',
          'cell': '555-987-6543', 'distance': 5.0},
    '3': {'name': 'Peter Jones', 'address': '789 Oak St', 'email': 'peter.jones@example.com',
          'cell': '555-111-2222', 'distance': 3.0},

}

def get_total(cart):
    total = 0.00
    if cart:
        total = sum(item['price'] for item in cart)
    return total

def get_printable_cart(cart):
    if not cart:
        return []
    cp_cart = []
    for item in cart:
        cp_cart.append({
            'product': item['product'],
            'price': item['price'],
            'quantity': item['quantity'],
        })
    for item in cp_cart:
        item['price'] = f'R{item['price']:.2f}'
    return cp_cart

def get_store_name(store_id):
    if store_id == '0':
        return ''
    store = Store.objects.filter(pk=int(store_id)).first()
    if not store:
        return ''
    else:
        return store.business_name

def get_delivery_charge(request):
    user_id = request.session.get('user_id', '1')
    config = StorefrontConfiguration.objects.get(pk=1)
    distance = users[user_id]['distance']
    if distance > config.threshold_distance_km:
        return (
                (float(config.threshold_distance_km) * distance)
                + ((distance - float(config.threshold_distance_km))
                * float(config.additional_charge_per_km + config.delivery_charge_per_km))
        )
    return distance * float(config.delivery_charge_per_km)

def get_delivery_partner():
    partner_ids = DeliveryPartner.objects.values_list('id', flat=True)
    p_id = random.choice(partner_ids)
    partner = DeliveryPartner.objects.get(pk=p_id)
    return partner.id, partner.name

def get_delivery_partner_account_code(p_id):
    partner = DeliveryPartner.objects.get(pk=p_id)
    return partner.subaccount_code

def index(request):
    cart = request.session.get('cart', [])
    delivery = request.session.get('delivery', 0.00)
    s_checkout = request.session.get('checkout', 'no')
    user_id = request.session.get('user_id', '1')
    cart_store = request.session.get('cart_store', '0')
    dp_id, dp_name, = get_delivery_partner()
    request.session['delivery_partner_id'] = dp_id
    request.session['delivery_partner'] = dp_name

    total = get_total(cart)
    formatted_cart = get_printable_cart(cart)

    context = {
        'cart': formatted_cart,
        'total': f'R{total:.2f}',
        'checkout': s_checkout,
        'delivery': f'R{delivery:.2f}',
        'users': [{'id': k, 'username': user['name']} for k, user in users.items()],
        'user_name': users[user_id]['name'],
        'address': users[user_id]['address'],
        'store_name': get_store_name(cart_store),
        'delivery_partner': dp_name,
    }

    return render(request, 'storefront/index.html', context)

def add_to_cart(request):

    s_checkout = request.session.get('checkout', 'no')
    cart_store = request.session.get('cart_store', '0')
    delivery = request.session.get('delivery', 0.00)
    cart = request.session.get('cart', [])

    if s_checkout != 'yes':
        if request.method == 'POST':
            item_store = request.POST.get('store')

            if cart_store == '0':
                request.session['cart_store'] = item_store
                cart_store = item_store

            if item_store == cart_store:
                product = request.POST.get('product')
                price = float(request.POST.get('price'))
                quantity = int(request.POST.get('quantity'))

                cart = request.session.get('cart', [])

                item_exists = False
                for item in cart:
                    if item['product'] == product:
                        item['quantity'] += quantity
                        item_exists = True
                        break

                if not item_exists:
                    cart.append({'product': product, 'price': price, 'quantity': quantity})

                request.session['cart'] = cart


        if delivery == 0.0:
            delivery = get_delivery_charge(request)
            request.session['delivery'] = delivery

        total = get_total(cart)
        formatted_cart = get_printable_cart(cart)

        context = {
            'cart': formatted_cart,
            'total': f'R{total:.2f}',
            'checkout': s_checkout,
            'delivery': f'R{delivery:.2f}',
            'store_name': get_store_name(cart_store),
        }

        template = loader.get_template('storefront/cart_items.html')
        return HttpResponse(template.render(context, request))


def cart_checkout(request):
    s_checkout = request.session.get('checkout', 'no')
    if s_checkout == 'no':
        s_checkout = 'yes'
        request.session['checkout'] = s_checkout
    delivery = request.session.get('delivery', 0.0)
    cart = request.session.get('cart', [])
    cart_store = request.session.get('cart_store', '0')
    dp_id, dp_name, = get_delivery_partner()
    request.session['delivery_partner_id'] = dp_id
    request.session['delivery_partner'] = dp_name

    total = get_total(cart)
    formatted_cart = get_printable_cart(cart)

    context = {
        'cart': formatted_cart,
        'total': f'{total:.2f}', 
        'delivery': f'R{delivery:.2f}',
        'checkout': s_checkout,
        'store_name': get_store_name(cart_store),
        'delivery_partner': dp_name,
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def cart_cancel(request):
    request.session['cart'] = []
    request.session['checkout'] = 'no'
    request.session['cart_store'] = '0'
    request.session['delivery'] = 0.00
    request.session['delivery_partner_id'] = None
    request.session['delivery_partner'] = None
    s_checkout = 'no'
    cart = []
    cart_store = '0'
    total = get_total(cart)
    formatted_cart = get_printable_cart(cart)
    delivery = 0.00

    context = {
        'cart': formatted_cart,
        'total': f'{total:.2f}',
        'delivery': f'R{delivery:.2f}',
        'checkout': s_checkout,
        'store_name': get_store_name(cart_store),
        'delivery_partner': None,
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def checkout_pay(request):

    cart = request.session.get('cart', [])
    delivery = int(request.session.get('delivery', 0.00) * 100)

    user_id = request.session.get('user_id', '1')

    total = int(get_total(cart)  * 100)
    my_share = int(total * 0.125)
    store_total = total - my_share

    cart_store = request.session.get('cart_store', '0')
    stores = Store.objects.filter(pk=cart_store).first()

    p_id = request.session.get('delivery_partner_id', '1')
    delivery_sub_account = get_delivery_partner_account_code(p_id)

    success_url = "https://b996-41-193-87-145.ngrok-free.app/payment-verify/"
    cancel_url = "https://b996-41-193-87-145.ngrok-free.app/checkout-cancel/"

#
    p_data = initialise_payment(
        customer_email=users[user_id]['email'],
        total_amount=total + delivery,
        store_subaccount=stores.subaccount_code,
        store_amount=store_total,
        delivery_subaccount=delivery_sub_account,
        delivery_amount=delivery,
        callback_url=success_url,
        metadata={'cancel_action': cancel_url}
    )

    if p_data and 'authorization_url' in p_data:
        request.session['p_data'] = p_data
        redirect_url = p_data['authorization_url']
        return HttpResponse(
            f'<div hx-get="{redirect_url}" hx-trigger="load"></div>'
        )
    else:
        print(f'Payment initialization failed: {p_data}')

def payment_verify(request):
    p_data = request.session.get('p_data', {})
    p_reference = p_data.get('reference', None)

    if p_reference is None:
         return HttpResponse("Payment initialization failed.", status=500)

    v_data = verify_payment(reference=p_reference)

    if v_data and v_data['status'] == 'success':
        return HttpResponse(
            f'<div hx-get="/payment-complete/" hx-trigger="load"></div>'
        )
    else:
        return HttpResponse("Payment failed", status=500)

def checkout_cancel(request):
    cart = request.session.get('cart', [])
    delivery = request.session.get('delivery', 0.00)
    user_id = request.session.get('user_id', '1')
    cart_store = request.session.get('cart_store', '0')
    s_checkout = 'no'
    request.session['checkout'] = s_checkout

    total = get_total(cart)
    formatted_cart = get_printable_cart(cart)

    context = {
        'cart': formatted_cart,
        'total': f'R{total:.2f}',
        'checkout': s_checkout,
        'delivery': f'R{delivery:.2f}',
        'users': [{'id': k, 'username': user['name']} for k, user in users.items()],
        'user_name': users[user_id]['name'],
        'address': users[user_id]['address'],
        'store_name': get_store_name(cart_store),
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))


def payment_complete(request):
    request.session['cart'] = []
    request.session['checkout'] = 'no'
    request.session['cart_store'] = '0'
    request.session['delivery'] = 0.00
    request.session['delivery_partner_id'] = None
    request.session['delivery_partner'] = None
    s_checkout = 'no'
    cart = []
    cart_store = '0'
    total = get_total(cart)
    formatted_cart = get_printable_cart(cart)
    delivery = 0.00

    context = {
        'cart': formatted_cart,
        'total': f'{total:.2f}',
        'delivery': f'R{delivery:.2f}',
        'checkout': s_checkout,
        'store_name': get_store_name(cart_store),
        'delivery_partner': None,
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))


def simulate_user_login(request):
    user_id = request.session.get('user_id',1)
    request.session['delivery'] = 0.0

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id in users:
            request.session['user_id'] = user_id  # Store user_id in session

    context = {
        'users': [{'id': k, 'username': user['name']} for k, user in users.items()],
        'user_name': users[user_id]['name'],
        'address': users[user_id]['address'],
    }
    return render(request, 'storefront/user_selection.html', context)
