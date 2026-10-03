"""Composite para agrupar posiciones de una cartera de forma uniforme."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.portfolio import Cartera, Posicion


class ComponenteCartera(ABC):
    """Componente común para hojas y compuestos del árbol de cartera."""

    def __init__(self, nombre: str) -> None:
        self.nombre = nombre

    @abstractmethod
    def valor(self, precios: dict[str, float]) -> float:
        """Calcula el valor representado por el componente."""

    @abstractmethod
    def cantidad_componentes(self) -> int:
        """Devuelve el número de posiciones hoja contenidas."""


class PosicionActivo(ComponenteCartera):
    """Leaf: representa una posición individual de la cartera."""

    def __init__(self, posicion: "Posicion") -> None:
        super().__init__(posicion.nombre)
        self.posicion = posicion

    def valor(self, precios: dict[str, float]) -> float:
        precio = precios.get(self.posicion.nombre, self.posicion.precio_promedio)
        return self.posicion.cantidad * precio

    def cantidad_componentes(self) -> int:
        return 1


class GrupoActivos(ComponenteCartera):
    """Composite: agrupa posiciones y otros grupos de forma recursiva."""

    def __init__(self, nombre: str) -> None:
        super().__init__(nombre)
        self._componentes: list[ComponenteCartera] = []

    def agregar(self, componente: ComponenteCartera) -> None:
        if componente is self:
            raise ValueError("Un grupo no puede agregarse a sí mismo.")
        self._componentes.append(componente)

    def quitar(self, componente: ComponenteCartera) -> None:
        self._componentes.remove(componente)

    @property
    def componentes(self) -> tuple[ComponenteCartera, ...]:
        return tuple(self._componentes)

    def valor(self, precios: dict[str, float]) -> float:
        return sum(componente.valor(precios) for componente in self._componentes)

    def cantidad_componentes(self) -> int:
        return sum(componente.cantidad_componentes() for componente in self._componentes)


def construir_composite(cartera: "Cartera") -> GrupoActivos:
    """Construye el árbol Composite de las posiciones actuales de una cartera."""
    raiz = GrupoActivos(cartera.nombre)
    for posicion in cartera.activos:
        raiz.agregar(PosicionActivo(posicion))
    return raiz
