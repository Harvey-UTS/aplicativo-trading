"""Builder que ensambla los patrones de la plataforma."""

from __future__ import annotations

from dataclasses import dataclass

from models.asset import ActivoDigital
from models.portfolio import Cartera
from patterns.abstract_factory import (
    FabricaExchange,
    FabricaExchangeA,
    FabricaExchangeB,
    FabricaExchangeC,
)
from patterns.bridge import OrdenLimit, OrdenMarket, OrdenStopLoss, OrdenTrading
from patterns.factory_method import (
    CreadorCriptomoneda,
    CreadorNFT,
    CreadorToken,
)
from patterns.prototype import GestorCarteras
from patterns.singleton import ExchangeConnectionManager


@dataclass(slots=True)
class PlataformaTrading:
    """Producto final ensamblado por Builder."""

    sistema_ordenes: ExchangeConnectionManager | None = None
    creador: object | None = None
    activo: ActivoDigital | None = None
    fabrica_exchange: FabricaExchange | None = None
    cartera: Cartera | None = None
    gestor_carteras: GestorCarteras | None = None
    orden: OrdenTrading | None = None

    @property
    def exchange(self) -> str:
        if self.fabrica_exchange is None:
            return ""
        return self.fabrica_exchange.codigo


class PlataformaTradingBuilder:
    """Builder fluido para escenarios de trading completos."""

    def __init__(self) -> None:
        self.sistema_ordenes: ExchangeConnectionManager | None = None
        self.creador = None
        self.activo: ActivoDigital | None = None
        self.fabrica_exchange: FabricaExchange | None = None
        self.cartera: Cartera | None = None
        self.gestor_carteras: GestorCarteras | None = None
        self.orden: OrdenTrading | None = None

    def configurar_singleton(self) -> "PlataformaTradingBuilder":
        self.sistema_ordenes = ExchangeConnectionManager()
        return self

    def configurar_operacion(
        self,
        tipo_activo: str,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> "PlataformaTradingBuilder":
        creadores = {
            "CRIPTO": CreadorCriptomoneda,
            "CRYPTO": CreadorCriptomoneda,
            "TOKEN": CreadorToken,
            "NFT": CreadorNFT,
        }
        key = tipo_activo.upper().strip()
        aliases = {
            "CRIPTOMONEDA": "CRIPTO",
            "CRYPTOCURRENCY": "CRIPTO",
            "TOKEN": "TOKEN",
            "NFT": "NFT",
            "CRYPTO": "CRIPTO",
        }
        key = aliases.get(key, key)
        creador_cls = creadores.get(key)
        if creador_cls is None:
            raise ValueError("Tipo de activo no válido. Use CRIPTO, TOKEN o NFT.")
        self.creador = creador_cls()
        self.activo = self.creador.crear_activo(nombre, precio, simbolo)
        return self

    def configurar_exchange(
        self,
        exchange: str | FabricaExchange,
    ) -> "PlataformaTradingBuilder":
        if isinstance(exchange, FabricaExchange):
            self.fabrica_exchange = exchange
            return self

        factories = {
            "A": FabricaExchangeA,
            "B": FabricaExchangeB,
            "C": FabricaExchangeC,
        }
        factory_cls = factories.get(str(exchange).upper().strip())
        if factory_cls is None:
            raise ValueError("Exchange no válido. Use A, B o C.")
        self.fabrica_exchange = factory_cls()
        return self

    def configurar_cartera(
        self,
        cartera: Cartera,
        gestor_carteras: GestorCarteras | None = None,
    ) -> "PlataformaTradingBuilder":
        self.cartera = cartera
        self.gestor_carteras = gestor_carteras
        return self

    def configurar_orden(
        self,
        tipo_orden: str,
        precio_objetivo: float | None = None,
    ) -> "PlataformaTradingBuilder":
        if self.fabrica_exchange is None:
            raise ValueError("Primero debe configurar el exchange.")

        executor = self.fabrica_exchange.crear_orden()
        key = tipo_orden.upper().replace("-", " ").strip()
        if key == "MARKET":
            self.orden = OrdenMarket(executor)
        elif key == "LIMIT":
            if precio_objetivo is None:
                raise ValueError("La orden Limit requiere un precio objetivo.")
            self.orden = OrdenLimit(executor, precio_objetivo)
        elif key in {"STOP LOSS", "STOPLOSS"}:
            if precio_objetivo is None:
                raise ValueError("La orden Stop Loss requiere un precio de activación.")
            self.orden = OrdenStopLoss(executor, precio_objetivo)
        else:
            raise ValueError("Tipo de orden no válido.")
        return self

    def build(self) -> PlataformaTrading:
        if self.sistema_ordenes is None:
            self.configurar_singleton()
        if self.fabrica_exchange is None:
            raise ValueError("Debe configurar un exchange.")
        if self.cartera is None:
            raise ValueError("Debe configurar una cartera.")

        return PlataformaTrading(
            sistema_ordenes=self.sistema_ordenes,
            creador=self.creador,
            activo=self.activo,
            fabrica_exchange=self.fabrica_exchange,
            cartera=self.cartera,
            gestor_carteras=self.gestor_carteras,
            orden=self.orden,
        )
