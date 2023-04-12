from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import User
import jwt

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user is not None and user.password_check(password):
                token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'token': token.decode('utf-8')})
            else:
                return JsonResponse({'error': 'Credenciales Invalidas'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'El Usuario no existe'})