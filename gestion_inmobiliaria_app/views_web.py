from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from . import models


def _formatear_precio(propiedad):
    """Devuelve el precio con formato chileno: $120.000.000 o UF 3.500,00."""
    if propiedad.moneda == models.Propiedad.Moneda.UF:
        texto = f"{propiedad.precio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"UF {texto}"
    return "$" + f"{int(propiedad.precio):,}".replace(",", ".")


def _preparar(propiedades):
    """Agrega a cada propiedad el precio formateado y un tono de color para la tarjeta."""
    for propiedad in propiedades:
        propiedad.precio_texto = _formatear_precio(propiedad)
        propiedad.tono = propiedad.tipo_id % 4
    return propiedades


def _disponibles():
    """Solo las propiedades habilitadas y disponibles son visibles al público."""
    return (
        models.Propiedad.objects.filter(
            habilitado=True, estado=models.Propiedad.Estado.DISPONIBLE
        )
        .select_related("tipo", "comuna__region")
        .order_by("-created_at")
    )


def _comunas_con_oferta():
    return (
        models.Comuna.objects.filter(
            habilitado=True,
            propiedades__habilitado=True,
            propiedades__estado=models.Propiedad.Estado.DISPONIBLE,
        )
        .distinct()
        .order_by("nombre")
    )


def inicio(request):
    contexto = {
        "destacadas": _preparar(list(_disponibles()[:6])),
        "total": _disponibles().count(),
        "comunas": _comunas_con_oferta(),
        "tipos": models.TipoPropiedad.objects.filter(habilitado=True).order_by("nombre"),
    }
    return render(request, "inicio.html", contexto)


def catalogo(request):
    propiedades = _disponibles()
    tipo = request.GET.get("tipo", "")
    comuna = request.GET.get("comuna", "")
    dormitorios = request.GET.get("dormitorios", "")

    if tipo.isdigit():
        propiedades = propiedades.filter(tipo_id=int(tipo))
    if comuna.isdigit():
        propiedades = propiedades.filter(comuna_id=int(comuna))
    if dormitorios.isdigit():
        propiedades = propiedades.filter(dormitorios__gte=int(dormitorios))

    pagina = Paginator(propiedades, 9).get_page(request.GET.get("page"))
    pagina.object_list = _preparar(list(pagina.object_list))

    filtros = request.GET.copy()
    filtros.pop("page", None)

    contexto = {
        "pagina": pagina,
        "tipos": models.TipoPropiedad.objects.filter(habilitado=True).order_by("nombre"),
        "comunas": _comunas_con_oferta(),
        "seleccion": {"tipo": tipo, "comuna": comuna, "dormitorios": dormitorios},
        "filtros_url": filtros.urlencode(),
    }
    return render(request, "catalogo.html", contexto)


def detalle_propiedad(request, pk):
    propiedad = get_object_or_404(_disponibles(), pk=pk)
    _preparar([propiedad])
    return render(request, "detalle.html", {"p": propiedad})