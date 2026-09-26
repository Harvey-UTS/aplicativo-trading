"""Bridge: tipos de orden desacoplados de exchanges."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.asset import ActivoDigital
from models.order import ExecutionResult, EstadoOrden, LadoOrden, TipoOrden


class EjecutorOrden(ABC):
    """Implementador del Bridge y producto abstracto para Abstract Factory."""

    nombre_exchange = "Exchange"

    @abstractmethod
    def ejecutar(
        self,
        orden: "OrdenTrading",
        activo: ActivoDigital,
        lado: LadoOrden,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        pass

    def _resultado_ejecutado(
        self,
        activo: ActivoDigital,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        return ExecutionResult(
            status=EstadoOrden.EJECUTADA,
            message=(
                f"Orden {activo.nombre} ejecutada en {self.nombre_exchange}."
            ),
            total=precio * cantidad,
        )

    def _resultado_pendiente(self, mensaje: str) -> ExecutionResult:
        return ExecutionResult(
            status=EstadoOrden.PENDIENTE,
            message=mensaje,
            total=0.0,
        )


class OrdenTrading(ABC):
    """Abstracción del Bridge para el tipo de orden."""

    tipo: TipoOrden = TipoOrden.MARKET

    def __init__(self, executor: EjecutorOrden) -> None:
        self.executor = executor

    def cambiar_executor(self, executor: EjecutorOrden) -> None:
        self.executor = executor

    @abstractmethod
    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        pass

    def ejecutar(
        self,
        activo: ActivoDigital,
        lado: LadoOrden,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        lado_enum = lado if isinstance(lado, LadoOrden) else LadoOrden(str(lado).upper())
        activo.validar_cantidad(cantidad)
        self.validar(lado_enum, cantidad, precio)
        return self.executor.ejecutar(self, activo, lado_enum, cantidad, precio)


class OrdenMarket(OrdenTrading):
    tipo = TipoOrden.MARKET

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Market requiere cantidad y precio positivos.")


class OrdenLimit(OrdenTrading):
    tipo = TipoOrden.LIMIT

    def __init__(self, executor: EjecutorOrden, precio_limite: float) -> None:
        super().__init__(executor)
        if precio_limite <= 0:
            raise ValueError("El precio límite debe ser mayor que cero.")
        self.precio_limite = float(precio_limite)

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Limit requiere cantidad y precio positivos.")


class OrdenStopLoss(OrdenTrading):
    tipo = TipoOrden.STOP_LOSS

    def __init__(self, executor: EjecutorOrden, precio_activacion: float) -> None:
        super().__init__(executor)
        if precio_activacion <= 0:
            raise ValueError("El precio de activación debe ser mayor que cero.")
        self.precio_activacion = float(precio_activacion)

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Stop Loss requiere cantidad y precio positivos.")


class ExchangeAExecutor(EjecutorOrden):
    nombre_exchange = "Exchange A"

    def ejecutar(self, orden, activo, lado, cantidad, precio) -> ExecutionResult:
        if isinstance(orden, OrdenLimit):
            condicion = precio <= orden.precio_limite if lado == LadoOrden.COMPRA else precio >= orden.precio_limite
            if not condicion:
                return self._resultado_pendiente(
                    f"Orden Limit pendiente: el precio actual (${precio:,.2f}) "
                    f"no cumple el límite (${orden.precio_limite:,.2f})."
                )

        if isinstance(orden, OrdenStopLoss):
            condicion = precio >= orden.precio_activacion if lado == LadoOrden.COMPRA else precio <= orden.precio_activacion
            if not condicion:
                return self._resultado_pendiente(
                    f"Stop Loss pendiente: el precio actual (${precio:,.2f}) "
                    f"no ha alcanzado la activación (${orden.precio_activacion:,.2f})."
                )

        return self._resultado_ejecutado(activo, cantidad, precio)


class ExchangeBExecutor(ExchangeAExecutor):
    nombre_exchange = "Exchange B"


class ExchangeCExecutor(ExchangeAExecutor):
    nombre_exchange = "Exchange C"
