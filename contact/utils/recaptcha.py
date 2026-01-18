import urllib.parse
import urllib.request
import json
from django.conf import settings

def verify_recaptcha(token, remote_ip=None):
    """
    Verify reCAPTCHA v2 token.
    Returns (success, error_message)
    """
    secret_key = settings.RECAPTCHA_SECRET_KEY
    if not secret_key:
        return False, "reCAPTCHA not configured"

    data = {
        'secret': secret_key,
        'response': token,
    }
    if remote_ip:
        data['remoteip'] = remote_ip

    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False), None
    except Exception as e:
        return False, str(e)