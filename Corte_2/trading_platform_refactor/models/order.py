"""Modelos de órdenes e historial."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class TipoOrden(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP LOSS"


class LadoOrden(str, Enum):
    COMPRA = "COMPRA"
    VENTA = "VENTA"


class EstadoOrden(str, Enum):
    EJECUTADA = "EJECUTADA"
    PENDIENTE = "PENDIENTE"
    RECHAZADA = "RECHAZADA"


@dataclass(slots=True)
class ExecutionResult:
    """Resultado normalizado de un executor de exchange."""

    status: EstadoOrden
    message: str
    total: float = 0.0


@dataclass(slots=True)
class OrdenRegistro:
    """Registro inmutable de una operación simulada."""

    id: str = field(default_factory=lambda: uuid4().hex[:10].upper())
    timestamp: datetime = field(default_factory=datetime.now)
    tipo: TipoOrden = TipoOrden.MARKET
    lado: LadoOrden = LadoOrden.COMPRA
    exchange: str = "A"
    cartera: str = "Cartera Principal"
    activo: str = ""
    cantidad: float = 0.0
    precio: float = 0.0
    precio_objetivo: float | None = None
    estado: EstadoOrden = EstadoOrden.PENDIENTE
    total: float = 0.0
    mensaje: str = ""

    def to_row(self) -> list[str]:
        objetivo = "—" if self.precio_objetivo is None else f"${self.precio_objetivo:,.2f}"
        return [
            self.id,
            self.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            self.tipo.value,
            self.lado.value,
            self.exchange,
            self.cartera,
            self.activo,
            f"{self.cantidad:g}",
            f"${self.precio:,.2f}",
            objetivo,
            self.estado.value,
            f"${self.total:,.2f}",
        ]
