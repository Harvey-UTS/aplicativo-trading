"""Command: encapsula y despacha solicitudes de órdenes simuladas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from models.order import OrdenRegistro
from patterns.builder import PlataformaTrading


class ReceptorOrdenes(Protocol):
    """Contrato mínimo del servicio que recibe la operación encapsulada."""

    def crear_orden(
        self,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> tuple[PlataformaTrading, OrdenRegistro]: ...

    def ejecutar_orden(
        self,
        plataforma: PlataformaTrading,
        registro: OrdenRegistro,
    ) -> OrdenRegistro: ...


class ComandoOrden(ABC):
    """Abstracción de una solicitud de operación ejecutable."""

    @abstractmethod
    def ejecutar(self) -> OrdenRegistro:
        """Ejecuta la solicitud y devuelve su registro de operación."""


class ComandoEjecutarOrden(ComandoOrden):
    """Encapsula los parámetros y la ejecución completa de una orden."""

    def __init__(
        self,
        receptor: ReceptorOrdenes,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> None:
        self._receptor = receptor
        self._tipo_orden = tipo_orden
        self._lado = lado
        self._exchange = exchange
        self._activo_nombre = activo_nombre
        self._cantidad = float(cantidad)
        self._cartera_nombre = cartera_nombre
        self._precio_objetivo = precio_objetivo
        self._resultado: OrdenRegistro | None = None

    @property
    def resultado(self) -> OrdenRegistro | None:
        """Registro producido por el comando, si ya fue ejecutado."""
        return self._resultado

    def ejecutar(self) -> OrdenRegistro:
        # El mismo objeto de comando representa una sola solicitud; repetir su
        # ejecución devuelve el resultado previo y no genera otra operación.
        if self._resultado is not None:
            return self._resultado

        plataforma, registro = self._receptor.crear_orden(
            self._tipo_orden,
            self._lado,
            self._exchange,
            self._activo_nombre,
            self._cantidad,
            self._cartera_nombre,
            self._precio_objetivo,
        )
        self._resultado = self._receptor.ejecutar_orden(plataforma, registro)
        return self._resultado


class InvocadorOrdenes:
    """Centraliza el despacho y mantiene el historial de comandos completados."""

    def __init__(self) -> None:
        self._historial: list[ComandoOrden] = []

    def ejecutar(self, comando: ComandoOrden) -> OrdenRegistro:
        resultado = comando.ejecutar()
        if not any(registrado is comando for registrado in self._historial):
            self._historial.append(comando)
        return resultado

    def historial(self) -> tuple[ComandoOrden, ...]:
        """Devuelve una vista inmutable del historial de comandos despachados."""
        return tuple(self._historial)

    @property
    def cantidad_ejecutados(self) -> int:
        return len(self._historial)
