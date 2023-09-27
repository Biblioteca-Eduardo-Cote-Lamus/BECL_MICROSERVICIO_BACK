from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..models import CargoUsuario
from ..models import Usuarios

class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: Usuarios):
        token = super().get_token(user)

        token['user_rol'] =  user.cargo.descripcion
        token['user_name'] =  f'{user.first_name} {user.last_name}'
        token['user_email'] =  user.email
        token['user_faculty'] =  user.facultad

        return token