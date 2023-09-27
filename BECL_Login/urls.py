from django.urls import path
from .views import  reset_password, valid_code, Login, ForgotPasswordView, Emails

urlpatterns = [
    path('login/', Login.as_view(), name='login_v2'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('valid_code/', valid_code, name='valid_code'),
    path('send_email/', Emails.as_view(), name='emails')
]
