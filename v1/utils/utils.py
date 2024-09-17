from v1.auth.token_verify import verify
import requests

def get_client_metadata(client_request):
    client_ip = client_request.headers.get('Client-IP', 'Unknown')
    origin_ip = client_request.client.host
    origin = client_request.headers.get('Origin', 'Unknown')
    referer = client_request.headers.get('Referer', 'Unknown')
    source_app = origin if origin != 'Unknown' else referer
    client_ip = client_ip if client_ip else origin_ip
    city, country = get_geolocation(client_ip)
    return client_ip, source_app,city, country

def get_geolocation(ip_address):
    try:
        # Example using ipapi
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        data = response.json()
        city = data.get('city', 'Unknown')
        country = data.get('country_name', 'Unknown')
    except Exception as e:
        city, country = 'Unknown', 'Unknown'
    
    return city, country

async def get_user_id(token: str):
    if token:
        return await verify(token)
    return None   