import os
from datetime import datetime
from session_manager import get_session
from util import compute_hash, read_last_hash, write_hash
import time

tracker_name = "tesla_model_three"
product_desc = "Tesla Model 3"
hash_file_path = f"{os.getenv('HASH_DIR', 'hashes')}/{tracker_name}.txt"

def fetch():
    api_url = "https://www.tesla.com/cua-api/drive/get-all-locations?locale=en_US&country=US&zipcode=77007&lat=29.7738&lon=-95.406"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.tesla.com/drive",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "x-account-locale": "en_us"
    }
    
    time.sleep(5)
    session = get_session()
    response = session.get(api_url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()
    else:
        return ("error", f"Failed to fetch data from API (Status {response.status_code}): ", f"Body: {response.text}")

def process(response):
    print(str(response)[:1000] + ' truncated...')  # log response

    if response and 'error' not in response:
        # Create a dictionary to store availability by location
        availability_by_location = {}

        # Get Model 3 data and store details
        model_3_data = response.get('timeAndDatesExtendedHours', {}).get('Model3', {})
        
        # Get trtIdsWithSlots
        trt_ids_data = model_3_data.get('trtIdsWithSlots', [])
        
        # Extract all dates from trtIdsWithSlots
        date_keys = [date for trt_id in trt_ids_data for date in model_3_data.get(str(trt_id), {}).keys()]

        # Check if any dates fall on Friday or Saturday
        has_weekend_slots = any(
            datetime.strptime(date, "%Y-%m-%d").weekday() in [3, 4, 5]  # 3 is Thursday, 4 is Friday, 5 is Saturday
            for date in date_keys
        )

        # For each trtId with slots, get the store details and corresponding Model 3 data
        for trt_id in trt_ids_data:
            store_details = response.get('storeDetails', {}).get(str(trt_id), {})
            if store_details:
                address, trt_data = store_details.get('streetAddress', ''), model_3_data.get(str(trt_id), {})
                if trt_data:
                    availability_by_location[address] = trt_data
        
        # Compute hash of the availability data
        if trt_ids_data and has_weekend_slots and compute_hash(date_keys) != read_last_hash(hash_file_path):
            write_hash(hash_file_path, compute_hash(date_keys))
            print(f"Availability {product_desc} found on {set(date_keys)}: ", availability_by_location)
            return availability_by_location
        else:
            print(f"No changes in {product_desc} availability")
            return ("null", "No changes in availability")
    else:
        return response

def template(availability_by_location):
    if 'error' in availability_by_location:
        return availability_by_location[1] + availability_by_location[2]
    elif 'null' in availability_by_location:
        return ""
    else:
        email_body = [f"{product_desc} Available on <a href='https://www.tesla.com/drive'>Tesla</a>"]
        
        for address, dates_data in availability_by_location.items():
            email_body.append(f"{address}:")
            for date, times in dates_data.items():
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                # Format date like "Wednesday, July 25 2025"
                formatted_date = date_obj.strftime("%A, %B %d %Y")
                
                # Add each time slot to the email body
                for time, time_data in times.items():
                    formatted_time = time_data.get('timeFormatted', time)
                    email_body.append(f"&nbsp;&nbsp;&nbsp;&nbsp;- {formatted_date} at {formatted_time}")
        
        return "<br>".join(email_body) 