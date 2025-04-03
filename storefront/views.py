import random
from decimal import Decimal

from django.db.models import UUIDField

import storefront.utilities as ut

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

from config.models import StorefrontConfiguration, Store, DeliveryPartner, DeliveryCharges
from paystack.payment import initialise_payment, verify_payment
from storefront.sessionvars import SessionVars
from storefront.sessionvars import get_session_vars, save_session_vars, clear_session_vars


# this is the primary display view to build the
def index(request):

    sv: SessionVars = get_session_vars(request)
    sv.shopping_cart_total_cents = ut.get_cart_total(sv.shopping_cart)

    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': ''
    }

    return render(request, 'storefront/index.html', context)

def add_to_cart(request):
    sv: SessionVars = get_session_vars(request)
    message = ''
    if not sv.isCheckout:
        if request.method == 'POST':
            product = request.POST.get('product')
            price = float(request.POST.get('price'))
            quantity = int(request.POST.get('quantity'))
            store = request.POST.get('store')

            item_exists = False
            for item in sv.shopping_cart:
                if item['product'] == product:
                    item['quantity'] += quantity
                    item['total'] = item['price'] * item['quantity']
                    item_exists = True
                    message = f'Updated quantity of {item["quantity"]} for {item["product"]}.'
                    break

            if not item_exists:
                message = f'Added {product} to cart.'
                sv.shopping_cart.append(
                    {
                        'store': store,
                        'product': product,
                        'price': price,
                        'quantity': quantity,
                        'total': price * quantity}
                )

        sv.shopping_cart_total_cents = ut.get_cart_total(sv.shopping_cart)
        save_session_vars(request, sv)

        context = {
            'cart': ut.get_printable_cart(sv.shopping_cart),
            'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
            'checkout': 'yes' if sv.isCheckout else 'no',
            'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
            'user_name': ut.users[sv.user_id]['name'],
            'address': ut.users[sv.user_id]['address'],
            'store_name': ut.get_store_name(sv.shopping_store),
            'delivery_partner': sv.delivery_partner_name,
            'message': message
        }

        template = loader.get_template('storefront/cart_items.html')
        return HttpResponse(template.render(context, request))

def cart_checkout(request):
    sv: SessionVars = get_session_vars(request)
    sv.isCheckout = True
    sv.delivery_charge_cents = ut.calculate_delivery_charge(sv)
    save_session_vars(request, sv)
    checkout_total = f'R{(sv.shopping_cart_total_cents + sv.delivery_charge_cents)/100:.2f}'

    context = {
        'checkout_total': checkout_total,
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': 'Checkout in progress.'
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def cart_cancel(request):
    sv: SessionVars = clear_session_vars()
    save_session_vars(request, sv)
    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': 'Cart cancelled.'
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def checkout_pay(request):
    sv: SessionVars = get_session_vars(request)
    st_totals: dict[str: ut.StoreTotal] = ut.get_store_totals(sv.shopping_cart)

    sv.delivery_partner_id, sv.delivery_partner_name = ut.get_delivery_partner()
    partner = DeliveryPartner.objects.get(pk=sv.delivery_partner_id)

    # Create a new entry in the DeliveryCharges model
    DeliveryCharges.objects.create(
        order_number=UUIDField(default=random.randint(1000000000, 9999999999)),
        user_Name=ut.users[sv.user_id]['name'],
        distance=ut.users[sv.user_id]['distance'],
        total_amount=sv.shopping_cart_total_cents,
        delivery_charge=sv.delivery_charge_cents,
        delivery_partner=partner,
    )

    success_url = request.build_absolute_uri(reverse('payment-verify'))
    meta_data = {"cancel_action": request.build_absolute_uri(reverse('payment-cancel'))}
#
    p_data = initialise_payment(sv, st_totals, success_url, meta_data)

    if p_data and 'authorization_url' in p_data:
        request.session['p_data'] = p_data
        redirect_url = p_data['authorization_url']
        htmx_response = HttpResponse(status=200)
        htmx_response['HX-Redirect'] = redirect_url
        return htmx_response

    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': 'Payment failed (init).',
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def payment_verify(request):
    reference = request.GET.get('reference', None)
    if reference:
        verify_data = verify_payment(reference=reference)
        if verify_data['status'] == 'success':
            message = 'Payment successful.'
        else:
            message = 'Payment unsuccessful.'
    else:
        message = 'Payment failed (verify).'
    sv:SessionVars = clear_session_vars()
    save_session_vars(request, sv)

    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': message,
    }
    return render(request, 'storefront/index.html', context)


def checkout_cancel(request):
    sv: SessionVars = get_session_vars(request)
    sv.isCheckout = False
    save_session_vars(request, sv)

    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': 'Checkout cancelled.'
    }
    template = loader.get_template('storefront/cart_items.html')
    return HttpResponse(template.render(context, request))

def payment_cancel(request):
    sv:SessionVars = get_session_vars(request)
    sv.isCheckout = False
    save_session_vars(request, sv)

    context = {
        'cart': ut.get_printable_cart(sv.shopping_cart),
        'total': f'R{sv.shopping_cart_total_cents/100:.2f}',
        'checkout': 'yes' if sv.isCheckout else 'no',
        'delivery': f'R{sv.delivery_charge_cents/100:.2f}',
        'user_name': ut.users[sv.user_id]['name'],
        'address': ut.users[sv.user_id]['address'],
        'store_name': ut.get_store_name(sv.shopping_store),
        'delivery_partner': sv.delivery_partner_name,
        'message': 'Payment cancelled.'
    }
    return render(request, 'storefront/index.html', context)
