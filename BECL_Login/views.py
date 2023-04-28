from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import Usuarios
from datetime import datetime, timedelta
import jwt
import json

def generate_login_token(user):
    payload = {
        'user_id': user.codigo,
        'user_name': user.nombre,
        'user_email': user.email,
        'user_faculty': user.facultad,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def generate_forgot_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=5)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        username = body.get("username")
        password = body.get("password")
        try:
            user = Usuarios.objects.get(usuario=username)
            if user is not None and user.password_check(password):
                token = generate_login_token(user)
                return JsonResponse({'token': token, 'ok': True})
            else:
                return JsonResponse({'error': 'Credenciales Invalidas', 'ok': False})
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El Usuario no existe'})
#TODO:Terminar de hacer esta vista 
@csrf_exempt
@require_http_methods(['POST'])
def forgot_password(request):
    body = json.loads(request.body.decode('utf-8'))
    email = body.get("email")
    if not email:
        return JsonResponse({'message': 'Debe ingresar una direccion de correo electronica'}, status=400)
    try:
        user = Usuarios.objects.get(email=email)
        token = generate_forgot_token(user.codigo)
        reset_link = f'{settings.FRo}'
    except Usuarios.DoesNotExist:
        return JsonResponse({'error': 'El Usuario no existe'})    

@csrf_exempt
@require_http_methods(['POST'])
def reset_password(request):
    pass    