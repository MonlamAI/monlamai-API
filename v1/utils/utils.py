from v1.auth.token_verify import verify


def get_client_metadata(client_request):
    client_ip = client_request.client.host
    origin = client_request.headers.get('Origin', 'Unknown')
    referer = client_request.headers.get('Referer', 'Unknown')
    source_app = origin if origin != 'Unknown' else referer

    return client_ip, source_app


def get_user_id(token: str):
    if token:
        return verify(token)
    return None   