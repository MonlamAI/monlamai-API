from v1.auth.token_verify import verify
import requests
import os
from dotenv import load_dotenv


load_dotenv(override=True)

def get_first_ip(ip_string):
    # Split the string by commas and strip any whitespace
    ip_list = [ip.strip() for ip in ip_string.split(',')]
    # Return the first IP if the list is not empty, otherwise return an empty string
    return ip_list[0] if ip_list else ''

def get_client_metadata(client_request):
    client_ip = client_request.headers.get('Client-IP', 'Unknown')
    origin_ip = client_request.client.host
    origin = client_request.headers.get('Origin', 'Unknown')
    referer = client_request.headers.get('Referer', 'Unknown')
   
    source_app = origin if origin != 'Unknown' else referer
    client_ip = client_ip if client_ip else origin_ip
    city, country = get_geolocation(get_first_ip(client_ip))
    return client_ip, source_app,city, country


import requests

def get_geolocation(ip_address):
    api_key = os.getenv('GEOAPIFY_API_KEY')
    url = f"https://api.geoapify.com/v1/ipinfo?ip={ip_address}&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Extract city and country information, defaulting to "Unknown" if not available
        city = data.get('city', {}).get('name') or "Unknown"
        country = data.get('country', {}).get('name') or "Unknown"
        
        return city, country
 
    except requests.exceptions.RequestException as e:
        return "Unknown", "Unknown"

async def get_user_id(token: str):
    if token:
        user = await verify(token)
        if user:
            user_id = user.id  # Access id using dot notation
            return user_id
    return None
