"""Observer: notifica a los suscriptores cuando se consulta un precio."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EventoPrecioMercado:
    """Evento inmutable que describe una actualización consultada del mercado."""

    exchange: str
    activo: str
    simbolo: str
    precio: float
    fecha: datetime


class ObservadorMercado(Protocol):
    """Contrato que deben implementar los componentes interesados en el mercado."""

    def actualizar(self, evento: EventoPrecioMercado) -> None:
        """Recibe una notificación de precio."""


class PublicadorMercado:
    """Mantiene suscriptores y distribuye eventos sin conocer sus implementaciones."""

    def __init__(self) -> None:
        self._observadores: list[ObservadorMercado] = []
        self._lock = RLock()

    def suscribir(self, observador: ObservadorMercado) -> None:
        if not callable(getattr(observador, "actualizar", None)):
            raise TypeError("El observador debe implementar actualizar(evento).")
        with self._lock:
            if observador not in self._observadores:
                self._observadores.append(observador)

    def cancelar_suscripcion(self, observador: ObservadorMercado) -> bool:
        with self._lock:
            try:
                self._observadores.remove(observador)
            except ValueError:
                return False
            return True

    def notificar(self, evento: EventoPrecioMercado) -> tuple[Exception, ...]:
        """Notifica sobre una instantánea de suscriptores y aísla fallos individuales."""
        with self._lock:
            observadores = tuple(self._observadores)

        errores: list[Exception] = []
        for observador in observadores:
            try:
                observador.actualizar(evento)
            except Exception as exc:  # Un suscriptor defectuoso no debe detener el mercado.
                errores.append(exc)
                logger.exception("Error notificando a un observador del mercado.")
        return tuple(errores)

    @property
    def cantidad_suscriptores(self) -> int:
        with self._lock:
            return len(self._observadores)
