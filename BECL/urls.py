from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('BECL_Login.urls')),
    path('', include('BECL_PDB.urls')),
    path('', include('BECL_Admin.urls')),
]
