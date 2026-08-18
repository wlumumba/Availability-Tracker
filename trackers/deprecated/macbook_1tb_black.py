import requests

tracker_name = "macbook_1tb_black"
product_desc = "M4 MacBook Pro 14 inch 1TB - Space Black"

def fetch():
    api_url = "https://www.apple.com/shop/buyability-message?parts.0=G1FF2LL%2FA"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return ("error", "Failed to fetch data from API: ", response)

def process(response):
    print(response) # log response

    if response and 'error' not in response:
        buyability_message = response.get("body", {}).get("content", {}).get("buyabilityMessage", {})
        
        for key in buyability_message.get("order", []):
            if buyability_message.get(key, {}).get("G1FF2LL/A", {}).get("isBuyable", False):
                return (True, f"{product_desc} is available for purchase!")
            else:
                print(f"No {product_desc}")
                return (False, "")
        
    return response

def template(status):
    if True in status:
        product_url = "https://www.apple.com/shop/product/G1FF2LL/A/Refurbished-14-inch-MacBook-Pro-Apple-M4-Pro-Chip-with-14%E2%80%91Core-CPU-and-20%E2%80%91Core-GPU-Space-Black?fnode=0b751f640dab2e317b5194fbd74d34e24f3f502f3e74ada98bdabe20b058504ff219244183915b1500e7e38e27eb97d8ae712ad5c7e0d083930d29ae7585ecad7ecd79b948ba619e7bb30dc0fd724fbe"
        return f"{product_desc} is <a href='{product_url}'>available</a> for purchase!"
    elif 'error' in status:
        return status[1] + status[2]

    
