"""Proxy virtual: controla y difiere la creación del adapter de mercado."""

from __future__ import annotations

from threading import RLock
from typing import Callable

from models.asset import ActivoDigital
from patterns.abstract_factory import Mercado


class MercadoProxy(Mercado):
    """Intermediario compatible con ``Mercado`` que inicializa el target al usarlo.

    La fábrica del adapter se ejecuta solo ante la primera consulta válida. El
    proxy también valida el tipo de activo antes de crear o invocar el objeto
    real. El bloqueo protege la inicialización cuando hay consultas concurrentes.
    """

    def __init__(self, creador_mercado: Callable[[], Mercado]) -> None:
        if not callable(creador_mercado):
            raise TypeError("El creador del mercado debe ser invocable.")
        self._creador_mercado: Callable[[], Mercado] | None = creador_mercado
        self._mercado_real: Mercado | None = None
        self._lock = RLock()

    @property
    def inicializado(self) -> bool:
        """Indica si el adapter real ya fue creado."""
        with self._lock:
            return self._mercado_real is not None

    def _obtener_mercado_real(self) -> Mercado:
        with self._lock:
            if self._mercado_real is None:
                if self._creador_mercado is None:
                    raise RuntimeError("No hay un creador disponible para el mercado.")
                mercado = self._creador_mercado()
                if not isinstance(mercado, Mercado):
                    raise TypeError("El creador debe devolver una implementación de Mercado.")
                self._mercado_real = mercado
                self._creador_mercado = None
            return self._mercado_real

    def consultar_precio(self, activo: ActivoDigital) -> float:
        if not isinstance(activo, ActivoDigital):
            raise TypeError("La consulta requiere un objeto ActivoDigital válido.")
        if not str(activo.simbolo).strip():
            raise ValueError("El activo debe tener un símbolo válido.")
        mercado = self._obtener_mercado_real()
        return float(mercado.consultar_precio(activo))
