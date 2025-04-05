import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.plaid")

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

PLAID_BASE_URLS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com"
}

BASE_URL = PLAID_BASE_URLS.get(PLAID_ENV.lower())
HEADERS = {
    "Content-Type": "application/json"
}


def plaid_request(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    payload.update({
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET
    })
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Plaid API request failed: {e}")
        if response is not None:
            print("Response:", response.text)
        return None


def create_link_token(user_id: str = "user-unique-id"):
    payload = {
        "user": {
            "client_user_id": user_id
        },
        "client_name": "LedgerBase",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en"
    }
    return plaid_request("/link/token/create", payload)


def get_accounts(access_token: str):
    payload = {
        "access_token": access_token
    }
    return plaid_request("/accounts/get", payload)


def get_transactions(access_token: str, start_date: str, end_date: str, options: dict = None):
    payload = {
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date
    }
    if options:
        payload["options"] = options
    return plaid_request("/transactions/get", payload)


def sync_transactions(access_token: str, cursor: str = None):
    payload = {
        "access_token": access_token
    }
    if cursor:
        payload["cursor"] = cursor
    return plaid_request("/transactions/sync", payload)
