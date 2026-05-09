from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from gestion_escolar_api.views import auth, users
from gestion_escolar_api.views import AlumnoView  # Importamos el ARCHIVO
from gestion_escolar_api.views import MaestroView # Importamos el ARCHIVO

urlpatterns = [
    #Agregamos las endpoints de usuarios
    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Lista de administradores
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
# --- ENDPOINTS DE ALUMNOS ---
    # Aquí: Archivo AlumnoView . Clase AlumnoView
    path('alumnos/', AlumnoView.AlumnoView.as_view()), 

    # --- ENDPOINTS DE MAESTROS ---
    # Aquí: Archivo MaestroView . Clase MaestroView
    path('maestros/', MaestroView.MaestroView.as_view()),

    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)