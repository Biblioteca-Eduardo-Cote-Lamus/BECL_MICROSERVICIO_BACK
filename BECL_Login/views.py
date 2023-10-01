from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import  TokenObtainPairView
from dotenv import load_dotenv
import re

from .models import Usuarios
from .utils.otp import OTP
from .serializers.token_serializer import MyTokenSerializer
from .utils.sendEmails import send_email

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

    def __email_valid(email):
        regex = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if re.fullmatch(regex, email):
            return True
        return False

    def post(self, request):
        email = request.data.get("email")

        if not self.__email_valid(email):
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
                {"ok": True, "message": "The code was sended", "code": OTP.generate_code()},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {"ok": False, "message": "unexpected error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
class ValidCode(APIView):

    def post(self, request):    
        code = request.data.get('codeVery')
        if not OTP.validate_code(code):
            return Response({'ok': False, 'message': 'The code has been expired'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({'ok': True, 'message': 'The code has been verified'}, status=status.HTTP_200_OK)

class ResetPassword(APIView):
    def post(self, request): 
        email = request.data.get('email')
        password = request.data.get('password')

        # change the password

        user = Usuarios.objects.filter(email=email).first()
        if not user:
            return Response(
                {"ok": False, "message": f"{email} does'nt exist. Try again"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        user.set_password(password)
        user.save()

        return Response({'ok':True, 'message': 'The password has been updated'}, status=status.HTTP_200_OK)
    





