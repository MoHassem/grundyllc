
import requests
import storefront.utilities as ut

from paystack.util import get_headers
from storefront.sessionvars import SessionVars

INIT_TRANSACTION = 'https://api.paystack.co/transaction/initialize'


def get_split_list(st: dict[str: ut.StoreTotal]):
    sub_accounts = []
    for store in st.values():
        sub_accounts.append(
            {
                "subaccount": store.sub_account,
                "share": store.cart_partner_share
            }
        )
    return sub_accounts

def initialise_payment(sv: SessionVars, st: dict[str: ut.StoreTotal], success_url: str, metadata: dict = None,):
    url = INIT_TRANSACTION

    payload = {
        "email": ut.get_user_email(sv),
        "amount": sv.shopping_cart_total_cents + sv.delivery_charge_cents,
        "currency": "ZAR",
        "split": {
            "type": "flat",
            "bearer_type": "all",
            "subaccounts": get_split_list(st)
        },
        "callback_url": success_url,
        "metadata": metadata if metadata else {}
    }
    headers = get_headers()
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        returned_data = response.json()
        if returned_data['status'] == True:
            return returned_data['data']
        else:
            print(f'Payment failed: {returned_data}')
            return {}
    except requests.exceptions.RequestException as e:
        print(f'Payment failed: {e}')
        return None

def verify_payment(reference: str):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        returned_data = response.json()
        response.raise_for_status()
        return returned_data['data']
    except requests.exceptions.RequestException as e:
        return None
