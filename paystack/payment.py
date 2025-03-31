
import requests

from paystack.util import get_headers

def initialise_payment(
        customer_email: str,
        total_amount: int,
        store_subaccount: str,
        store_amount: int,
        delivery_subaccount: str,
        delivery_amount: int,
        callback_url: str,
        metadata: dict = None
):
    url = "https://api.paystack.co/transaction/initialize"

    payload = {
        "email": customer_email,
        "amount": str(total_amount),
        "currency": "ZAR",
        "split": {
            "type": "flat",
            "bearer_type": "account",
            "subaccounts": [
                {
                    "subaccount": store_subaccount,
                    "share": str(store_amount)
                },
                {
                    "subaccount": delivery_subaccount,
                    "share": str(delivery_amount)
                },
            ]
        },
        # "callback_url": callback_url,
        # "metadata": metadata if metadata else {}
    }
    print(f'{payload=}')
    headers = get_headers()
    try:
        print('I am doing this now')
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        returned_data = response.json()

        if returned_data['status'] == 'true':
            return returned_data['data']
        else:
            return {}
    except requests.exceptions.RequestException as e:
        print(f"exception thrown==>{e}")
        return None

def verify_payment(reference: str):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        returned_data = response.json()
        return returned_data['data']
    except requests.exceptions.RequestException as e:
        print(f"exception thrown==>{e}")
        return None


if __name__ == '__main__':
   p = initialise_payment(
        customer_email='otherOne@gmail.com',
        total_amount=10000,
        store_subaccount='ACCT_fb7kx36h4srk1jw',
        store_amount=90000,
        delivery_subaccount='ACCT_zencm9w32ua1agy',
        delivery_amount=500,
        callback_url="https://b996-41-193-87-145.ngrok-free.app/payment-verify/"
    )
   print(f'{p=}')

