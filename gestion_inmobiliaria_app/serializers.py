import re

from rest_framework import serializers

from . import models


def validar_rut(valor):
    """Valida un RUT chileno con el algoritmo módulo 11. Formato exigido: 12345678-5."""
    if not re.fullmatch(r"\d{7,8}-[\dK]", valor):
        raise serializers.ValidationError(
            "Formato de RUT inválido. Use 12345678-5 (sin puntos, con guion y K en mayúscula)."
        )
    cuerpo, digito = valor.split("-")
    suma, factor = 0, 2
    for numero in reversed(cuerpo):
        suma += int(numero) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
    if digito != esperado:
        raise serializers.ValidationError("El dígito verificador del RUT no es válido.")
    return valor


# ---------------------------------------------------------------- Catálogos

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = "__all__"


class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comuna
        fields = "__all__"


class TipoPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoPropiedad
        fields = "__all__"


# ------------------------------------------------------------------ Personas

class PersonaSerializer(serializers.ModelSerializer):
    """Base para Propietario, Cliente y Agente: todos validan el RUT."""

    def validate_rut(self, valor):
        return validar_rut(valor)


class PropietarioSerializer(PersonaSerializer):
    class Meta:
        model = models.Propietario
        fields = "__all__"


class ClienteSerializer(PersonaSerializer):
    class Meta:
        model = models.Cliente
        fields = "__all__"


class AgenteSerializer(PersonaSerializer):
    class Meta:
        model = models.Agente
        fields = "__all__"


# ---------------------------------------------------------------- Propiedades

class PropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Propiedad
        fields = "__all__"

    def validate_precio(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero.")
        return valor

    def validate_superficie_m2(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("La superficie debe ser mayor a cero.")
        return valor


# ------------------------------------------------------------------ Contratos

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contrato
        fields = "__all__"

    def validate_monto(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return valor

    def validate(self, datos):
        # En PATCH llegan solo algunos campos: se completa con los del registro existente.
        actual = self.instance
        inicio = datos.get("fecha_inicio", getattr(actual, "fecha_inicio", None))
        termino = datos.get("fecha_termino", getattr(actual, "fecha_termino", None))
        tipo = datos.get("tipo", getattr(actual, "tipo", None))

        if inicio and termino and termino < inicio:
            raise serializers.ValidationError(
                {"fecha_termino": "La fecha de término no puede ser anterior a la de inicio."}
            )
        if tipo == models.Contrato.Tipo.ARRIENDO and not termino:
            raise serializers.ValidationError(
                {"fecha_termino": "Un contrato de arriendo requiere fecha de término."}
            )
        return datos