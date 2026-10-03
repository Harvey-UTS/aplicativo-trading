"""Decorator para añadir trazabilidad a las consultas de mercado."""

from __future__ import annotations

from abc import ABC
from datetime import datetime

from models.asset import ActivoDigital
from patterns.abstract_factory import Mercado


class MercadoDecorator(Mercado, ABC):
    """Decorator base que conserva el contrato de Mercado."""

    def __init__(self, mercado: Mercado) -> None:
        self.mercado = mercado

    def consultar_precio(self, activo: ActivoDigital) -> float:
        return self.mercado.consultar_precio(activo)


class MercadoConAuditoria(MercadoDecorator):
    """Añade historial de consultas sin modificar el adapter original."""

    def __init__(self, mercado: Mercado, exchange: str) -> None:
        super().__init__(mercado)
        self.exchange = str(exchange).upper()
        self._consultas = 0
        self._ultima_consulta: dict[str, object] | None = None

    def consultar_precio(self, activo: ActivoDigital) -> float:
        precio = super().consultar_precio(activo)
        self._consultas += 1
        self._ultima_consulta = {
            "exchange": self.exchange,
            "activo": activo.nombre,
            "simbolo": activo.simbolo,
            "precio": float(precio),
            "timestamp": datetime.now(),
        }
        return float(precio)

    @property
    def consultas(self) -> int:
        return self._consultas

    @property
    def ultima_consulta(self) -> dict[str, object] | None:
        return None if self._ultima_consulta is None else dict(self._ultima_consulta)

    def resumen(self) -> dict[str, object]:
        return {
            "exchange": self.exchange,
            "consultas": self.consultas,
            "ultima_consulta": self.ultima_consulta,
        }
