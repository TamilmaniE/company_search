

from datetime import datetime, timedelta
import jwt
from django.conf import settings

def generate_access_token(user):
    payload = {
        'id': str(user['_id']),
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user):
    payload = {
        'id': str(user['_id']),
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
