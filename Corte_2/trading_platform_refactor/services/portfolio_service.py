"""Servicio de gestión de carteras y riesgo."""

from __future__ import annotations

from patterns.composite import construir_composite
from patterns.iterator import ColeccionTrading
from patterns.memento import HistorialCartera
from patterns.prototype import clonar_cartera, crear_cartera_principal, crear_gestor_carteras
from patterns.strategy import (
    EstrategiaRiesgo,
    EstrategiaRiesgoConfigurada,
    EstrategiaRiesgoPreventiva,
)
from models.portfolio import Cartera


class PortfolioService:
    USD_COP = 4000.0

    def __init__(self) -> None:
        principal = crear_cartera_principal("Cartera Principal", 50.0, 10.0)
        principal.recargar(5000.0, "USD")
        principal.capital_referencia_usd = principal.saldo_usd
        self._portfolios: dict[str, Cartera] = {principal.nombre: principal}
        self.gestor = crear_gestor_carteras(principal)
        self._mementos: dict[str, HistorialCartera] = {}
        self._eventos_trading: list[dict[str, object]] = []
        self._estrategias_riesgo: dict[str, EstrategiaRiesgo] = {
            principal.nombre: EstrategiaRiesgoConfigurada()
        }

    def vincular_mediador(self, mediador) -> None:
        """Registra este servicio como receptor de los eventos del trading."""
        mediador.registrar(mediador.ANTES_ACTUALIZAR_CARTERA, self._guardar_estado_previo)
        mediador.registrar(mediador.ORDEN_PROCESADA, self._registrar_evento_orden)
        mediador.registrar(mediador.RESTAURAR_CARTERA, self._restaurar_estado_previo)

    def _historial_de(self, nombre: str) -> HistorialCartera:
        return self._mementos.setdefault(nombre, HistorialCartera())

    def _guardar_estado_previo(self, *, cartera: Cartera, registro) -> None:
        motivo = f"Antes de {registro.lado.value} {registro.activo}"
        self._historial_de(cartera.nombre).guardar(cartera, motivo)

    def _restaurar_estado_previo(self, *, cartera: Cartera) -> None:
        historial = self._mementos.get(cartera.nombre)
        if historial:
            historial.deshacer(cartera)

    def _registrar_evento_orden(self, *, cartera: Cartera, registro) -> None:
        self._eventos_trading.append({
            "orden_id": registro.id,
            "cartera": cartera.nombre,
            "activo": registro.activo,
            "estado": registro.estado.value,
        })
        del self._eventos_trading[:-100]

    def guardar_punto_control(self, nombre: str, motivo: str = "Punto de control manual"):
        """Guarda una instantánea solicitada explícitamente."""
        return self._historial_de(nombre).guardar(self.obtener_cartera(nombre), motivo)

    def restaurar_ultimo_estado(self, nombre: str):
        """Restaura el último estado conservado para la cartera indicada."""
        historial = self._mementos.get(nombre)
        if not historial:
            raise ValueError("La cartera no tiene estados guardados para restaurar.")
        return historial.deshacer(self.obtener_cartera(nombre))

    def listar_puntos_control(self, nombre: str) -> tuple:
        historial = self._mementos.get(nombre)
        return historial.listar() if historial else ()

    def eventos_trading(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(evento) for evento in self._eventos_trading)

    def iterar_posiciones(self, nombre: str) -> ColeccionTrading:
        """Entrega un recorrido independiente de las posiciones actuales."""
        return ColeccionTrading(self.obtener_cartera(nombre).activos)

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
        # Cada cartera nueva comienza con la política predeterminada.
        self._estrategias_riesgo[clon.nombre] = EstrategiaRiesgoConfigurada()
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

    def configurar_estrategia_riesgo(self, nombre: str, estrategia: EstrategiaRiesgo) -> None:
        """Asigna una política de evaluación a una cartera concreta."""
        self.obtener_cartera(nombre)
        if not isinstance(estrategia, EstrategiaRiesgo):
            raise TypeError("La estrategia debe implementar EstrategiaRiesgo.")
        self._estrategias_riesgo[nombre] = estrategia

    def obtener_tipo_estrategia_riesgo(self, nombre: str) -> str:
        """Devuelve la clave de la política activa para mostrarla en la interfaz."""
        self.obtener_cartera(nombre)
        estrategia = self._estrategias_riesgo.get(nombre)
        if isinstance(estrategia, EstrategiaRiesgoPreventiva):
            return "preventiva"
        return "configurada"

    def configurar_estrategia_riesgo_por_tipo(self, nombre: str, tipo: str) -> None:
        """Selecciona una de las políticas disponibles sin exponer clases a la UI."""
        estrategias = {
            "configurada": EstrategiaRiesgoConfigurada,
            "preventiva": EstrategiaRiesgoPreventiva,
        }
        clave = str(tipo).strip().lower()
        clase_estrategia = estrategias.get(clave)
        if clase_estrategia is None:
            opciones = ", ".join(estrategias)
            raise ValueError(f"Estrategia no válida. Opciones disponibles: {opciones}.")
        self.configurar_estrategia_riesgo(nombre, clase_estrategia())

    def obtener_balance(self, nombre: str, precios: dict[str, float]) -> dict:
        cartera = self.obtener_cartera(nombre)
        composite = construir_composite(cartera)
        activos_valor = composite.valor(precios)
        total = cartera.saldo_usd + activos_valor
        return {
            "saldo_usd": cartera.saldo_usd,
            "saldo_cop": cartera.saldo_cop,
            "valor_activos": activos_valor,
            "valor_total": total,
            "cantidad_activos": composite.cantidad_componentes(),
            "exposicion_pct": (activos_valor / total * 100.0) if total else 0.0,
            "drawdown_pct": (
                max(0.0, (cartera.capital_referencia_usd - total) / cartera.capital_referencia_usd * 100.0)
                if cartera.capital_referencia_usd > 0
                else 0.0
            ),
        }

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
        resumen = self.obtener_balance(cartera.nombre, precios)
        drawdown = float(resumen["drawdown_pct"])
        exposure = float(resumen["exposicion_pct"])
        estrategia = self._estrategias_riesgo.get(
            cartera.nombre, EstrategiaRiesgoConfigurada()
        )
        evaluacion = estrategia.evaluar(cartera, exposure, drawdown)
        return {
            "exposicion_pct": exposure,
            "drawdown_pct": drawdown,
            "stop_loss": cartera.stop_loss,
            "take_profit": cartera.take_profit,
            "alertas": evaluacion["alertas"],
            "advertencias": evaluacion["advertencias"],
        }
