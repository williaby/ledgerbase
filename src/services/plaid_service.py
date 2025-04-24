import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.plaid")

PLAID_CLIENT_ID: str | None = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET: str | None = os.getenv("PLAID_SECRET")
PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")

PLAID_BASE_URLS: dict[str, str] = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}

BASE_URL: str | None = PLAID_BASE_URLS.get(PLAID_ENV.lower())
HEADERS: dict[str, str] = {"Content-Type": "application/json"}
DEFAULT_TIMEOUT: float = 10.0


def plaid_request(endpoint: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the Plaid API.

    Args:
    ----
        endpoint (str): The API endpoint to call.
        payload (Dict[str, Any]): The payload to send in the request.

    Returns:
    -------
        Optional[Dict[str, Any]]: The JSON response from the API,
        or None if the request fails. # noqa: E501

    """
    url = f"{BASE_URL}{endpoint}"
    payload.update(
        {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
        },
    )
    response: requests.Response | None = None
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


def create_link_token(user_id: str = "user-unique-id") -> dict[str, Any] | None:
    """Create a link token for the Plaid API.

    Args:
    ----
        user_id (str): A unique identifier for the user. Defaults to "user-unique-id".

    Returns:
    -------
        Optional[Dict[str, Any]]: The response containing the link token,
        or None if the request fails. # noqa: E501

    """
    payload = {
        "user": {"client_user_id": user_id},
        "client_name": "LedgerBase",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
    }
    return plaid_request("/link/token/create", payload)


def get_accounts(access_token: str) -> dict[str, Any] | None:
    """Retrieve account information from the Plaid API.

    Args:
    ----
        access_token (str): The access token for the user's account.

    Returns:
    -------
        Optional[Dict[str, Any]]: The response containing account information,
        or None if the request fails.

    """
    payload = {"access_token": access_token}
    return plaid_request("/accounts/get", payload)


def get_transactions(
    access_token: str,
    start_date: str,
    end_date: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Retrieve transaction data from the Plaid API.

    Args:
    ----
        access_token (str): The access token for the user's account.
        start_date (str): The start date for the transaction query (YYYY-MM-DD).
        end_date (str): The end date for the transaction query (YYYY-MM-DD).
        options (Optional[Dict[str, Any]]): Additional options for the query.
        Defaults to None. # noqa: E501

    Returns:
    -------
        Optional[Dict[str, Any]]: The response containing transaction data, or
         None if the request fails.

    """
    payload: dict[str, Any] = {
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date,
    }
    if options:
        payload["options"] = options
    return plaid_request("/transactions/get", payload)


def sync_transactions(
    access_token: str,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """Synchronize transactions using the Plaid API.

    Args:
    ----
        access_token (str): The access token for the user's account.
        cursor (Optional[str]): The cursor for incremental sync. Defaults to None.

    Returns:
    -------
        Optional[Dict[str, Any]]: The response containing synchronized transactions,
        or None if the request fails.

    """
    payload: dict[str, Any] = {
        "access_token": access_token,
    }
    if cursor is not None:
        payload["cursor"] = cursor
    return plaid_request(
        "/transactions/sync",
        payload,
    )
