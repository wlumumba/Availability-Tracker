import requests
from datetime import datetime, timedelta
from util import compute_hash, read_last_hash, write_hash

tracker_name = "fifteenth_street"
hash_file_path = f"hashes/{tracker_name}.txt"

def fetch():
    api_url = "https://doorway-api.knockrentals.com/v1/property/2012477/units"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()['units_data']['units']
    else:
        return ("error", "Failed to fetch data from API: ", response)

def process(response, area=724, days_ahead=30, end_date="2025-12-31"):
    print(response) # log response

    today = datetime.today()
    future_date = today + timedelta(days=days_ahead)
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    if response and 'error' not in response:
        filtered_units = []
        for unit in response:
            available_on = datetime.strptime(unit['availableOn'], "%Y-%m-%d")
            unit_name_as_int = int(unit['name']) if unit['name'].isdigit() else 0
            if (unit['area'] == area and 
                future_date <= available_on < end_date and
                unit_name_as_int > 299):
                filtered_units.append(unit)
        
        # check hash
        if filtered_units and (read_last_hash(hash_file_path) != compute_hash(filtered_units)):
            write_hash(hash_file_path, compute_hash(filtered_units))
            return filtered_units
        else:
            print("No filtered units available.")
            return ("null", "No filtered units available.")
    else:
        return response

def template(filtered_units):
    if 'error' in filtered_units:
        return filtered_units[1] + filtered_units[2]
    elif 'null' in filtered_units:
        return ""
    else:
        return "<br>".join([f"Name: {unit['name']}, Price: {unit['price']}, Available On: {unit['availableOn']}" for unit in filtered_units])