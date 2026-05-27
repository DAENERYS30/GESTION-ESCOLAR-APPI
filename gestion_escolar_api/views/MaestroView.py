from django.db.models import *
from django.db import transaction
from gestion_escolar_api.models import Administradores, Maestros
from gestion_escolar_api.serializers import UserSerializer
from gestion_escolar_api.serializers import *
from gestion_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
import json
from django.shortcuts import get_object_or_404

""" para maestros, se pueden registrar, actualizar, eliminar y consultar maestros específicos o todos los maestros registrados """
class MaestrosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestrosSerializer(maestros, many=True).data
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    #Cambiar comillas simples por dobles para que sea JSON válido
                    materias_corregidas = maestro["materias_json"].replace("'", '"')
                    maestro["materias_json"] = json.loads(materias_corregidas)
                except Exception:
                    maestro["materias_json"] = []
        return Response(lista, 200)


class MaestroView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    #Obtener un maestro específico por su ID
    def get(self, request, *args, **kwargs):
        maestro = Maestros.objects.filter(id=request.GET.get("id"), user__is_active=1).first()
        if not maestro:
            return Response({"message": "Maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MaestrosSerializer(maestro)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
                                              materias_json= request.data["materias_json"],
                                              campus= request.data["campus"],
                                              sueldo= request.data["sueldo"])   
            maestro.save()

            return Response({"Maestro creado ID": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
     # Actualizar datos del maestro
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        maestro = Maestros.objects.filter(id=request.data["id"], user__is_active=1).first()
        if not maestro:
            return Response({"message": "Maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        user = maestro.user
        # Actualizar campos del usuario
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        #Guardamos los cambios del usuario no es necesario actualizar la contraseña
        user.save()

        # Actualizar campos del maestro
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"].upper()
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        maestro.materias_json = request.data["materias_json"]
        maestro.campus = request.data["campus"]
        maestro.sueldo = request.data["sueldo"]
        maestro.save()

        return Response({"message": "Maestro actualizado correctamente"}, status=status.HTTP_200_OK)
    
    #Función para eliminar un maestro específico por su ID
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Error al eliminar maestro"},400)
    