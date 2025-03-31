import requests

from .util import get_headers

def register_account(name: str, bank_id: str, account: str, percentage: float):

    url = "https://api.paystack.co/subaccount"
    payload = {
        "business_name": name,
        "settlement_bank": bank_id,
        "account_number": account,
        "percentage_charge": percentage,
    }
    headers = get_headers()

    try:
        response = requests.post(url, json=payload, headers=headers)
        sub_account_code = response.json()['data']['subaccount_code']
        return sub_account_code
    except requests.exceptions.RequestException as e:
        print(e)

def update_account(subaccount_code: str, name: str, description: str ):
    url = f"https://api.paystack.co/subaccount:{subaccount_code}"

    payload = {
        "business_name": name,
        "business_description": description
    }

    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        returned_data = response.json()

    except requests.exceptions.RequestException as e:
        print(e)
