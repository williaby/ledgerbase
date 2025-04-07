import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.plaid")

PLAID_CLIENT_ID: Optional[str] = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET: Optional[str] = os.getenv("PLAID_SECRET")
PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")

PLAID_BASE_URLS: Dict[str, str] = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}

BASE_URL: Optional[str] = PLAID_BASE_URLS.get(PLAID_ENV.lower())
HEADERS: Dict[str, str] = {"Content-Type": "application/json"}
DEFAULT_TIMEOUT: float = 10.0


def plaid_request(endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{endpoint}"
    payload.update(
        {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
        }
    )
    response: Optional[requests.Response] = None
    try:
        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Plaid API request failed: {e}")
        if response is not None:
            print("Response:", response.text)
        return None


def create_link_token(user_id: str = "user-unique-id") -> Optional[Dict[str, Any]]:
    payload = {
        "user": {"client_user_id": user_id},
        "client_name": "LedgerBase",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
    }
    return plaid_request("/link/token/create", payload)


def get_accounts(access_token: str) -> Optional[Dict[str, Any]]:
    payload = {"access_token": access_token}
    return plaid_request("/accounts/get", payload)


def get_transactions(
    access_token: str,
    start_date: str,
    end_date: str,
    options: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date,
    }
    if options:
        payload["options"] = options
    return plaid_request("/transactions/get", payload)


def sync_transactions(
    access_token: str,
    cursor: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {"access_token": access_token}
    if cursor is not None:
        payload["cursor"] = cursor
    return plaid_request("/transactions/sync", payload)
