import requests

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
                return (True, "M4 MacBook Pro 14 inch 512GB is available for purchase!")
            else:
                return (False, "")
        
    return response

def template(status):
    if True in status:
        return f"M4 MacBook Pro 14 inch 512GB is available for purchase!"
    elif 'error' in status:
        return status[1] + status[2]

    
