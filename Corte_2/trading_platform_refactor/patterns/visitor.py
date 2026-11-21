"""Visitor: agrega operaciones de ficha técnica sin repartirlas entre los activos."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.asset import ActivoDigital, Criptomoneda, NFT, Token


class VisitanteActivo(ABC):
    """Interfaz para operaciones que necesitan distinguir el tipo de activo."""

    @abstractmethod
    def visitar_criptomoneda(self, activo: Criptomoneda) -> dict[str, object]:
        pass

    @abstractmethod
    def visitar_token(self, activo: Token) -> dict[str, object]:
        pass

    @abstractmethod
    def visitar_nft(self, activo: NFT) -> dict[str, object]:
        pass


class FichaTecnicaActivoVisitor(VisitanteActivo):
    """Construye una ficha uniforme con las características de cada activo."""

    @staticmethod
    def _datos_base(
        activo: ActivoDigital,
        naturaleza: str,
        fraccionable: bool,
        regla_cantidad: str,
    ) -> dict[str, object]:
        return {
            "nombre": activo.nombre,
            "simbolo": activo.simbolo,
            "tipo": activo.tipo,
            "precio": float(activo.precio),
            "unidad": activo.unidad,
            "naturaleza": naturaleza,
            "fraccionable": fraccionable,
            "regla_cantidad": regla_cantidad,
        }

    def visitar_criptomoneda(self, activo: Criptomoneda) -> dict[str, object]:
        return self._datos_base(
            activo,
            naturaleza="Criptoactivo fungible",
            fraccionable=True,
            regla_cantidad="Cantidad positiva; admite fracciones.",
        )

    def visitar_token(self, activo: Token) -> dict[str, object]:
        return self._datos_base(
            activo,
            naturaleza="Token digital fungible",
            fraccionable=True,
            regla_cantidad="Cantidad positiva; admite fracciones.",
        )

    def visitar_nft(self, activo: NFT) -> dict[str, object]:
        return self._datos_base(
            activo,
            naturaleza="Activo digital no fungible",
            fraccionable=False,
            regla_cantidad="Se negocia una unidad por operación.",
        )
