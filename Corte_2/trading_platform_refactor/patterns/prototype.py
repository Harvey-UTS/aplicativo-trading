"""Prototype para clonar carteras y sus configuraciones."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.portfolio import Cartera


class Prototype(ABC):
    @abstractmethod
    def clonar(self):
        pass


class GestorCarteras:
    """Administrador de copias del prototipo principal."""

    def __init__(self) -> None:
        self.prototipo: Cartera | None = None

    def establecer_prototipo(self, cartera: Cartera) -> None:
        self.prototipo = cartera

    def crear_copia(self, nombre: str, porcentaje_recargado: float = 100.0) -> Cartera:
        if self.prototipo is None:
            raise ValueError("No existe un prototipo de cartera configurado.")

        nueva = self.prototipo.clonar()
        nueva.nombre = nombre
        nueva.porcentaje_recargado = porcentaje_recargado
        factor = porcentaje_recargado / 100.0
        nueva.saldo_cop = self.prototipo.saldo_cop * factor
        nueva.saldo_usd = self.prototipo.saldo_usd * factor
        nueva.capital_referencia_usd = self.prototipo.capital_referencia_usd * factor
        return nueva


def crear_cartera_principal(
    nombre: str = "Cartera Principal",
    limite_exposicion: float = 50.0,
    limite_perdida: float = 10.0,
) -> Cartera:
    cartera = Cartera(nombre)
    cartera.configurar_riesgo(limite_exposicion, limite_perdida)
    return cartera


def crear_gestor_carteras(cartera: Cartera) -> GestorCarteras:
    gestor = GestorCarteras()
    gestor.establecer_prototipo(cartera)
    return gestor


def clonar_cartera(
    gestor: GestorCarteras,
    nombre: str,
    porcentaje_recargado: float,
) -> Cartera:
    try:
        porcentaje = float(porcentaje_recargado)
    except (TypeError, ValueError) as exc:
        raise ValueError("El porcentaje debe ser numérico.") from exc

    if not 0 <= porcentaje <= 100:
        raise ValueError("El porcentaje debe estar entre 0% y 100%.")

    if not nombre.strip():
        raise ValueError("El nombre de la cartera no puede estar vacío.")

    return gestor.crear_copia(nombre.strip(), porcentaje)


def obtener_precio_singleton(nombre: str, api) -> float | None:
    pares = {
        "Bitcoin": "BTC/USDT",
        "Ethereum": "ETH/USDT",
        "Solana": "SOL/USDT",
    }
    par = pares.get(nombre)
    return None if par is None else api.get_price(par)
