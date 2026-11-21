"""Servicio principal de compra, venta, órdenes y ejecución."""

from __future__ import annotations

from models.order import EstadoOrden, LadoOrden, OrdenRegistro, TipoOrden
from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from patterns.builder import PlataformaTrading, PlataformaTradingBuilder
from patterns.iterator import ColeccionTrading
from patterns.mediator import MediadorTrading
from patterns.template_method import FlujoCompra, FlujoVenta


class TradingService:
    """Orquesta la construcción y ejecución de órdenes mediante servicios y patrones."""

    def __init__(self, market_service: MarketService, portfolio_service: PortfolioService) -> None:
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self._history: list[OrdenRegistro] = []
        self._mediador = MediadorTrading()
        self._flujos_ejecucion = {
            LadoOrden.COMPRA: FlujoCompra(),
            LadoOrden.VENTA: FlujoVenta(),
        }
        self.portfolio_service.vincular_mediador(self._mediador)

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
        try:
            flujo = self._flujos_ejecucion[registro.lado]
        except KeyError as exc:
            raise ValueError("El lado de la orden no tiene un flujo de ejecución válido.") from exc
        return flujo.ejecutar(
            market_service=self.market_service,
            portfolio_service=self.portfolio_service,
            mediador=self._mediador,
            plataforma=platform,
            registro=registro,
            historial=self._history,
        )

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

    def iterar_historial(self) -> ColeccionTrading[OrdenRegistro]:
        """Entrega el historial mediante el patrón Iterator."""
        return ColeccionTrading(self._history)

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
