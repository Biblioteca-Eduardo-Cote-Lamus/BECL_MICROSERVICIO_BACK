from django.urls import path
from .views import Login, ForgotPasswordView, ValidCode, ResetPassword

urlpatterns = [
    path('login/', Login.as_view(), name='login_v2'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('valid_code/', ValidCode.as_view(), name='valid_code_v2'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password')
]