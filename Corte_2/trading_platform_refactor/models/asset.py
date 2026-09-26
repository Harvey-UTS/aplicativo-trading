"""Modelos de activos digitales.

El módulo no conoce la consola ni la interfaz gráfica. Los métodos de
compra/venta devuelven información estructurada para que los servicios
puedan decidir qué hacer con ella.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ResultadoActivo:
    """Resultado descriptivo de una validación de operación."""

    accion: str
    activo: str
    cantidad: float
    precio: float
    total: float


class ActivoDigital(ABC):
    """Producto abstracto del Factory Method."""

    tipo: str = "ACTIVO"
    unidad: str = "unidades"

    def __init__(self, nombre: str, precio: float, simbolo: str | None = None) -> None:
        nombre = str(nombre).strip()
        if not nombre:
            raise ValueError("El nombre del activo es obligatorio.")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")

        self.nombre = nombre
        self.precio = float(precio)
        self.simbolo = (simbolo or self._generar_simbolo(nombre)).upper()

    @staticmethod
    def _generar_simbolo(nombre: str) -> str:
        limpio = "".join(ch for ch in nombre.upper() if ch.isalnum())
        return limpio[:10] or "ASSET"

    @abstractmethod
    def validar_cantidad(self, cantidad: float) -> None:
        """Valida las reglas de cantidad del tipo de activo."""

    def comprar(self, cantidad: float) -> ResultadoActivo:
        self.validar_cantidad(cantidad)
        return ResultadoActivo(
            accion="COMPRA",
            activo=self.nombre,
            cantidad=float(cantidad),
            precio=float(self.precio),
            total=float(self.precio * cantidad),
        )

    def vender(self, cantidad: float) -> ResultadoActivo:
        self.validar_cantidad(cantidad)
        return ResultadoActivo(
            accion="VENTA",
            activo=self.nombre,
            cantidad=float(cantidad),
            precio=float(self.precio),
            total=float(self.precio * cantidad),
        )

    def mostrar_informacion(self) -> dict[str, object]:
        return {
            "nombre": self.nombre,
            "simbolo": self.simbolo,
            "tipo": self.tipo,
            "precio": self.precio,
            "unidad": self.unidad,
        }


class Criptomoneda(ActivoDigital):
    """Producto concreto para criptomonedas."""

    tipo = "Criptomoneda"

    def validar_cantidad(self, cantidad: float) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")


class Token(ActivoDigital):
    """Producto concreto para tokens."""

    tipo = "Token"

    def validar_cantidad(self, cantidad: float) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")


class NFT(ActivoDigital):
    """Producto concreto para NFT unitarios."""

    tipo = "NFT"
    unidad = "unidad"

    def validar_cantidad(self, cantidad: float) -> None:
        if float(cantidad) != 1.0:
            raise ValueError("Un NFT se opera de uno en uno.")
