# shopify_api.py
import requests, time
from .shopify_config import SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION
from dotenv import load_dotenv
from .shopify_auth import ShopifyAuth
import json

auth = ShopifyAuth()

def _shopify_headers():
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

def _build_payload(
    isbn13, title, author, age_group, category, weight, description,
    mrp, image_fp_url, image_other_url_1, image_other_url_2, image_other_url_3,
    last_updated_by, quantity, inventory_type
):
    
    """Build Shopify product payload based on inventory type."""
    base_payload = {
        "title": title,
        "body_html": f"<strong>{description}</strong>",
        "vendor": "MonkeyBarrow",
        "product_type": inventory_type,
        "variants": [
            {
                "sku": isbn13,
                "price": float(mrp),
                "inventory_management": "shopify",
                "inventory_quantity": quantity,
                "weight": float(weight),
            }
        ],
        "images": [
            {"src": image_other_url_1},
            {"src": image_other_url_2},
            {"src": image_other_url_3},
            {"src": image_fp_url}
        ],
        "metafields": [
            {
                "namespace": "custom",
                "key": "age_category",
                "value": age_group,
                "type": "single_line_text_field"
            },
            {
                "namespace": "custom",
                "key": "category",
                "value": category,
                "type": "single_line_text_field"
            }
        ]
    }

    if inventory_type == "BOOK":
        base_payload["tags"] = "mb-book"
        base_payload["metafields"].append({
            "namespace": "custom",
            "key": "author",
            "value": author,
            "type": "single_line_text_field"
        })

    elif inventory_type == "Toy":
        base_payload["tags"] = "mb-toy"
        base_payload["metafields"].append({
            "namespace": "custom",
            "key": "brand",
            "value": author,  # ⚠️ consider renaming to brand if available
            "type": "single_line_text_field"
        })

    elif inventory_type == "PremiumToy":
        base_payload["tags"] = "mb-premiumtoy"
        base_payload["metafields"].append({
            "namespace": "custom",
            "key": "brand",
            "value": author,  # ⚠️ same note as above
            "type": "single_line_text_field"
        })

    else:
        base_payload["tags"] = ""

    return {"product": base_payload}

      
def create_product(
    mb_isbn13, title, author, age_group, category, weight, description,
    mrp, image_fp_url, image_other_url_1, image_other_url_2, image_other_url_3,
    last_updated_by, quantity, inventory_type
):
    
    """Create a product in Shopify with error handling."""
    payload = _build_payload(
        isbn13, title, author, age_group, category, weight, description,
        mrp, image_fp_url, image_other_url_1, image_other_url_2, image_other_url_3,
        last_updated_by, quantity, inventory_type
    )

    try:
        resp = requests.post(
            f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/products.json",
            headers=_shopify_headers(),
            json=payload
        )
        resp.raise_for_status()
        print("📥 Shopify create product:", resp.json())
        return resp.json()
    except requests.RequestException as e:
        print(f"❌ Shopify product creation failed: {e}")
        return {"error": str(e)}

def update_quantity(isbn13: str, added_qty: int):
    """Update product quantity in Shopify with error handling."""
    try:
        resp = requests.get(
            f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/products.json?sku={isbn13}",
            headers=_shopify_headers()
        )
        resp.raise_for_status()
        products = resp.json().get("products", [])
        if not products:
            raise Exception(f"No Shopify product found for ISBN {isbn13}")

        variant = products[0]["variants"][0]
        inventory_item_id = variant["inventory_item_id"]

        inv_resp = requests.get(
            f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/inventory_levels.json?inventory_item_ids={inventory_item_id}",
            headers=_shopify_headers()
        )
        print(f"inv_resp: {inv_resp}")
        inv_resp.raise_for_status()
        inv_levels = inv_resp.json().get("inventory_levels", [])
        if not inv_levels:
            raise Exception(f"No inventory level found for ISBN {isbn13}")

        location_id = inv_levels[0]["location_id"]
        
        # ✅ Safe fallback: treat None as 0
        available_val = inv_levels[0].get("available")
        current_qty = int(available_val) if available_val is not None else 0
        new_qty = current_qty + int(added_qty)
        
        update_payload = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": new_qty
        }
        print(f"Payload: {update_payload}")
        
        upd_resp = requests.post(
            f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/inventory_levels/set.json",
            headers=_shopify_headers(),
            json=update_payload
        )
        upd_resp.raise_for_status()
        print("📥 Shopify update product:", upd_resp.json())
        return upd_resp.json()

    except requests.RequestException as e:
        print(f"❌ Shopify quantity update failed: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ Shopify quantity update logic error: {e}")
        return {"error": str(e)}