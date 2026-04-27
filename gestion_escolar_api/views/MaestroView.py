from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from gestion_escolar_api.serializers import UserSerializer, MaestrosSerializer
from gestion_escolar_api.models import Maestros

class MaestroView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    # Registrar nuevo usuario maestro
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        # Serializamos los datos del usuario para volverlo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            # Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            # Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Nombre de usuario "+email+", ya existe"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)

            user.save()
            # Cifrar la contraseña
            user.set_password(password)
            user.save()

            # Asignar el rol al usuario a la tabla de grupos
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # Almacenar los datos adicionales del maestro en la tabla correspondiente
            maestro = Maestros.objects.create(user=user,
                                              id_trabajador= request.data["id_trabajador"],
                                              fecha_nacimiento= request.data["fecha_nacimiento"],
                                              telefono= request.data["telefono"],
                                              rfc= request.data["rfc"].upper(),
                                              cubiculo= request.data["cubiculo"],
                                              area_investigacion= request.data["area_investigacion"],
                                              materias_json= request.data["materias_json"])
            maestro.save()

            return Response({"Maestro creado ID": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)