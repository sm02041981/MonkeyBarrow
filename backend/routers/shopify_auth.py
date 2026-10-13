#SM:3sep2026
# This program is to fetch shopify access token via shopify auth api

#import modules
import os
import requests
import time
from .shopify_config import SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET, SHOPIFY_STORE

#Shopify auth class defined

class ShopifyAuth:
    def __init__(self):
        self.shop = SHOPIFY_SHOP  # e.g. monkeybarrow.myshopify.com
        self.client_id = SHOPIFY_CLIENT_ID
        self.client_secret = SHOPIFY_CLIENT_SECRET
        self._token = None
        self._expiry = 0

    def _refresh_token(self):
        url = f"https://{self.shop}/admin/oauth/access_token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        resp = requests.post(url, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()

        self._token = token_data["access_token"]
        self._expiry = time.time() + token_data.get("expires_in", 3600)

    def get_token(self):
        if not self._token or time.time() >= self._expiry:
            self._refresh_token()
        return self._token

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.get_token()
        }
