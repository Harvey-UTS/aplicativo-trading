"""Memento: conserva y restaura estados completos de una cartera."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class CarteraMemento:
    """Instantánea privada del estado de una cartera en un momento dado."""

    __slots__ = ("_estado", "motivo", "creado_en")

    def __init__(self, cartera, motivo: str = "Punto de control") -> None:
        self._estado = deepcopy(vars(cartera))
        self.motivo = motivo
        self.creado_en = datetime.now()

    def restaurar(self, cartera) -> None:
        """Restaura el contenido sin reemplazar la instancia de la cartera."""
        estado = deepcopy(self._estado)
        vars(cartera).clear()
        vars(cartera).update(estado)


class HistorialCartera:
    """Caretaker que limita y administra las instantáneas de una cartera."""

    def __init__(self, capacidad: int = 20) -> None:
        if capacidad < 1:
            raise ValueError("La capacidad debe ser al menos uno.")
        self._capacidad = capacidad
        self._estados: list[CarteraMemento] = []

    def guardar(self, cartera, motivo: str = "Punto de control") -> CarteraMemento:
        memento = CarteraMemento(cartera, motivo)
        self._estados.append(memento)
        del self._estados[:-self._capacidad]
        return memento

    def deshacer(self, cartera) -> CarteraMemento:
        if not self._estados:
            raise ValueError("No hay estados guardados para restaurar.")
        memento = self._estados.pop()
        memento.restaurar(cartera)
        return memento

    def listar(self) -> tuple[CarteraMemento, ...]:
        return tuple(self._estados)

    def __len__(self) -> int:
        return len(self._estados)
