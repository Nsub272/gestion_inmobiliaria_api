from django.db import models


class ModeloBase(models.Model):
    """Campos de control comunes a todas las tablas del sistema."""

    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha actualización", auto_now=True)

    class Meta:
        abstract = True


class Persona(ModeloBase):
    """Datos personales comunes a propietarios, clientes y agentes."""

    nombre = models.CharField("Nombre", max_length=60)
    apellido = models.CharField("Apellido", max_length=60)
    rut = models.CharField("RUT", max_length=12, unique=True)
    correo = models.EmailField("Email", blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# ---------------------------------------------------------------- Catálogos

class Region(ModeloBase):
    codigo = models.CharField("Código", max_length=2, unique=True)
    nombre = models.CharField("Región", max_length=60)

    class Meta:
        db_table_comment = "Regiones de Chile donde se ubican las propiedades."

    def __str__(self):
        return self.nombre


class Comuna(ModeloBase):
    codigo = models.CharField("Código", max_length=5, unique=True)
    nombre = models.CharField("Comuna", max_length=60)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="comunas"
    )

    class Meta:
        db_table_comment = "Comunas de Chile. Cada comuna pertenece a una región."

    def __str__(self):
        return self.nombre


class TipoPropiedad(ModeloBase):
    nombre = models.CharField("Tipo de propiedad", max_length=40)
    descripcion = models.CharField("Descripción", max_length=255, blank=True)

    class Meta:
        db_table_comment = "Catálogo de tipos de propiedad: casa, departamento, local, terreno."

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------------ Personas

class Propietario(Persona):
    class Meta:
        db_table_comment = "Dueños de las propiedades que se administran, arriendan o venden."


class Cliente(Persona):
    class Meta:
        db_table_comment = "Personas que arriendan o compran una propiedad."


class Agente(Persona):
    class Meta:
        db_table_comment = "Corredores de la inmobiliaria que gestionan los contratos."


# ---------------------------------------------------------------- Propiedades

class Propiedad(ModeloBase):
    class Moneda(models.TextChoices):
        CLP = "CLP", "Peso chileno"
        UF = "UF", "Unidad de fomento"

    class Estado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        ARRENDADA = "ARRENDADA", "Arrendada"
        VENDIDA = "VENDIDA", "Vendida"
        RETIRADA = "RETIRADA", "Retirada del mercado"

    titulo = models.CharField("Título", max_length=120)
    descripcion = models.TextField("Descripción", blank=True)
    tipo = models.ForeignKey(
        TipoPropiedad, on_delete=models.PROTECT, related_name="propiedades"
    )
    propietario = models.ForeignKey(
        Propietario, on_delete=models.PROTECT, related_name="propiedades"
    )
    comuna = models.ForeignKey(
        Comuna, on_delete=models.PROTECT, related_name="propiedades"
    )
    calle = models.CharField("Calle", max_length=100)
    numero = models.CharField("Número", max_length=10)
    departamento = models.CharField("Dpto/Oficina", max_length=10, blank=True)
    superficie_m2 = models.DecimalField("Superficie (m²)", max_digits=8, decimal_places=2)
    dormitorios = models.PositiveSmallIntegerField("Dormitorios", default=0)
    banios = models.PositiveSmallIntegerField("Baños", default=0)
    precio = models.DecimalField("Precio", max_digits=14, decimal_places=2)
    moneda = models.CharField("Moneda", max_length=3, choices=Moneda.choices, default=Moneda.CLP)
    estado = models.CharField(
        "Estado", max_length=12, choices=Estado.choices, default=Estado.DISPONIBLE
    )

    class Meta:
        db_table_comment = "Propiedades publicadas por la inmobiliaria."

    def __str__(self):
        return f"{self.titulo} ({self.calle} {self.numero})"


# ------------------------------------------------------------------ Contratos

class Contrato(ModeloBase):
    class Tipo(models.TextChoices):
        ARRIENDO = "ARRIENDO", "Arriendo"
        VENTA = "VENTA", "Venta"

    class Estado(models.TextChoices):
        VIGENTE = "VIGENTE", "Vigente"
        FINALIZADO = "FINALIZADO", "Finalizado"
        CANCELADO = "CANCELADO", "Cancelado"

    tipo = models.CharField("Tipo de contrato", max_length=10, choices=Tipo.choices)
    propiedad = models.ForeignKey(
        Propiedad, on_delete=models.PROTECT, related_name="contratos"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="contratos"
    )
    agente = models.ForeignKey(
        Agente, on_delete=models.PROTECT, related_name="contratos"
    )
    fecha_inicio = models.DateField("Fecha inicio")
    fecha_termino = models.DateField("Fecha término", null=True, blank=True)
    monto = models.DecimalField("Monto", max_digits=14, decimal_places=2)
    moneda = models.CharField(
        "Moneda", max_length=3, choices=Propiedad.Moneda.choices, default=Propiedad.Moneda.CLP
    )
    estado = models.CharField(
        "Estado", max_length=12, choices=Estado.choices, default=Estado.VIGENTE
    )
    observaciones = models.TextField("Observaciones", blank=True)

    class Meta:
        db_table_comment = "Contratos de arriendo o venta que vinculan propiedad, cliente y agente."

    def __str__(self):
        return f"{self.get_tipo_display()} #{self.pk} - {self.propiedad}"