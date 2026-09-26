"""Servicio de mercado: única puerta de entrada a precios y activos."""

from __future__ import annotations

from dataclasses import dataclass

from models.asset import ActivoDigital
from patterns.abstract_factory import FabricaExchangeA, FabricaExchangeB, FabricaExchangeC
from patterns.factory_method import CreadorCriptomoneda, CreadorNFT, CreadorToken
from patterns.singleton import ExchangeConnectionManager


@dataclass(slots=True)
class MarketRow:
    activo: str
    simbolo: str
    tipo: str
    exchange: str
    precio: float
    variacion: float


class MarketService:
    """Coordina Factory Method, Abstract Factory, Adapter y Singleton."""

    USD_COP = 4000.0

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()
        self.factories = {
            "A": FabricaExchangeA(),
            "B": FabricaExchangeB(),
            "C": FabricaExchangeC(),
        }
        self.creators = {
            "CRIPTO": CreadorCriptomoneda(),
            "CRYPTO": CreadorCriptomoneda(),
            "TOKEN": CreadorToken(),
            "NFT": CreadorNFT(),
        }
        self._assets: dict[str, ActivoDigital] = {}
        self._seed_assets()

    def _seed_assets(self) -> None:
        initial = [
            ("CRIPTO", "Bitcoin", 60000.0, "BTC"),
            ("CRIPTO", "Ethereum", 3000.0, "ETH"),
            ("TOKEN", "Chainlink", 15.0, "LINK"),
            ("TOKEN", "Polygon", 0.5, "MATIC"),
            ("NFT", "CryptoArt #001", 2500.0, "CRYPTOART001"),
            ("CRIPTO", "Solana", 145.2, "SOL"),
        ]
        for kind, name, price, symbol in initial:
            self._assets[name] = self.creators[kind].crear_activo(name, price, symbol)

    def crear_activo(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        kind = tipo.upper().strip()
        creator = self.creators.get(kind)
        if creator is None:
            raise ValueError("Tipo de activo no válido.")
        if nombre in self._assets:
            raise ValueError("Ya existe un activo con ese nombre.")
        if precio <= 0:
            raise ValueError("El precio inicial debe ser mayor que cero.")

        activo = creator.crear_activo(nombre, precio, simbolo)
        self._assets[activo.nombre] = activo
        return activo

    def obtener_activos(self) -> list[ActivoDigital]:
        return list(self._assets.values())

    def obtener_activo(self, nombre: str) -> ActivoDigital:
        try:
            return self._assets[nombre]
        except KeyError as exc:
            raise ValueError(f"No existe el activo {nombre}.") from exc

    def obtener_precio(self, activo: ActivoDigital | str, exchange: str = "A") -> float:
        if isinstance(activo, str):
            activo = self.obtener_activo(activo)
        factory = self.factories.get(str(exchange).upper())
        if factory is None:
            raise ValueError("Exchange no válido.")
        mercado = factory.crear_mercado()
        try:
            precio = mercado.consultar_precio(activo)
        except KeyError:
            # Los activos personalizados todavía pueden cotizar con el precio
            # inicial mientras el simulador no tenga un ticker específico.
            precio = activo.precio
        self.manager.set_cached_price(str(exchange).upper(), f"{activo.simbolo}/USDT", precio)
        activo.precio = float(precio)
        return float(precio)

    def actualizar_mercado(self) -> None:
        """Actualiza el cache de todos los activos con sus adapters."""
        self.manager.simulate_market_update()
        for exchange in self.factories:
            for activo in self._assets.values():
                try:
                    self.obtener_precio(activo, exchange)
                except (ValueError, KeyError):
                    continue

    def tabla_mercado(self, previous: dict[tuple[str, str], float] | None = None) -> list[MarketRow]:
        previous = previous or {}
        rows: list[MarketRow] = []
        for exchange in self.factories:
            for activo in self._assets.values():
                precio = self.obtener_precio(activo, exchange)
                key = (exchange, activo.nombre)
                old = previous.get(key, precio)
                variacion = ((precio - old) / old * 100.0) if old else 0.0
                rows.append(MarketRow(activo.nombre, activo.simbolo, activo.tipo, exchange, precio, variacion))
        return rows
