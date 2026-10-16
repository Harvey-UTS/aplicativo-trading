"""Flyweight: reutiliza la metadata inmutable de pares de mercado."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True, slots=True)
class ParMercadoFlyweight:
    """Estado intrínseco compartido para un par base/cotización."""

    simbolo_base: str
    simbolo_cotizacion: str
    par: str


class ParMercadoFactory:
    """Mantiene un registro compartido de pares de mercado normalizados.

    La clave está formada por el símbolo base y la divisa de cotización. Así,
    los adapters de distintos exchanges reutilizan el mismo objeto inmutable
    para, por ejemplo, BTC/USDT, sin compartir datos variables del exchange.
    """

    _flyweights: dict[tuple[str, str], ParMercadoFlyweight] = {}
    _lock = RLock()

    @classmethod
    def obtener(
        cls,
        simbolo_base: str,
        simbolo_cotizacion: str = "USDT",
    ) -> ParMercadoFlyweight:
        if simbolo_base is None or simbolo_cotizacion is None:
            raise ValueError("Los símbolos base y de cotización son obligatorios.")
        base = str(simbolo_base).strip().upper()
        cotizacion = str(simbolo_cotizacion).strip().upper()
        if not base or not cotizacion:
            raise ValueError("Los símbolos base y de cotización son obligatorios.")
        if "/" in base or "/" in cotizacion:
            raise ValueError("Los símbolos no deben contener '/'.")

        clave = (base, cotizacion)
        with cls._lock:
            flyweight = cls._flyweights.get(clave)
            if flyweight is None:
                flyweight = ParMercadoFlyweight(
                    simbolo_base=base,
                    simbolo_cotizacion=cotizacion,
                    par=f"{base}/{cotizacion}",
                )
                cls._flyweights[clave] = flyweight
            return flyweight

    @classmethod
    def cantidad_compartidos(cls) -> int:
        """Devuelve la cantidad de pares únicos que mantiene el registro."""
        with cls._lock:
            return len(cls._flyweights)

    @classmethod
    def limpiar_cache(cls) -> None:
        """Limpia el registro compartido; se utiliza principalmente en pruebas."""
        with cls._lock:
            cls._flyweights.clear()
