
import random

from attrs import define, field

from config.models import StorefrontConfiguration, Store, DeliveryPartner
from storefront.sessionvars import SessionVars

@define
class StoreTotal:
    name: str = field(init=True, default='0')
    sub_account: str = field(init=True, default='0')
    cart_total: int = field(init=True, default=0)
    cart_grundy_share: int = field(init=True, default=0)
    cart_partner_share: int = field(init=True, default=0)



# in a production app the user data will be stored in the admin system provided by Django
users = {
    '1': {'name': 'Mohammed Hassem', 'address': '4 6th Street, Orange Grove, 2192', 'email': 'mhassem786@gmail.com',
          'cell': '083-555-5555', 'distance': 4.0},
}


# format the total for display on the glass
def get_cart_total(cart):
    total = 0
    if cart:
        total = sum(item['total'] for item in cart)
    return int(total)

# create a cart that can be displayed on the glass
def get_printable_cart(cart):
    if not cart:
        return []
    cp_cart = []
    for item in cart:
        cp_cart.append(
            {
                'product': item['product'],
                'quantity': item['quantity'],
                'price': f'{item['price']/100:.2f}',
                'total': f'{item['total']/100:.2f}',
            }
        )
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
        return int(
            (
                (float(config.threshold_distance_km * config.delivery_charge_per_km)
                 + (
                         (distance - float(config.threshold_distance_km))
                         * float(config.additional_charge_per_km + config.delivery_charge_per_km))
                 )
            ) * 100
        )
    return int(distance * float(config.delivery_charge_per_km) * 100)

# allocate a delivery partner randomly (will have to change in prod)
def get_delivery_partner():
    partner_ids = DeliveryPartner.objects.values_list('id', flat=True)
    p_id = random.choice(partner_ids)
    partner = DeliveryPartner.objects.get(pk=p_id)
    return partner.id, partner.name

# get store totals for the basket
def get_store_totals(cart):

    store_dict: dict[str, StoreTotal] = {}

    def get_store_total_entry(store_name: str):
        st = StoreTotal()
        store = Store.objects.filter(business_name=store_name).first()
        if store:
            st.name = store.business_name
            st.sub_account = store.subaccount_code
            st.cart_total = 0
            st.cart_grundy_share = 0
            st.cart_partner_share = 0
        return st

    for item in cart:
        if item['store'] not in store_dict:
            store_dict[item['store']] = get_store_total_entry(item['store'])
        store_dict[item['store']].cart_total += int(item['price'] * item['quantity'])


    sf_config = StorefrontConfiguration.objects.get(pk=1)
    cart_charge = float(sf_config.basket_charge/100)
    for store_name, st_totals in store_dict.items():
        st_totals.cart_grundy_share = int(st_totals.cart_total * cart_charge)
        st_totals.cart_partner_share = st_totals.cart_total - st_totals.cart_grundy_share
    return store_dict

def get_user_email(sv: SessionVars):
    return users[sv.user_id]['email']
