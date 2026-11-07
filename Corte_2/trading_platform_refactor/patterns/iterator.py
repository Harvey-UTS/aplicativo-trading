"""Iterator: recorre colecciones de trading sin exponer su almacenamiento."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class IteradorTrading(Iterator[T], Generic[T]):
    """Iterador secuencial sobre una instantánea estable de elementos."""

    def __init__(self, elementos: tuple[T, ...]) -> None:
        self._elementos = elementos
        self._indice = 0

    def __next__(self) -> T:
        if self._indice >= len(self._elementos):
            raise StopIteration
        elemento = self._elementos[self._indice]
        self._indice += 1
        return elemento


class ColeccionTrading(Iterable[T], Generic[T]):
    """Agregado iterable reutilizable para posiciones e historial de órdenes."""

    def __init__(self, elementos: Iterable[T]) -> None:
        self._elementos = tuple(elementos)

    def __iter__(self) -> IteradorTrading[T]:
        return IteradorTrading(self._elementos)

    def __len__(self) -> int:
        return len(self._elementos)
