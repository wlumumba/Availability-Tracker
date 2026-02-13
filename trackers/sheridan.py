import os
from datetime import datetime
from session_manager import get_session
from util import compute_hash, read_last_hash, write_hash
import time

tracker_name = "sheridan"
product_desc = "Sheridan Parking"
hash_file_path = f"{os.getenv('HASH_DIR', 'hashes')}/{tracker_name}.txt"

def fetch():
    api_url = "https://i-subscriptions.thx.lazparking.com/subscription/shop/locationRates?startDate=2026-02-13T00:00:00.000Z&distance=32&locationNo=600174&promoCode=%20"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "x-api-key": os.getenv("sheridan_api_key")
    }
    session = get_session()
    response = session.get(api_url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()
    else:
        return ("error", f"Failed to fetch data from API (Status {response.status_code}): ", f"Body: {response.text}")

def process(response):
    print(str(response)[:1000] + ' truncated...')

    if response and 'error' not in str(response):
        products = response.get('products') or {}
        
        current_hash = compute_hash(str(products))
        if current_hash != read_last_hash(hash_file_path):
            write_hash(hash_file_path, current_hash)
            print(f"Changes detected in {product_desc}: ", products)
            return products
        else:
            print(f"No changes in {product_desc}")
            return ("null", "No changes")
    else:
        return response

def template(products):
    if 'error' in str(products):
        return products[1] + products[2]
    elif 'null' in products:
        return ""
    elif not products:
        return f"{product_desc}: No products available"
    else:
        email_body = [f"<b>{product_desc}</b>"]
        for p in products:
            email_body.append(f"<br><b>{p.get('prdctName')}</b>")
            for rp in p.get('ratePlans', []):
                email_body.append(f"&nbsp;&nbsp;- {rp.get('description')}: ${rp.get('price')}")
        return "<br>".join(email_body)
