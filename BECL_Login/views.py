from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta
from .models import Usuarios
import pytz
import jwt
import json


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
    if not email:
        return JsonResponse({'ok': False, 'message': 'Debe ingresar una direccion de correo electronica'}, status=400)
    try:
        user = Usuarios.objects.get(email=email)
        token = generate_forgot_token(user.codigo)
        reset_link = f'reset_password?token={token}'
        send_mail(
            subject= 'Recuperacion de Contraseña', 
            message= f'Haga click en el siguiente enlace para restablecer su contraseña : {reset_link}', 
            from_email = settings.EMAIL_HOST_USER, 
            recipient_list = [email],
            fail_silently= False)
        return JsonResponse({'ok': True, 'message': f'Se ha enviado un enlace de recuperación de contraseña a su correo electronico: {email}'}, status= 200)
    except Usuarios.DoesNotExist:
        return JsonResponse({'ok': False, 'message': 'El Usuario no existe'})    

@csrf_exempt
@require_http_methods(['POST'])
def reset_password(request):
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    password = body.get('password')
    try:
        if not is_Token_Valid(token) or not password:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = Usuarios.objects.get(codigo=user_id)
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