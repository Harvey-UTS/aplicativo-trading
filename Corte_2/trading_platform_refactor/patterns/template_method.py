"""Template Method: define el flujo común de ejecución de órdenes."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.order import ExecutionResult, EstadoOrden, OrdenRegistro
from patterns.state import MaquinaEstadoOrden


class FlujoEjecucionOrdenTemplate(ABC):
    """Esqueleto invariable de una operación; las subclases especializan compra y venta."""

    def ejecutar(
        self,
        *,
        market_service,
        portfolio_service,
        mediador,
        plataforma,
        registro: OrdenRegistro,
        historial: list[OrdenRegistro],
    ) -> OrdenRegistro:
        if plataforma.orden is None or plataforma.activo is None or plataforma.cartera is None:
            raise ValueError("La plataforma de trading no tiene una orden completa configurada.")

        activo = plataforma.activo
        cartera = plataforma.cartera
        precio = market_service.obtener_precio(activo, registro.exchange)
        registro.precio = precio
        activo.precio = precio

        precios_cartera = {
            posicion.nombre: market_service.obtener_precio(posicion.nombre, registro.exchange)
            for posicion in cartera.activos
        }
        precios_cartera[activo.nombre] = precio

        self.validar_operacion(
            portfolio_service,
            cartera,
            activo.nombre,
            registro.cantidad,
            precio,
            precios_cartera,
        )

        resultado = plataforma.orden.ejecutar(
            activo,
            registro.lado,
            registro.cantidad,
            precio,
        )

        if resultado.status == EstadoOrden.EJECUTADA:
            mediador.notificar(
                mediador.ANTES_ACTUALIZAR_CARTERA,
                cartera=cartera,
                registro=registro,
            )
            try:
                resultado = self.actualizar_cartera(
                    cartera, activo, registro, resultado, precio
                )
                if resultado.status != EstadoOrden.EJECUTADA:
                    mediador.notificar(mediador.RESTAURAR_CARTERA, cartera=cartera)
            except Exception:
                mediador.notificar(mediador.RESTAURAR_CARTERA, cartera=cartera)
                raise

        MaquinaEstadoOrden(registro).procesar(resultado)
        mediador.notificar(
            mediador.ORDEN_PROCESADA,
            cartera=cartera,
            registro=registro,
        )
        historial.insert(0, registro)
        return registro

    @abstractmethod
    def validar_operacion(
        self,
        portfolio_service,
        cartera,
        activo_nombre: str,
        cantidad: float,
        precio: float,
        precios: dict[str, float],
    ) -> None:
        """Implementa la validación particular del lado de la orden."""

    @abstractmethod
    def actualizar_cartera(
        self,
        cartera,
        activo,
        registro: OrdenRegistro,
        resultado: ExecutionResult,
        precio: float,
    ) -> ExecutionResult:
        """Implementa los cambios particulares de compra o venta."""


class FlujoCompra(FlujoEjecucionOrdenTemplate):
    """Especializa la validación y actualización de una compra simulada."""

    def validar_operacion(
        self, portfolio_service, cartera, activo_nombre, cantidad, precio, precios
    ) -> None:
        portfolio_service.validar_compra(
            cartera, activo_nombre, cantidad, precio, precios
        )

    def actualizar_cartera(
        self, cartera, activo, registro, resultado, precio
    ) -> ExecutionResult:
        cartera.saldo_usd -= resultado.total
        cartera.registrar_compra(activo, registro.cantidad, precio)
        return resultado


class FlujoVenta(FlujoEjecucionOrdenTemplate):
    """Especializa la validación y actualización de una venta simulada."""

    def validar_operacion(
        self, portfolio_service, cartera, activo_nombre, cantidad, precio, precios
    ) -> None:
        portfolio_service.validar_venta(cartera, activo_nombre, cantidad)

    def actualizar_cartera(
        self, cartera, activo, registro, resultado, precio
    ) -> ExecutionResult:
        vendido = cartera.registrar_venta(activo.nombre, registro.cantidad)
        if not vendido:
            return ExecutionResult(
                status=EstadoOrden.RECHAZADA,
                message="La venta no pudo actualizar la cartera.",
                total=0.0,
            )
        cartera.saldo_usd += resultado.total
        return resultado
