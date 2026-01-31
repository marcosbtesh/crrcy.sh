from flask import request

def parse_list(param_str):
    if not param_str:
        return []
    return [x.strip() for x in param_str.split(",")]

def is_curl_client():
    """Checks if the request is coming from curl."""
    user_agent = request.headers.get('User-Agent', '').lower()
    return 'curl' in user_agent
