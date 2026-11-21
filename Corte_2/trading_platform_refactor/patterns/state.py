"""State: administra las transiciones permitidas del ciclo de vida de una orden."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.order import ExecutionResult, EstadoOrden, OrdenRegistro


class EstadoOrdenState(ABC):
    """Estado abstracto de una orden."""

    estado: EstadoOrden

    @abstractmethod
    def procesar(self, resultado: ExecutionResult) -> "EstadoOrdenState":
        """Determina el siguiente estado a partir del resultado del executor."""


class EstadoPendiente(EstadoOrdenState):
    estado = EstadoOrden.PENDIENTE

    def procesar(self, resultado: ExecutionResult) -> EstadoOrdenState:
        if resultado.status == EstadoOrden.PENDIENTE:
            return self
        if resultado.status == EstadoOrden.EJECUTADA:
            return EstadoEjecutada()
        if resultado.status == EstadoOrden.RECHAZADA:
            return EstadoRechazada()
        raise ValueError("El resultado contiene un estado de orden no reconocido.")


class EstadoEjecutada(EstadoOrdenState):
    estado = EstadoOrden.EJECUTADA

    def procesar(self, resultado: ExecutionResult) -> EstadoOrdenState:
        raise ValueError("Una orden ejecutada es un estado final y no admite transiciones.")


class EstadoRechazada(EstadoOrdenState):
    estado = EstadoOrden.RECHAZADA

    def procesar(self, resultado: ExecutionResult) -> EstadoOrdenState:
        raise ValueError("Una orden rechazada es un estado final y no admite transiciones.")


class MaquinaEstadoOrden:
    """Contexto que aplica transiciones y sincroniza el registro de la orden."""

    _ESTADOS = {
        EstadoOrden.PENDIENTE: EstadoPendiente,
        EstadoOrden.EJECUTADA: EstadoEjecutada,
        EstadoOrden.RECHAZADA: EstadoRechazada,
    }

    def __init__(self, registro: OrdenRegistro) -> None:
        self.registro = registro
        try:
            self._estado = self._ESTADOS[registro.estado]()
        except KeyError as exc:
            raise ValueError("El registro contiene un estado de orden no válido.") from exc

    @property
    def estado_actual(self) -> EstadoOrden:
        return self._estado.estado

    @property
    def es_terminal(self) -> bool:
        return self.estado_actual in {EstadoOrden.EJECUTADA, EstadoOrden.RECHAZADA}

    def procesar(self, resultado: ExecutionResult) -> OrdenRegistro:
        nuevo_estado = self._estado.procesar(resultado)
        self._estado = nuevo_estado
        self.registro.estado = nuevo_estado.estado
        self.registro.total = float(resultado.total)
        self.registro.mensaje = str(resultado.message)
        return self.registro
