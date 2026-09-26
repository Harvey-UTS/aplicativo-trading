"""Modelo de cartera y posiciones.

El modelo conserva los nombres y responsabilidades centrales del ejercicio
Prototype original, pero ya no imprime resultados ni solicita datos.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True)
class Posicion:
    nombre: str
    cantidad: float
    precio_promedio: float

    @property
    def valor_invertido(self) -> float:
        return self.cantidad * self.precio_promedio


class Cartera:
    """Prototipo concreto de cartera."""

    def __init__(self, nombre: str = "Cartera Base") -> None:
        self.nombre = nombre
        self.activos: list[Posicion] = []
        self.saldo_cop = 0.0
        self.saldo_usd = 0.0
        self.limite_exposicion = 100.0
        self.limite_perdida = 10.0
        self.stop_loss = 5.0
        self.take_profit = 10.0
        self.porcentaje_recargado = 100.0
        self.capital_referencia_usd = 0.0

    def clonar(self) -> "Cartera":
        """Clonación profunda del Prototype."""
        return deepcopy(self)

    def registrar_compra(self, activo, cantidad: float, precio: float) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        posicion = self.buscar_posicion(activo.nombre)
        if posicion is None:
            self.activos.append(Posicion(activo.nombre, cantidad, precio))
            return

        costo_anterior = posicion.cantidad * posicion.precio_promedio
        costo_nuevo = cantidad * precio
        cantidad_total = posicion.cantidad + cantidad
        posicion.precio_promedio = (costo_anterior + costo_nuevo) / cantidad_total
        posicion.cantidad = cantidad_total

    def registrar_venta(self, nombre: str, cantidad: float) -> bool:
        if cantidad <= 0:
            return False

        posicion = self.buscar_posicion(nombre)
        if posicion is None or cantidad > posicion.cantidad:
            return False

        posicion.cantidad -= cantidad
        if posicion.cantidad <= 1e-12:
            self.activos.remove(posicion)
        return True

    def buscar_posicion(self, nombre: str) -> Posicion | None:
        for posicion in self.activos:
            if posicion.nombre == nombre:
                return posicion
        return None

    def recargar(self, monto: float, moneda: str) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")

        moneda = moneda.upper().strip()
        if moneda == "COP":
            self.saldo_cop += monto
        elif moneda == "USD":
            self.saldo_usd += monto
            self.capital_referencia_usd += monto
        else:
            raise ValueError("Moneda no válida. Use COP o USD.")

    def configurar_riesgo(
        self,
        limite_exposicion: float,
        limite_perdida: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> None:
        valores = [limite_exposicion, limite_perdida]
        if any(value < 0 or value > 100 for value in valores):
            raise ValueError("Los límites deben estar entre 0% y 100%.")

        self.limite_exposicion = float(limite_exposicion)
        self.limite_perdida = float(limite_perdida)
        if stop_loss is not None:
            if stop_loss < 0 or stop_loss > 100:
                raise ValueError("Stop Loss debe estar entre 0% y 100%.")
            self.stop_loss = float(stop_loss)
        if take_profit is not None:
            if take_profit < 0:
                raise ValueError("Take Profit no puede ser negativo.")
            self.take_profit = float(take_profit)

    def valor_activos(self, precios: dict[str, float]) -> float:
        return sum(
            posicion.cantidad * precios.get(posicion.nombre, posicion.precio_promedio)
            for posicion in self.activos
        )

    def valor_total_usd(self, precios: dict[str, float]) -> float:
        return self.saldo_usd + self.valor_activos(precios)

    def exposicion_usd(self, precios: dict[str, float]) -> float:
        return self.valor_activos(precios)

    def drawdown_pct(self, precios: dict[str, float]) -> float:
        actual = self.valor_total_usd(precios)
        referencia = self.capital_referencia_usd
        if referencia <= 0:
            return 0.0
        return max(0.0, (referencia - actual) / referencia * 100.0)

    def resumen(self, precios: dict[str, float]) -> dict[str, float | int]:
        activos_valor = self.valor_activos(precios)
        total = self.saldo_usd + activos_valor
        return {
            "saldo_usd": self.saldo_usd,
            "saldo_cop": self.saldo_cop,
            "valor_activos": activos_valor,
            "valor_total": total,
            "cantidad_activos": len(self.activos),
            "exposicion_pct": (activos_valor / total * 100.0) if total else 0.0,
            "drawdown_pct": self.drawdown_pct(precios),
        }
