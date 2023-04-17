from django.conf import settings
from datetime import datetime, timedelta

import jwt

#Genera el token que mando al frontend 
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'ext': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token   