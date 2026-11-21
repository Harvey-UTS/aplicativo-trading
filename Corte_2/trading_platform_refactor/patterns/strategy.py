"""Strategy: algoritmos intercambiables para evaluar el riesgo de una cartera."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.portfolio import Cartera


class EstrategiaRiesgo(ABC):
    """Contrato común para las políticas de evaluación de riesgo."""

    @abstractmethod
    def evaluar(
        self,
        cartera: Cartera,
        exposicion_pct: float,
        drawdown_pct: float,
    ) -> dict[str, list[str]]:
        """Devuelve alertas y advertencias sin modificar la cartera."""


class EstrategiaRiesgoConfigurada(EstrategiaRiesgo):
    """Aplica exactamente los límites configurados en la cartera."""

    def evaluar(
        self,
        cartera: Cartera,
        exposicion_pct: float,
        drawdown_pct: float,
    ) -> dict[str, list[str]]:
        alertas: list[str] = []
        if exposicion_pct > cartera.limite_exposicion:
            alertas.append("Exposición por encima del límite configurado.")
        if drawdown_pct > cartera.limite_perdida:
            alertas.append("Pérdida simulada por encima del límite configurado.")
        return {"alertas": alertas, "advertencias": []}


class EstrategiaRiesgoPreventiva(EstrategiaRiesgo):
    """Añade advertencias al alcanzar el 80 % de los límites configurados."""

    FACTOR_PREVENTIVO = 0.80

    def evaluar(
        self,
        cartera: Cartera,
        exposicion_pct: float,
        drawdown_pct: float,
    ) -> dict[str, list[str]]:
        resultado = EstrategiaRiesgoConfigurada().evaluar(
            cartera, exposicion_pct, drawdown_pct
        )
        advertencias: list[str] = []

        limite_exposicion = float(cartera.limite_exposicion)
        limite_perdida = float(cartera.limite_perdida)

        if (
            limite_exposicion > 0
            and self.FACTOR_PREVENTIVO * limite_exposicion <= exposicion_pct <= limite_exposicion
        ):
            advertencias.append("La exposición se aproxima al límite configurado.")
        if (
            limite_perdida > 0
            and self.FACTOR_PREVENTIVO * limite_perdida <= drawdown_pct <= limite_perdida
        ):
            advertencias.append("La pérdida simulada se aproxima al límite configurado.")

        resultado["advertencias"] = advertencias
        return resultado
