import requests

BASE_URL = "http://127.0.0.1:8000"


class APIClient:

  def __init__(self, token: str = None):
    self.token = token

  def _headers(self):
    headers = {}
    if self.token:
      headers["Authorization"] = f"Bearer {self.token}"
    return headers

  # --- AUTH ---
  def create_user(self, payload: dict):
    return requests.post(f"{BASE_URL}/auth/create-user", json=payload)

  def login(self, username, password):
    return requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": username, "password": password},
    )

  # --- USERS ---
  def get_me(self):
    return requests.get(f"{BASE_URL}/users/me", headers=self._headers())

  def update_me(self, payload: dict):
    return requests.put(
        f"{BASE_URL}/users/me", json=payload, headers=self._headers()
    )

  def update_password(self, payload: dict):
    return requests.put(
        f"{BASE_URL}/users/me/password", json=payload, headers=self._headers()
    )

  # --- ACCOUNTS ---
  def get_accounts(self):
    return requests.get(f"{BASE_URL}/account/", headers=self._headers())

  def get_account_by_id(self, acc_id: int):
    return requests.get(f"{BASE_URL}/account/{acc_id}", headers=self._headers())

  def create_account(self, payload: dict):
    return requests.post(
        f"{BASE_URL}/account/", json=payload, headers=self._headers()
    )

  def update_account(self, acc_id: int, payload: dict):
    return requests.put(
        f"{BASE_URL}/account/{acc_id}", json=payload, headers=self._headers()
    )

  def delete_account(self, acc_id: int):
    return requests.delete(
        f"{BASE_URL}/account/{acc_id}", headers=self._headers()
    )

  # --- CATEGORIES ---
  def get_categories(self):
    return requests.get(f"{BASE_URL}/category/", headers=self._headers())

  def get_category_by_id(self, cat_id: int):
    return requests.get(
        f"{BASE_URL}/category/{cat_id}", headers=self._headers()
    )

  def create_category(self, payload: dict):
    return requests.post(
        f"{BASE_URL}/category/", json=payload, headers=self._headers()
    )

  def update_category(self, cat_id: int, payload: dict):
    return requests.put(
        f"{BASE_URL}/category/{cat_id}", json=payload, headers=self._headers()
    )

  def delete_category(self, cat_id: int):
    return requests.delete(
        f"{BASE_URL}/category/{cat_id}", headers=self._headers()
    )

  # --- TRANSACTIONS ---
  def get_transactions(self):
    return requests.get(f"{BASE_URL}/transactions/", headers=self._headers())

  def get_transaction_by_id(self, tx_id: int):
    return requests.get(
        f"{BASE_URL}/transactions/{tx_id}", headers=self._headers()
    )

  def create_transaction(self, payload: dict):
    return requests.post(
        f"{BASE_URL}/transactions/", json=payload, headers=self._headers()
    )

  def update_transaction(self, tx_id: int, payload: dict):
    return requests.put(
        f"{BASE_URL}/transactions/{tx_id}",
        json=payload,
        headers=self._headers(),
    )

  def delete_transaction(self, tx_id: int):
    return requests.delete(
        f"{BASE_URL}/transactions/{tx_id}", headers=self._headers()
    )

  def import_csv(self, account_id: int, file_bytes, filename: str):
    files = {"file": (filename, file_bytes, "text/csv")}
    data = {"account_id": account_id}
    return requests.post(
        f"{BASE_URL}/transactions/import-csv",
        data=data,
        files=files,
        headers=self._headers(),
    )

  def classify_pending(self):
    return requests.post(
        f"{BASE_URL}/transactions/classify-pending", headers=self._headers()
    )