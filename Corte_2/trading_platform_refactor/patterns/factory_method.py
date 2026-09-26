"""Factory Method para criptomonedas, tokens y NFT."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.asset import ActivoDigital, Criptomoneda, NFT, Token


class CreadorActivo(ABC):
    """Creator abstracto del patrón Factory Method."""

    @abstractmethod
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        pass

    def comprar_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float,
        simbolo: str | None = None,
    ):
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.comprar(cantidad)

    def vender_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float,
        simbolo: str | None = None,
    ):
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.vender(cantidad)

    def mostrar_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> dict[str, object]:
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.mostrar_informacion()


class CreadorCriptomoneda(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return Criptomoneda(nombre, precio, simbolo)


class CreadorToken(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return Token(nombre, precio, simbolo)


class CreadorNFT(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return NFT(nombre, precio, simbolo)
