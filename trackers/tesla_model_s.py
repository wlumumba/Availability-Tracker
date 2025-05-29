import os
from datetime import datetime
from session_manager import get_session
from util import compute_hash, read_last_hash, write_hash

tracker_name = "tesla_model_s"
product_desc = "Tesla Model S"
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
        "x-account-locale": "en_us",
        "cookie": "_abck=8E40C781094E8F542FC867945C9F5379~-1~YAAQ0iXAF/6OBeGWAQAAODivGg0rmFWHOmb7Keb9Jo3Zls6qnp2q2yv/oc1Ea/iq1A0X3ucmT4MY+cpuWBxUZDIK8XC7GNFHbnEUiVLNVSo9w147ohft3dNV+gn2ylEgAt5qEjqjhbDu/qZEWSUY9Gs8t3ODOm+2GyUZpCZx61ln1VmYyyFAqWaepFSCV0sbMliWRG+5Zj676CfR2pjLAakGqpIPlX/MxCzGY9yi/2nGYE3dY63VaDEcqOIIq0HtHMYjsuPLh0vU1gKP45CvD7pRUxthzLnTY4P5NPURudg+Qi2zy2t6z5siGMJA+8B9++aPO86OGDWcoF5a3cb3dkNv1pVSTSZow72xrStG2B+CVwmr/FUx7EXxXR4OjVbk9Xew+OqhzPrFfurUVaIdRZ5zEjfAKlFFZvohMxkVhs0spdI2SEm5i1DvO3uygu4++Cts~-1~-1~-1; ak_bmsc=DD559CAFF991443C571F8E2559EAE27F~000000000000000000000000000000~YAAQ0iXAF50tBuGWAQAAWLC3GhvXSIG/du4GpacIS6c92ecEzi8hiThi02kLhBcP5sau18z5/zPACcRS51N9TeJRmhLl+6MkuSFNEHSVCHsj6KUjjH+Q1/USyUk/SiXe5mTbDi1yJ0PNPKqHrysRlCywf2NFMOy5jz3jmPH4kGhMjgya6LCSVMrKPcG+DcvmnWU0W8G0kTIFDt1MHGu9n5FGrrEmpS/ACGx7jXRq4k37HzJcDgDdeJuWc906EJ0dpf42heKLtFfK04xRkAYmXuSsFxm48QSglD/PS3BCTujSS+DazHXVfa9fL5unCfOo77GBmNwTEhQ5RMWJWsyAL2sX9wa99hDUIQ==; bm_s=YAAQ0iXAF7S0BuGWAQAAWiS/GgMrt7FDeQaarK3ppsI9NcWGDEB86bn92ZkWWcvba3c9hsaTZ7lNjHdJun2rAP5NdMR/JZeCoJnga7P8zUFqV+kcInWmazTIdSLNdlsLax76YTdYtRQZyx2wl6A4MwMTDfK8n5VCd65fznsJ0XVRC2o24/IBmvwP9BFKj0E33Thd1GatikoZ/4eclWuBQOrL7YVoTMlQw1EjFjHijwmyBKqQKiK3Uvz7oYQPNKizFNuTK4yE4hdvGnWKRH0QexnBZGs5C/QCWft751JnnvLg/oyw32gteLm2xLTkrrMIZM+PlOJW9/PW+KFSemOnm9vMKW2ukBfsTnfs/n8VcDTNY4yO1GPmg0+5kxW/kkdgKUeuC3Ncr3O1Am8rdfQrcrgDMQXphKgE5h79cDzrRZIzcoLd5bxFIofHfx4BvfwQw03UVoM/Uohk+PEhgPSwe6+7wObuUsDPjjgCi+3Q/pH/AQ1YcktyBV5k8tGn4Qb1Oe6raBoAmFR2WGSUOQzbeIlOs8oCPz76eGqNgF0XKHIgSA==; bm_ss=ab8e18ef4e; bm_sv=E218FE772A51684F2B4E622A19491BDC~YAAQ0iXAF7W0BuGWAQAAWiS/GhtFnRNhvzSKsDM8cfXbaxD6IkDfLHYpUvn0+r3/cj3PvQ4cUzJFnRHpd22qUMZi6wcAksajzTasaQsZyIbbWZ3ZwEJ6eiSXo9Gt51g8dcWjMXQWzR/3/Q4iamE6v+Gjc8VtSiUAvRd2zJfLQp6ltVEl/RQ/lKnj5UguABBeMyEYN9GUEFJ9Nv407XQHEkwargVS4xglkDxenq+b2x2iSUHHABD8M7djvcFJOLg=~1; bm_sz=222D76846340C85055669A8F7A579A64~YAAQ0iXAFwCPBeGWAQAAODivGhtpgc2zjwE/kDlhy5+1nWkv6A7cxuosNfeL22AjyTmOOBM05WNVmjBaZf6yAonjuPgoQlIp6GYNcjbdBverhP3E2LYgOjH7dQauXBYHCyaritWliwVr651VJeRVQVuUOVQlGZbX51v9bdxAVbhCGsCnuQ4q1dVdTG0oEpyGcTbCifV+JRdEALqguJGTGPAeENZHg48Uy7g2jvO9D0DtJ5A8vKqGuVhACuUwlk19KsfpE1D17d9TcAyeA9oPgiK8YudPPtpCIdEXUsRpB4UnuB+v0Wthxa6OlPMKAyMjMMZLbRDQ3/g2r4sgbvIoZ5y4/JJesEckp9JVtA==~4470832~3289154; cua_sess=37b1eb3b62027f4ea0fc3036165298fc; akavpau_zezxapz5yf=1748500723~id=671e504fd6f6bc714ab9d34f36482726"
    }
    
    session = get_session()
    response = session.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return ("error", f"Failed to fetch data from API (Status {response.status_code}): ", response.text)

def process(response):
    print(str(response)[:1000] + ' truncated...')  # log response

    if response and 'error' not in response:
        # Create a dictionary to store availability by location
        availability_by_location = {}

        # Get Model S data and store details
        model_s_data = response.get('timeAndDatesExtendedHours', {}).get('ModelS', {})
        
        # Get trtIdsWithSlots
        trt_ids_data = model_s_data.get('trtIdsWithSlots', [])
        
        # Extract all dates from trtIdsWithSlots
        date_keys = [date for trt_id in trt_ids_data for date in model_s_data.get(str(trt_id), {}).keys()]

        # For each trtId with slots, get the store details and corresponding Model S data
        for trt_id in trt_ids_data:
            store_details = response.get('storeDetails', {}).get(str(trt_id), {})
            if store_details:
                address, trt_data = store_details.get('streetAddress', ''), model_s_data.get(str(trt_id), {})
                if trt_data:
                    availability_by_location[address] = trt_data
        
        # Compute hash of the availability data
        if trt_ids_data and compute_hash(date_keys) != read_last_hash(hash_file_path):
            write_hash(hash_file_path, compute_hash(date_keys))
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
                # Format date as "Wednesday, July 25 2025"
                formatted_date = date_obj.strftime("%A, %B %d %Y")
                
                # Format each time slot
                for time, time_data in times.items():
                    formatted_time = time_data.get('timeFormatted', time)
                    email_body.append(f"&nbsp;&nbsp;&nbsp;&nbsp;- {formatted_date} at {formatted_time}")
        
        return "<br>".join(email_body) 