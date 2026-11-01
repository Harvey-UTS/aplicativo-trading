"""Cadena de validación previa para las órdenes simuladas."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from models.asset import ActivoDigital
from models.order import LadoOrden, TipoOrden
from models.portfolio import Cartera


@dataclass(frozen=True, slots=True)
class ContextoValidacionOrden:
    """Datos necesarios para evaluar una solicitud antes de despacharla."""

    tipo_orden: TipoOrden
    lado: LadoOrden
    exchange: str
    activo: ActivoDigital
    cantidad: float
    cartera: Cartera
    precio_objetivo: float | None = None


@dataclass(frozen=True, slots=True)
class ResultadoValidacion:
    """Resultado uniforme producido por la cadena de validadores."""

    valido: bool
    mensaje: str


class ManejadorValidacionOrden(ABC):
    """Manejador base que delega la solicitud al siguiente eslabón."""

    def __init__(self, siguiente: ManejadorValidacionOrden | None = None) -> None:
        self._siguiente = siguiente

    def enlazar(self, siguiente: ManejadorValidacionOrden) -> ManejadorValidacionOrden:
        """Conecta el siguiente manejador y permite construir la cadena."""
        self._siguiente = siguiente
        return siguiente

    def manejar(self, contexto: ContextoValidacionOrden) -> ResultadoValidacion:
        error = self.validar(contexto)
        if error:
            return ResultadoValidacion(False, error)
        if self._siguiente is not None:
            return self._siguiente.manejar(contexto)
        return ResultadoValidacion(True, "Validación previa completada.")

    @abstractmethod
    def validar(self, contexto: ContextoValidacionOrden) -> str | None:
        """Devuelve un mensaje si la solicitud debe detenerse."""


class ValidarSolicitudOrden(ManejadorValidacionOrden):
    """Comprueba los datos generales y los valores admitidos por la plataforma."""

    EXCHANGES_PERMITIDOS = frozenset({"A", "B", "C"})

    def validar(self, contexto: ContextoValidacionOrden) -> str | None:
        if not isinstance(contexto.tipo_orden, TipoOrden):
            return "El tipo de orden no es válido."
        if not isinstance(contexto.lado, LadoOrden):
            return "El lado de la operación debe ser COMPRA o VENTA."
        if str(contexto.exchange).upper().strip() not in self.EXCHANGES_PERMITIDOS:
            return "El exchange seleccionado no está disponible. Use A, B o C."
        try:
            cantidad = float(contexto.cantidad)
        except (TypeError, ValueError):
            return "La cantidad de la orden debe ser numérica."
        if not math.isfinite(cantidad) or cantidad <= 0:
            return "La cantidad de la orden debe ser mayor que cero."
        return None


class ValidarActivoCantidad(ManejadorValidacionOrden):
    """Verifica el activo y aplica sus reglas particulares de cantidad."""

    def validar(self, contexto: ContextoValidacionOrden) -> str | None:
        if not isinstance(contexto.activo, ActivoDigital):
            return "El activo solicitado no corresponde a un activo digital válido."
        try:
            contexto.activo.validar_cantidad(float(contexto.cantidad))
        except (TypeError, ValueError) as exc:
            return str(exc)
        return None


class ValidarCarteraOrden(ManejadorValidacionOrden):
    """Comprueba que la solicitud esté asociada a una cartera existente."""

    def validar(self, contexto: ContextoValidacionOrden) -> str | None:
        if not isinstance(contexto.cartera, Cartera):
            return "La cartera seleccionada no está disponible."
        if not str(contexto.cartera.nombre).strip():
            return "La cartera debe tener un nombre válido."
        return None


class ValidarPrecioObjetivo(ManejadorValidacionOrden):
    """Valida el precio objetivo requerido por las órdenes Limit y Stop Loss."""

    def validar(self, contexto: ContextoValidacionOrden) -> str | None:
        requiere_objetivo = contexto.tipo_orden in (TipoOrden.LIMIT, TipoOrden.STOP_LOSS)
        if requiere_objetivo and contexto.precio_objetivo is None:
            return "La orden Limit o Stop Loss requiere un precio objetivo."
        if contexto.precio_objetivo is not None:
            try:
                objetivo = float(contexto.precio_objetivo)
            except (TypeError, ValueError):
                return "El precio objetivo debe ser numérico."
            if not math.isfinite(objetivo) or objetivo <= 0:
                return "El precio objetivo debe ser mayor que cero."
        if not requiere_objetivo and contexto.precio_objetivo is not None:
            return "La orden Market no utiliza un precio objetivo."
        return None


class CadenaValidacionOrden:
    """Punto de entrada que ejecuta los validadores en el orden establecido."""

    def __init__(self, primero: ManejadorValidacionOrden | None = None) -> None:
        self._primero = primero or self.crear_cadena_por_defecto()

    @staticmethod
    def crear_cadena_por_defecto() -> ManejadorValidacionOrden:
        solicitud = ValidarSolicitudOrden()
        solicitud.enlazar(ValidarActivoCantidad()).enlazar(
            ValidarCarteraOrden()
        ).enlazar(ValidarPrecioObjetivo())
        return solicitud

    def validar(self, contexto: ContextoValidacionOrden) -> ResultadoValidacion:
        if self._primero is None:
            return ResultadoValidacion(True, "No hay validadores configurados.")
        return self._primero.manejar(contexto)
