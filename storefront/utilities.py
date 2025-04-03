
import random

from config.models import StorefrontConfiguration, Store, DeliveryPartner
from storefront.sessionvars import SessionVars

# in a production app the user data will be stored in the admin system provided by Django
users = {
    '1': {'name': 'Mohammed Hassem', 'address': '4 6th Street, Orange Grove, 2192', 'email': 'mhassem786@gmail.com',
          'cell': '083-555-5555', 'distance': 4.0},
}

# format the total for display on the glass
def get_cart_total(cart):
    total = 0.00
    if cart:
        total = sum(item['price'] for item in cart)
    return total

# create a cart that can be displayed on the glass
def get_printable_cart(cart):
    if not cart:
        return []
    cp_cart = []
    for item in cart:
        cp_cart.append(
            {
                'product': item['product'],
                'price': item['price'],
                'quantity': item['quantity'],
            }
        )
    for item in cp_cart:
        item['price'] = f'R{item['price']:.2f}'
    return cp_cart

# get the store name from the Store repo
def get_store_name(store_id):
    if store_id == '0':
        return ''
    store = Store.objects.filter(pk=int(store_id)).first()
    if not store:
        return ''
    else:
        return store.business_name

# calculate the delivery charge
def calculate_delivery_charge(sv: SessionVars):
    config = StorefrontConfiguration.objects.get(pk=1)
    distance = users[sv.user_id]['distance']
    if distance > config.threshold_distance_km:
        return (
                (float(config.threshold_distance_km) * distance)
                + ((distance - float(config.threshold_distance_km))
                * float(config.additional_charge_per_km + config.delivery_charge_per_km))
        )
    return distance * float(config.delivery_charge_per_km)

# allocate a delivery partner randomly (will have to change in prod)
def get_delivery_partner():
    partner_ids = DeliveryPartner.objects.values_list('id', flat=True)
    p_id = random.choice(partner_ids)
    partner = DeliveryPartner.objects.get(pk=p_id)
    return partner.id, partner.name

# get delivery partner account code
def get_delivery_partner_account_code(p_id):
    partner = DeliveryPartner.objects.get(pk=p_id)
    return partner.subaccount_code
