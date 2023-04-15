from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import Usuarios
import jwt
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        username = body.get("username")
        password = body.get("password")
        try:
            user = Usuarios.objects.get(usuario=username)
            if user is not None and user.password_check(password):
                token = jwt.encode({'user_id': user.codigo, 'user_name': user.nombre,
                                    'user_email': user.email, 'user_faculty': user.facultad}, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'token': token})
            else:
                return JsonResponse({'error': 'Credenciales Invalidas'})
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El Usuario no existe'})