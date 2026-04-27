from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from gestion_escolar_api.serializers import UserSerializer, AlumnosSerializer
from gestion_escolar_api.models import Alumnos



class AlumnoView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    # Registrar nuevo usuario alumno
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

            # Almacenar los datos adicionales del alumno en la tabla correspondiente
            # Asegúrate de que el modelo se llame 'Alumnos' (o en singular 'Alumno', según tu models.py)
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado ID": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)