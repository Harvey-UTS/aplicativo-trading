"""Facade: punto de acceso unificado a los servicios de la plataforma."""

from __future__ import annotations

from models.asset import ActivoDigital
from models.order import OrdenRegistro
from models.portfolio import Cartera
from patterns.builder import PlataformaTrading
from patterns.singleton import ExchangeConnectionManager
from services.market_service import MarketRow, MarketService
from services.portfolio_service import PortfolioService
from services.trading_service import TradingService


class TradingPlatformFacade:
    """Simplifica la interacción con mercado, carteras, órdenes y riesgo.

    La interfaz gráfica utiliza esta fachada en lugar de crear y coordinar los
    servicios por separado. La lógica detallada continúa encapsulada en cada
    servicio especializado.
    """

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self._manager = manager or ExchangeConnectionManager()
        self._market = MarketService(self._manager)
        self._portfolios = PortfolioService()
        self._trading = TradingService(self._market, self._portfolios)

    @property
    def manager(self) -> ExchangeConnectionManager:
        """Expone el gestor compartido para administrar el ciclo de vida local."""
        return self._manager

    def iniciar(self) -> None:
        """Inicia la actualización local de precios simulados."""
        self._manager.start()

    def cerrar(self) -> None:
        """Detiene la actualización local al cerrar la aplicación."""
        self._manager.stop()

    # Mercado y activos
    def actualizar_mercado(self) -> None:
        self._market.actualizar_mercado()

    def crear_activo(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return self._market.crear_activo(tipo, nombre, precio, simbolo)

    def obtener_activos(self) -> list[ActivoDigital]:
        return self._market.obtener_activos()

    def obtener_activo(self, nombre: str) -> ActivoDigital:
        return self._market.obtener_activo(nombre)

    def obtener_precio(self, activo: ActivoDigital | str, exchange: str = "A") -> float:
        return self._market.obtener_precio(activo, exchange)

    def obtener_auditoria_mercado(self, exchange: str) -> dict[str, object]:
        return self._market.obtener_auditoria_mercado(exchange)

    def tabla_mercado(
        self,
        previous: dict[tuple[str, str], float] | None = None,
    ) -> list[MarketRow]:
        return self._market.tabla_mercado(previous)

    # Carteras y control de riesgo
    def listar_carteras(self) -> list[Cartera]:
        return self._portfolios.listar_carteras()

    def obtener_cartera(self, nombre: str) -> Cartera:
        return self._portfolios.obtener_cartera(nombre)

    def recargar_cartera(self, nombre: str, monto: float, moneda: str) -> None:
        self._portfolios.recargar(nombre, monto, moneda)

    def clonar_cartera(self, nombre: str, porcentaje: float) -> Cartera:
        return self._portfolios.clonar_cartera(nombre, porcentaje)

    def configurar_riesgo(
        self,
        nombre: str,
        exposicion: float,
        perdida: float,
        stop_loss: float,
        take_profit: float,
    ) -> None:
        self._portfolios.configurar_riesgo(
            nombre, exposicion, perdida, stop_loss, take_profit
        )

    def obtener_balance(self, nombre: str, precios: dict[str, float]) -> dict:
        return self._portfolios.obtener_balance(nombre, precios)

    def evaluar_riesgo(self, cartera: Cartera, precios: dict[str, float]) -> dict[str, object]:
        return self._portfolios.evaluar_riesgo(cartera, precios)

    # Órdenes y simulación de operaciones
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
        return self._trading.crear_orden(
            tipo_orden,
            lado,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
            precio_objetivo,
        )

    def ejecutar_orden(
        self,
        plataforma: PlataformaTrading,
        registro: OrdenRegistro,
    ) -> OrdenRegistro:
        return self._trading.ejecutar_orden(plataforma, registro)

    def crear_y_ejecutar_orden(
        self,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> OrdenRegistro:
        """Coordina la construcción, validación y ejecución de una orden."""
        plataforma, registro = self.crear_orden(
            tipo_orden,
            lado,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
            precio_objetivo,
        )
        return self.ejecutar_orden(plataforma, registro)

    def comprar_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        return self._trading.comprar_activo(
            exchange, activo_nombre, cantidad, cartera_nombre
        )

    def vender_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        return self._trading.vender_activo(
            exchange, activo_nombre, cantidad, cartera_nombre
        )

    def historial_ordenes(self) -> list[OrdenRegistro]:
        return self._trading.historial()
