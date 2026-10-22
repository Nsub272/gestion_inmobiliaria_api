from django.contrib import admin
from . import models

for modelo in (
    models.Region, models.Comuna, models.TipoPropiedad,
    models.Propietario, models.Cliente, models.Agente,
    models.Propiedad, models.Contrato,
):
    admin.site.register(modelo)