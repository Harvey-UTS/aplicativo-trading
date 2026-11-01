"""Coordina Chain of Responsibility y Command para despachar órdenes."""

from __future__ import annotations

from models.order import LadoOrden, OrdenRegistro, TipoOrden
from patterns.chain_of_responsibility import (
    CadenaValidacionOrden,
    ContextoValidacionOrden,
)
from patterns.command import ComandoEjecutarOrden, ComandoOrden, InvocadorOrdenes


class ServicioDespachoOrdenes:
    """Valida y despacha órdenes usando las interfaces públicas de la fachada.

    Este servicio añade el flujo Command + Chain sin modificar la fachada ni
    el servicio de trading existentes. La fachada actúa como receptor del
    comando y continúa delegando la lógica de negocio en sus servicios actuales.
    """

    def __init__(self, fachada) -> None:
        self._fachada = fachada
        self._cadena_validacion = CadenaValidacionOrden()
        self._invocador = InvocadorOrdenes()

    def ejecutar_orden(
        self,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> OrdenRegistro:
        """Valida la solicitud y luego la ejecuta como un comando."""
        tipo_enum = self._parse_tipo(tipo_orden)
        try:
            lado_enum = LadoOrden(str(lado).upper().strip())
        except ValueError as exc:
            raise ValueError("El lado de la operación debe ser COMPRA o VENTA.") from exc

        exchange_normalizado = str(exchange).upper().strip()
        activo = self._fachada.obtener_activo(activo_nombre)
        cartera = self._fachada.obtener_cartera(cartera_nombre)
        contexto = ContextoValidacionOrden(
            tipo_orden=tipo_enum,
            lado=lado_enum,
            exchange=exchange_normalizado,
            activo=activo,
            cantidad=cantidad,
            cartera=cartera,
            precio_objetivo=precio_objetivo,
        )
        resultado = self._cadena_validacion.validar(contexto)
        if not resultado.valido:
            raise ValueError(resultado.mensaje)

        comando = ComandoEjecutarOrden(
            receptor=self._fachada,
            tipo_orden=tipo_enum.value,
            lado=lado_enum.value,
            exchange=exchange_normalizado,
            activo_nombre=activo.nombre,
            cantidad=cantidad,
            cartera_nombre=cartera.nombre,
            precio_objetivo=precio_objetivo,
        )
        return self._invocador.ejecutar(comando)

    def historial_comandos(self) -> tuple[ComandoOrden, ...]:
        """Devuelve los comandos completados por este despachador."""
        return self._invocador.historial()

    @staticmethod
    def _parse_tipo(tipo_orden: str) -> TipoOrden:
        key = str(tipo_orden).upper().replace("-", " ").strip()
        aliases = {
            "MARKET": TipoOrden.MARKET,
            "LIMIT": TipoOrden.LIMIT,
            "STOP LOSS": TipoOrden.STOP_LOSS,
            "STOPLOSS": TipoOrden.STOP_LOSS,
        }
        try:
            return aliases[key]
        except KeyError as exc:
            raise ValueError("Tipo de orden no válido.") from exc
