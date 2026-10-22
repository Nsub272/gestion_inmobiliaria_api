from django.db.models import ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from . import models, serializers


class BaseViewSet(viewsets.ModelViewSet):
    """ModelViewSet con búsqueda, ordenamiento y borrado seguro.

    Un ModelViewSet entrega list, retrieve, create, update, partial_update
    y destroy, es decir GET, POST, PUT, PATCH y DELETE.
    """

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def destroy(self, request, *args, **kwargs):
        # Las claves foráneas usan PROTECT: si hay registros asociados,
        # se responde 409 en lugar de dejar caer el servidor con un error 500.
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar: existen registros asociados."},
                status=status.HTTP_409_CONFLICT,
            )


class RegionViewSet(BaseViewSet):
    queryset = models.Region.objects.all().order_by("id")
    serializer_class = serializers.RegionSerializer
    search_fields = ["codigo", "nombre"]


class ComunaViewSet(BaseViewSet):
    queryset = models.Comuna.objects.select_related("region").order_by("id")
    serializer_class = serializers.ComunaSerializer
    search_fields = ["codigo", "nombre", "region__nombre"]


class TipoPropiedadViewSet(BaseViewSet):
    queryset = models.TipoPropiedad.objects.all().order_by("id")
    serializer_class = serializers.TipoPropiedadSerializer
    search_fields = ["nombre"]


class PropietarioViewSet(BaseViewSet):
    queryset = models.Propietario.objects.all().order_by("id")
    serializer_class = serializers.PropietarioSerializer
    search_fields = ["nombre", "apellido", "rut", "correo"]


class ClienteViewSet(BaseViewSet):
    queryset = models.Cliente.objects.all().order_by("id")
    serializer_class = serializers.ClienteSerializer
    search_fields = ["nombre", "apellido", "rut", "correo"]


class AgenteViewSet(BaseViewSet):
    queryset = models.Agente.objects.all().order_by("id")
    serializer_class = serializers.AgenteSerializer
    search_fields = ["nombre", "apellido", "rut", "correo"]


class PropiedadViewSet(BaseViewSet):
    queryset = models.Propiedad.objects.select_related(
        "tipo", "propietario", "comuna"
    ).order_by("id")
    serializer_class = serializers.PropiedadSerializer
    search_fields = ["titulo", "calle", "comuna__nombre", "estado"]
    ordering_fields = ["precio", "superficie_m2", "created_at"]


class ContratoViewSet(BaseViewSet):
    queryset = models.Contrato.objects.select_related(
        "propiedad", "cliente", "agente"
    ).order_by("id")
    serializer_class = serializers.ContratoSerializer
    search_fields = ["tipo", "estado", "cliente__apellido", "propiedad__titulo"]
    ordering_fields = ["monto", "fecha_inicio", "created_at"]