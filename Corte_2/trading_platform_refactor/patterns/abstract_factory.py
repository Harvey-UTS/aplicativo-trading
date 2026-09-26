"""Abstract Factory para familias de productos de cada exchange."""

from __future__ import annotations

from abc import ABC, abstractmethod

from patterns.bridge import (
    EjecutorOrden,
    ExchangeAExecutor,
    ExchangeBExecutor,
    ExchangeCExecutor,
)


class Mercado(ABC):
    """Producto abstracto de consulta de mercado."""

    @abstractmethod
    def consultar_precio(self, activo):
        pass


class FabricaExchange(ABC):
    """Abstract Factory."""

    @abstractmethod
    def crear_mercado(self) -> Mercado:
        pass

    @abstractmethod
    def crear_orden(self) -> EjecutorOrden:
        pass

    @property
    @abstractmethod
    def codigo(self) -> str:
        pass


class MercadoExchangeA:
    """Alias conceptual mantenido para el ejercicio anterior."""

    pass


class MercadoExchangeB:
    pass


class MercadoExchangeC:
    pass


class FabricaExchangeA(FabricaExchange):
    codigo = "A"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeAAdapter
        return ExchangeAAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeAExecutor()


class FabricaExchangeB(FabricaExchange):
    codigo = "B"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeBAdapter
        return ExchangeBAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeBExecutor()


class FabricaExchangeC(FabricaExchange):
    codigo = "C"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeCAdapter
        return ExchangeCAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeCExecutor()


# Compatibilidad explícita con los nombres históricos del avance.
from patterns.adapter import ExchangeAAdapter, ExchangeBAdapter, ExchangeCAdapter

MercadoExchangeA = ExchangeAAdapter
MercadoExchangeB = ExchangeBAdapter
MercadoExchangeC = ExchangeCAdapter
OrdenExchangeA = ExchangeAExecutor
OrdenExchangeB = ExchangeBExecutor
OrdenExchangeC = ExchangeCExecutor
