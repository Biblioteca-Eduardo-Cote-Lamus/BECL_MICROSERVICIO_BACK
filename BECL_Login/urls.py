from django.urls import path
from .views import login_view, forgot_password, reset_password

urlpatterns = [
    path('login/', login_view, name='login'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
]
