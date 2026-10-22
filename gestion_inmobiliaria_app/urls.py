from django.urls import include, path
from rest_framework import routers

from . import views

enrutador = routers.DefaultRouter()

enrutador.register(r"regiones", views.RegionViewSet)
enrutador.register(r"comunas", views.ComunaViewSet)
enrutador.register(r"tipos-propiedad", views.TipoPropiedadViewSet)
enrutador.register(r"propietarios", views.PropietarioViewSet)
enrutador.register(r"clientes", views.ClienteViewSet)
enrutador.register(r"agentes", views.AgenteViewSet)
enrutador.register(r"propiedades", views.PropiedadViewSet)
enrutador.register(r"contratos", views.ContratoViewSet)

urlpatterns = [
    path("", include(enrutador.urls)),
]