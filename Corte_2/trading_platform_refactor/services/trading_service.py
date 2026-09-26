"""Servicio principal de compra, venta, órdenes y ejecución."""

from __future__ import annotations

from models.order import EstadoOrden, LadoOrden, OrdenRegistro, TipoOrden
from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from patterns.builder import PlataformaTrading, PlataformaTradingBuilder


class TradingService:
    """Orquesta Builder, Bridge, Adapter, Abstract Factory, Prototype y Singleton."""

    def __init__(self, market_service: MarketService, portfolio_service: PortfolioService) -> None:
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self._history: list[OrdenRegistro] = []

    def crear_orden(
        self,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> tuple[PlataformaTrading, OrdenRegistro]:
        activo = self.market_service.obtener_activo(activo_nombre)
        cartera = self.portfolio_service.obtener_cartera(cartera_nombre)
        exchange = exchange.upper().strip()
        lado_enum = LadoOrden(lado.upper().strip())
        tipo_enum = self._parse_tipo(tipo_orden)

        builder = (
            PlataformaTradingBuilder()
            .configurar_singleton()
            .configurar_operacion(activo.tipo, activo.nombre, activo.precio, activo.simbolo)
            .configurar_exchange(exchange)
            .configurar_cartera(cartera, self.portfolio_service.gestor)
            .configurar_orden(tipo_enum.value, precio_objetivo)
        )
        platform = builder.build()

        registro = OrdenRegistro(
            tipo=tipo_enum,
            lado=lado_enum,
            exchange=exchange,
            cartera=cartera.nombre,
            activo=activo.nombre,
            cantidad=float(cantidad),
            precio=0.0,
            precio_objetivo=precio_objetivo,
        )
        return platform, registro

    def ejecutar_orden(self, platform: PlataformaTrading, registro: OrdenRegistro) -> OrdenRegistro:
        if platform.orden is None or platform.activo is None or platform.cartera is None:
            raise ValueError("La plataforma de trading no tiene una orden completa configurada.")

        activo = platform.activo
        cartera = platform.cartera
        precio = self.market_service.obtener_precio(activo, registro.exchange)
        registro.precio = precio
        activo.precio = precio

        precios_cartera = {
            p.nombre: self.market_service.obtener_precio(p.nombre, registro.exchange)
            for p in cartera.activos
        }
        precios_cartera[activo.nombre] = precio

        if registro.lado == LadoOrden.COMPRA:
            self.portfolio_service.validar_compra(
                cartera,
                activo.nombre,
                registro.cantidad,
                precio,
                precios_cartera,
            )
        else:
            self.portfolio_service.validar_venta(cartera, activo.nombre, registro.cantidad)

        resultado = platform.orden.ejecutar(
            activo,
            registro.lado,
            registro.cantidad,
            precio,
        )
        registro.estado = resultado.status
        registro.total = resultado.total
        registro.mensaje = resultado.message

        if resultado.status == EstadoOrden.EJECUTADA:
            if registro.lado == LadoOrden.COMPRA:
                cartera.saldo_usd -= resultado.total
                cartera.registrar_compra(activo, registro.cantidad, precio)
            else:
                vendido = cartera.registrar_venta(activo.nombre, registro.cantidad)
                if not vendido:
                    registro.estado = EstadoOrden.RECHAZADA
                    registro.mensaje = "La venta no pudo actualizar la cartera."
                    registro.total = 0.0
                else:
                    cartera.saldo_usd += resultado.total

        self._history.insert(0, registro)
        return registro

    def comprar_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        platform, registro = self.crear_orden(
            TipoOrden.MARKET.value,
            LadoOrden.COMPRA.value,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
        )
        return self.ejecutar_orden(platform, registro)

    def vender_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        platform, registro = self.crear_orden(
            TipoOrden.MARKET.value,
            LadoOrden.VENTA.value,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
        )
        return self.ejecutar_orden(platform, registro)

    def historial(self) -> list[OrdenRegistro]:
        return list(self._history)

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
