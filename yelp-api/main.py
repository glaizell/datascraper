import os
import json
import pandas as pd
import requests
import time
from dotenv import load_dotenv

OFFSET_FILE = "offset_data.json"
RESULTS_FILE = "pest.csv"

load_dotenv()
API_KEY = os.getenv("API_KEY")

HEADERS = {'Authorization': f'Bearer {API_KEY}'}

SEARCH_URL = 'https://api.yelp.com/v3/businesses/search'
DETAILS_URL = 'https://api.yelp.com/v3/businesses/'

search_params = {
    "term": "Pest Control",
    "location": "Miami, Florida",
    "limit": 50
}

#========================================================================================================
def save_offset(offset):
    with open(OFFSET_FILE, "w", encoding='utf-8') as file:
        json.dump({"offset": offset}, file)

#========================================================================================================

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r", encoding='utf-8') as file:
            data = json.load(file)
            return data.get("offset", 0)
    return 0

#========================================================================================================

def save_to_csv(businesses, file_path):
    df = pd.DataFrame(businesses)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        df.to_csv(file_path, index=False)

#========================================================================================================

def fetch_all_businesses(search_url, details_url, headers, params):
    offset = load_offset()
    max_results = 240

    while True:
        params['offset'] = offset
        response = requests.get(search_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error fetching businesses: {response.status_code}, {response.json()}")
            break

        data = response.json()
        businesses = data.get("businesses", [])

        if not businesses:
            break

        businesses_no_url = []

        for business in businesses:
            business_id = business.get("id")
            details_response = requests.get(f"{details_url}{business_id}", headers=headers)

            if details_response.status_code == 200:
                details_data = details_response.json()
                website_url = details_data.get("attributes", {}).get("business_url")

                if website_url == "Not Found" or website_url is None:
                    name = details_data.get("name", "N/A")
                    address = ", ".join(details_data.get("location", {}).get("display_address", []))
                    phone = details_data.get("phone", "N/A")
                    categories = [cat.get("title", "N/A") for cat in details_data.get("categories", [])]


                    business_info = {
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                        "Categories": ", ".join(categories),
                        "Website URL": website_url or "N/A"
                    }
                    businesses_no_url.append(business_info)


        if businesses_no_url:
            save_to_csv(businesses_no_url, RESULTS_FILE)


        offset += len(businesses)
        save_offset(offset)


        print(f"Fetched {len(businesses)} businesses, sleeping for 2 seconds...")
        time.sleep(2)


        if offset >= max_results:
            break

    return offset

#========================================================================================================

if __name__ == "__main__":
    print("Starting Yelp data fetch...")
    fetch_all_businesses(SEARCH_URL, DETAILS_URL, HEADERS, search_params)
    print("Data fetching completed.")
    print(f"Results saved to {RESULTS_FILE}.")
