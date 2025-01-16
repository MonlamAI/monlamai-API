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
    try:
        # Extract client IP from headers, default to 'Unknown'
        client_ip = client_request.headers.get('Client-IP', 'Unknown')
        origin_ip = client_request.client.host  # Fallback to request's origin IP
        origin = client_request.headers.get('Origin', 'Unknown')
        referer = client_request.headers.get('Referer', 'Unknown')
        
        # Determine source app based on Origin or Referer
        source_app = origin if origin != 'Unknown' else referer
        
        # Use origin IP if no client IP is available
        client_ip = client_ip if client_ip != 'Unknown' else origin_ip
        
        # Handle IP-related errors gracefully
        if not client_ip or client_ip == 'Unknown':
            raise ValueError("Invalid client IP detected")
        
        # Attempt to get geolocation info
        try:
            city, country = get_geolocation(get_first_ip(client_ip))
        except Exception as geo_ex:
            # Log the geolocation error and set defaults
            print(f"Geolocation error: {geo_ex}")
            city, country = "", ""
        
    except Exception as e:
        # General error handling, log and provide safe defaults
        print(f"Error in get_client_metadata: {e}")
        client_ip, source_app, city, country = "Unknown", "Unknown", "", ""
    
    # Return all metadata
    return client_ip, source_app, city, country

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

