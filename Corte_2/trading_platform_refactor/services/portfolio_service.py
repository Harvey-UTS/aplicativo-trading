"""Servicio de gestión de carteras y riesgo."""

from __future__ import annotations

from patterns.prototype import clonar_cartera, crear_cartera_principal, crear_gestor_carteras
from models.portfolio import Cartera


class PortfolioService:
    USD_COP = 4000.0

    def __init__(self) -> None:
        principal = crear_cartera_principal("Cartera Principal", 50.0, 10.0)
        principal.recargar(5000.0, "USD")
        principal.capital_referencia_usd = principal.saldo_usd
        self._portfolios: dict[str, Cartera] = {principal.nombre: principal}
        self.gestor = crear_gestor_carteras(principal)

    def listar_carteras(self) -> list[Cartera]:
        return list(self._portfolios.values())

    def obtener_cartera(self, nombre: str) -> Cartera:
        try:
            return self._portfolios[nombre]
        except KeyError as exc:
            raise ValueError(f"No existe la cartera {nombre}.") from exc

    def recargar(self, nombre: str, monto: float, moneda: str) -> None:
        cartera = self.obtener_cartera(nombre)
        cartera.recargar(monto, moneda)

    def clonar_cartera(self, nombre: str, porcentaje: float) -> Cartera:
        if nombre in self._portfolios:
            raise ValueError("Ya existe una cartera con ese nombre.")
        clon = clonar_cartera(self.gestor, nombre, porcentaje)
        self._portfolios[clon.nombre] = clon
        return clon

    def configurar_riesgo(
        self,
        nombre: str,
        exposicion: float,
        perdida: float,
        stop_loss: float,
        take_profit: float,
    ) -> None:
        cartera = self.obtener_cartera(nombre)
        cartera.configurar_riesgo(exposicion, perdida, stop_loss, take_profit)

    def obtener_balance(self, nombre: str, precios: dict[str, float]) -> dict:
        cartera = self.obtener_cartera(nombre)
        return cartera.resumen(precios)

    def validar_compra(self, cartera: Cartera, activo_nombre: str, cantidad: float, precio: float, precios: dict[str, float]) -> None:
        total = cantidad * precio
        if total > cartera.saldo_usd + 1e-9:
            raise ValueError("Saldo USD insuficiente para ejecutar la compra simulada.")

        precios_actuales = dict(precios)
        precios_actuales[activo_nombre] = precio
        actual = cartera.valor_total_usd(precios_actuales)
        nuevo_valor_activos = cartera.valor_activos(precios_actuales) + total
        exposicion = (nuevo_valor_activos / (actual + total) * 100.0) if actual + total else 0.0
        if exposicion > cartera.limite_exposicion + 1e-9:
            raise ValueError(
                f"La compra supera el límite de exposición ({cartera.limite_exposicion:.2f}%)."
            )

    def validar_venta(self, cartera: Cartera, activo_nombre: str, cantidad: float) -> None:
        posicion = cartera.buscar_posicion(activo_nombre)
        if posicion is None or cantidad > posicion.cantidad + 1e-12:
            raise ValueError("La cartera no tiene suficiente cantidad del activo.")

    def evaluar_riesgo(self, cartera: Cartera, precios: dict[str, float]) -> dict[str, object]:
        resumen = cartera.resumen(precios)
        drawdown = float(resumen["drawdown_pct"])
        exposure = float(resumen["exposicion_pct"])
        alertas: list[str] = []
        if exposure > cartera.limite_exposicion:
            alertas.append("Exposición por encima del límite configurado.")
        if drawdown > cartera.limite_perdida:
            alertas.append("Pérdida simulada por encima del límite configurado.")
        return {
            "exposicion_pct": exposure,
            "drawdown_pct": drawdown,
            "stop_loss": cartera.stop_loss,
            "take_profit": cartera.take_profit,
            "alertas": alertas,
        }
