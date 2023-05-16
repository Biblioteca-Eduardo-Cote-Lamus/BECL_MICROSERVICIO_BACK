from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta
from .models import Usuarios
from dotenv import load_dotenv
import os
import pytz
import jwt
import json
import pyotp
import time
import re

load_dotenv()

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
            return JsonResponse({'error': 'El Usuario no existe', 'ok': False})
        
#TODO:Terminar de hacer esta vista 
@csrf_exempt
@require_http_methods(['POST'])
def forgot_password(request):
    body = json.loads(request.body.decode('utf-8'))
    email = body.get("email")
    if email_valid(email):
        try:
            #Obtengo el usuario de acuerdo al email suministrado
            user = Usuarios.objects.get(email=email)
            #Genero el token de cambiar contraseña
            token = generate_forgot_token(user.codigo)
            #Creo el digo de verificacion para la contraseña
            totp = pyotp.TOTP(os.getenv('SECRET_KEY_P'), interval=30)
            code = totp.now()
            print(f'Codigo: {code}')
            #Diccionario con los datos que le paso a la plantilla
            context = {
                'code_very': code,
            }
            #Renderiza la plantilla del email con los datos necesarios
            html_template = render_to_string('plantilla_recuperacion_pass.html', context)
            text_template = strip_tags(html_template)
            #Creo un objeto EmailMultiAlternatives para enviar el correo electronico
            mail = EmailMultiAlternatives(
                'Recuperación de Contraseña',
                text_template,
                'andresalexanderss@ufps.edu.co',
                [email]
            )
            #Agrego la plantilla HTML como un contenido alternativo al correo electronico
            mail.attach_alternative(html_template, 'text/html')
            mail.send()
            return JsonResponse({'ok': True, 'token':token}, status= 200)
        except Usuarios.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'El Correo no existe'})
    else:
        return JsonResponse({'ok': False, 'message': 'El correo introducido no es valido'})

@csrf_exempt
@require_http_methods(['POST'])
def valid_code(request):
    body = json.loads(request.body.decode('utf-8'))
    code_very = int(body.get('codeVery'))
    token = body.get('token')
    totp = pyotp.TOTP(os.getenv('SECRET_KEY_P'), interval=30)
    try:
        if not is_Token_Valid(token) and totp.verify(code_very):
            return JsonResponse({'ok': True, 'message': 'Codigo verificado'})
        return JsonResponse({'ok': True})
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({'ok': False, 'message': 'El token a expirado'})
    except jwt.exceptions.InvalidSignatureError:
        return JsonResponse({'ok': False, 'message': 'El token es invalido'})

@csrf_exempt
@require_http_methods(['POST'])
def reset_password(request):
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    email = body.get('email')
    password = body.get('password')
    try:
        if not is_Token_Valid(token):
            user = Usuarios.objects.get(email=email)
            user.password_encript(password)
            user.save()
            return JsonResponse({'ok': True, 'message': 'Se ha cambiado la contraseña con exito'}, status= 200)
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({'ok': True, 'message': 'El token ha caducado'}, status = 400)
    except jwt.exceptions.InvalidSignatureError:
        return JsonResponse({'ok': False, 'message': 'Token Invalido'}, status = 400)
    except Usuarios.DoesNotExist:
        return JsonResponse({'ok': False, 'message': 'El Usuario no se ha encontrado'}, status= 400)

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

def is_Token_Valid(token):
    colombia_time = datetime.utcnow() + timedelta(hours=-5)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    exp_timestamp= decode_token['exp']
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    if colombia_time < exp_datetime:
        return False
    else:
        return True
    
def email_valid(email):
    dominio = 'ufps.edu.co'
    patron = r'^[a-zA-Z0-9._%+-]+@' + re.escape(dominio) + r'$'
    if re.match(patron, email):
        return True
    return False