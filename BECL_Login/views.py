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
import jwt
import json
import pyotp

# ============================================


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import authenticate
from .utils.otp import OTP

from .serializers.token_serializer import MyTokenSerializer
from .utils.sendEmails import send_email

import re

load_dotenv()


class Login(TokenObtainPairView):
    serializer_class = MyTokenSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {
                    "ok": False,
                    "message": f"The user with {username} does not exist or password is not correct",
                },
                status=404,
            )

        login_serializer = self.serializer_class(data=request.data)

        if not login_serializer.is_valid():
            return Response({"ok": False, "message": "Invalid data format"})

        return Response(
            {
                "ok": True,
                "message": "Login done!",
                "token": login_serializer.validated_data.get("access"),
                "refresh": login_serializer.validated_data.get("refresh"),
            }
        )


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email_valid(email):
            return Response(
                {"ok": False, "message": "El correo introducido no es valido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check the user exists on the system
        user = Usuarios.objects.filter(email=email).first()

        if not user:
            return Response(
                {"ok": False, "message": f"{email} does'nt exist. Try again"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # if the user exists on the system
        try:
            html_template = render_to_string(
                "plantilla_recuperacion_pass.html", {"code_very": OTP.generate_code()}
            )
            send_email(
                {
                    "subject": "Recuperación de contraseña",
                    "from": "pruebasbeclpbd@gmail.com",
                    "to": "pruebasbeclpbd@gmail.com",
                },
                html_template=html_template,
            )
            return Response(
                {"ok": True, "message": "The code was sended"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {"ok": False, "message": "unexpected error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            


class Emails(APIView):
    def post(self, request):
        html_template = render_to_string(
            "plantilla_recuperacion_pass.html", {"code_very": f"{ OTP.generate_code()}"}
        )
        send_email(
            {
                "subject": "Recuperacion de contrasenia",
                "from": "pruebasbeclpbd@gmail.com",
                "to": "pruebasbeclpbd@gmail.com",
            },
            html_template=html_template,
            files=["BECL_PDB/doc/doc_auditorio/pruebas.docx"],
        )
        return Response({"msg": "email was send"})


# @csrf_exempt
# @require_http_methods(["POST"])
# def forgot_password(request):
#     body = json.loads(request.body.decode("utf-8"))
#     email = body.get("email")
#     if email_valid(email):
#         try:
#             # Obtengo el usuario de acuerdo al email suministrado
#             user = Usuarios.objects.filter(email=email).first()
#             # Genero el token de cambiar contraseña
#             token = generate_forgot_token(user.username)
#             # Creo el digo de verificacion para la contraseña
#             totp = pyotp.TOTP(os.getenv("SECRET_KEY_P"), interval=59)
#             code = totp.now()
#             # Diccionario con los datos que le paso a la plantilla
#             context = {
#                 "code_very": f"{code}",
#             }
#             # Renderiza la plantilla del email con los datos necesarios
#             html_template = render_to_string(
#                 "plantilla_recuperacion_pass.html", context
#             )
#             text_template = strip_tags(html_template)
#             # Creo un objeto EmailMultiAlternatives para enviar el correo electronico
#             mail = EmailMultiAlternatives(
#                 "Recuperación de Contraseña",
#                 text_template,
#                 "pruebasbeclpbd@gmail.com",
#                 [email],
#             )
#             # Agrego la plantilla HTML como un contenido alternativo al correo electronico
#             mail.attach_alternative(html_template, "text/html")
#             mail.send()
#             return JsonResponse({"ok": True, "token": token}, status=200)
#         except Usuarios.DoesNotExist:
#             return JsonResponse({"ok": False, "message": "El Correo no existe"})
#     else:
#         return JsonResponse(
#             {"ok": False, "message": "El correo introducido no es valido"}
#         )


@csrf_exempt
@require_http_methods(["POST"])
def valid_code(request):
    body = json.loads(request.body.decode("utf-8"))
    code_very = int(body.get("codeVery"))
    token = body.get("token")
    totp = pyotp.TOTP(os.getenv("SECRET_KEY_P"), interval=59)
    try:
        if not is_Token_Valid(token) and totp.verify(code_very):
            return JsonResponse({"ok": True, "message": "Codigo verificado"})
        return JsonResponse({"ok": True})
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({"ok": False, "message": "El token a expirado"})
    except jwt.exceptions.InvalidSignatureError:
        return JsonResponse({"ok": False, "message": "El token es invalido"})


@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    body = json.loads(request.body.decode("utf-8"))
    token = body.get("token")
    email = body.get("email")
    password = body.get("password")
    try:
        if not is_Token_Valid(token):
            user = Usuarios.objects.get(email=email)
            user.password_encript(password)
            user.save()
            return JsonResponse(
                {"ok": True, "message": "Se ha cambiado la contraseña con exito"},
                status=200,
            )
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({"ok": True, "message": "El token ha caducado"}, status=400)
    except jwt.exceptions.InvalidSignatureError:
        return JsonResponse({"ok": False, "message": "Token Invalido"}, status=400)
    except Usuarios.DoesNotExist:
        return JsonResponse(
            {"ok": False, "message": "El Usuario no se ha encontrado"}, status=400
        )


def generate_login_token(user):
    payload = {
        "user_rol": user.rol.descripcion,
        "user_id": user.codigo,
        "user_name": user.nombre,
        "user_email": user.email,
        "user_faculty": user.facultad,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def generate_forgot_token(user_id):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=5)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def is_Token_Valid(token):
    colombia_time = datetime.utcnow() + timedelta(hours=-5)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    exp_timestamp = decode_token["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    if colombia_time < exp_datetime:
        return False
    else:
        return True


def email_valid(email):
    regex = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    if re.fullmatch(regex, email):
        return True
    return False
