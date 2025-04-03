
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
                    "share": store_amount
                },
                {
                    "subaccount": delivery_subaccount,
                    "share": delivery_amount
                },
            ]
        },
        "callback_url": callback_url,
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
            return {}
    except requests.exceptions.RequestException as e:
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
