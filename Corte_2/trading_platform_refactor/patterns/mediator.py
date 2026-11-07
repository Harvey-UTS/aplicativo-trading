"""Mediator: coordina eventos entre los servicios de trading."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable


class MediadorTrading:
    """Centraliza la comunicación sin acoplar directamente los servicios."""

    ANTES_ACTUALIZAR_CARTERA = "antes_actualizar_cartera"
    ORDEN_PROCESADA = "orden_procesada"
    RESTAURAR_CARTERA = "restaurar_cartera"

    def __init__(self) -> None:
        self._receptores: dict[str, list[Callable[..., object]]] = defaultdict(list)

    def registrar(self, evento: str, receptor: Callable[..., object]) -> None:
        if not evento or not callable(receptor):
            raise ValueError("El evento y su receptor son obligatorios.")
        if receptor not in self._receptores[evento]:
            self._receptores[evento].append(receptor)

    def notificar(self, evento: str, **datos: object) -> tuple[object, ...]:
        return tuple(receptor(**datos) for receptor in tuple(self._receptores[evento]))
