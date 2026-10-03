# Fuentes completas — Trading MultiExchange

Cada archivo aparece por separado y dentro de un bloque completo listo para copiar.

## `main.py`

```python
"""Punto de entrada de la Plataforma de Trading MultiExchange.

La capa de entrada solo inicializa Qt y la interfaz gráfica. No contiene
lógica de negocio ni interacción por consola.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Trading MultiExchange")
    app.setApplicationDisplayName("Trading MultiExchange")
    app.setOrganizationName("Plataforma Académica")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

## `patterns/__init__.py`

```python
"""Patrones GoF de la plataforma."""
```

## `patterns/singleton.py`

```python
"""Singleton: fuente única de verdad para precios simulados."""

from __future__ import annotations

import random
import threading
import time
from typing import ClassVar


class ExchangeConnectionManager:
    """Administra una única instancia del caché de mercado.

    No conoce PySide6 y no imprime en consola. Puede ejecutar una pequeña
    simulación en segundo plano para mantener el comportamiento dinámico del
    ejercicio original.
    """

    _instance: ClassVar["ExchangeConnectionManager | None"] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    _initial_exchange_prices = {
        "A": {
            "BTC/USDT": 60000.00,
            "ETH/USDT": 3000.00,
            "SOL/USDT": 145.20,
            "LINK/USDT": 15.00,
            "MATIC/USDT": 0.50,
            "CRYPTOART001/USDT": 2500.00,
        },
        "B": {
            "BTC/USDT": 60500.00,
            "ETH/USDT": 3050.00,
            "SOL/USDT": 146.10,
            "LINK/USDT": 15.50,
            "MATIC/USDT": 0.55,
            "CRYPTOART001/USDT": 2600.00,
        },
        "C": {
            "BTC/USDT": 61000.00,
            "ETH/USDT": 3095.00,
            "SOL/USDT": 147.40,
            "LINK/USDT": 16.00,
            "MATIC/USDT": 0.57,
            "CRYPTOART001/USDT": 2700.00,
        },
    }

    _canonical_prices = {
        "BTC/USDT": 64500.50,
        "ETH/USDT": 3450.75,
        "SOL/USDT": 145.20,
    }

    def __new__(cls) -> "ExchangeConnectionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self) -> None:
        self._prices = {
            exchange: dict(prices)
            for exchange, prices in self._initial_exchange_prices.items()
        }
        self._canonical = dict(self._canonical_prices)
        self._data_lock = threading.RLock()
        self.running = False
        self._thread: threading.Thread | None = None

    def start(self, interval: float = 1.0) -> None:
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(
            target=self._update_loop,
            args=(interval,),
            daemon=True,
            name="market-simulator",
        )
        self._thread.start()

    def _update_loop(self, interval: float) -> None:
        while self.running:
            time.sleep(max(0.25, interval))
            self.simulate_market_update()

    def simulate_market_update(self) -> None:
        with self._data_lock:
            for exchange_prices in self._prices.values():
                for pair, value in list(exchange_prices.items()):
                    exchange_prices[pair] = round(
                        max(0.0001, value * (1.0 + random.uniform(-0.003, 0.003))),
                        4 if value < 1 else 2,
                    )

            for pair, value in list(self._canonical.items()):
                self._canonical[pair] = round(
                    max(0.0001, value * (1.0 + random.uniform(-0.003, 0.003))),
                    4 if value < 1 else 2,
                )

    def get_price(self, pair: str) -> float | None:
        """Mantiene el contrato original para el precio canónico."""
        with self._data_lock:
            return self._canonical.get(pair)

    def get_exchange_price(self, exchange: str, pair: str) -> float | None:
        exchange = str(exchange).upper()
        with self._data_lock:
            return self._prices.get(exchange, {}).get(pair)

    def set_cached_price(self, exchange: str, pair: str, price: float) -> None:
        with self._data_lock:
            self._prices.setdefault(exchange.upper(), {})[pair] = float(price)

    def snapshot(self, exchange: str | None = None) -> dict:
        with self._data_lock:
            if exchange is None:
                return {key: dict(value) for key, value in self._prices.items()}
            return dict(self._prices.get(exchange.upper(), {}))

    def stop(self) -> None:
        self.running = False

    @classmethod
    def reset_for_tests(cls) -> None:
        """Reinicia el Singleton únicamente para pruebas automatizadas."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.stop()
            cls._instance = None
```

## `patterns/factory_method.py`

```python
"""Factory Method para criptomonedas, tokens y NFT."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.asset import ActivoDigital, Criptomoneda, NFT, Token


class CreadorActivo(ABC):
    """Creator abstracto del patrón Factory Method."""

    @abstractmethod
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        pass

    def comprar_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float,
        simbolo: str | None = None,
    ):
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.comprar(cantidad)

    def vender_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float,
        simbolo: str | None = None,
    ):
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.vender(cantidad)

    def mostrar_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> dict[str, object]:
        activo = self.crear_activo(nombre, precio, simbolo)
        return activo.mostrar_informacion()


class CreadorCriptomoneda(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return Criptomoneda(nombre, precio, simbolo)


class CreadorToken(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return Token(nombre, precio, simbolo)


class CreadorNFT(CreadorActivo):
    def crear_activo(
        self,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        return NFT(nombre, precio, simbolo)
```

## `patterns/abstract_factory.py`

```python
"""Abstract Factory para familias de productos de cada exchange."""

from __future__ import annotations

from abc import ABC, abstractmethod

from patterns.bridge import (
    EjecutorOrden,
    ExchangeAExecutor,
    ExchangeBExecutor,
    ExchangeCExecutor,
)


class Mercado(ABC):
    """Producto abstracto de consulta de mercado."""

    @abstractmethod
    def consultar_precio(self, activo):
        pass


class FabricaExchange(ABC):
    """Abstract Factory."""

    @abstractmethod
    def crear_mercado(self) -> Mercado:
        pass

    @abstractmethod
    def crear_orden(self) -> EjecutorOrden:
        pass

    @property
    @abstractmethod
    def codigo(self) -> str:
        pass


class MercadoExchangeA:
    """Alias conceptual mantenido para el ejercicio anterior."""

    pass


class MercadoExchangeB:
    pass


class MercadoExchangeC:
    pass


class FabricaExchangeA(FabricaExchange):
    codigo = "A"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeAAdapter
        return ExchangeAAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeAExecutor()


class FabricaExchangeB(FabricaExchange):
    codigo = "B"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeBAdapter
        return ExchangeBAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeBExecutor()


class FabricaExchangeC(FabricaExchange):
    codigo = "C"

    def crear_mercado(self) -> Mercado:
        from patterns.adapter import ExchangeCAdapter
        return ExchangeCAdapter()

    def crear_orden(self) -> EjecutorOrden:
        return ExchangeCExecutor()


# Compatibilidad explícita con los nombres históricos del avance.
from patterns.adapter import ExchangeAAdapter, ExchangeBAdapter, ExchangeCAdapter

MercadoExchangeA = ExchangeAAdapter
MercadoExchangeB = ExchangeBAdapter
MercadoExchangeC = ExchangeCAdapter
OrdenExchangeA = ExchangeAExecutor
OrdenExchangeB = ExchangeBExecutor
OrdenExchangeC = ExchangeCExecutor
```

## `patterns/prototype.py`

```python
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
```

## `patterns/builder.py`

```python
"""Builder que ensambla los patrones de la plataforma."""

from __future__ import annotations

from dataclasses import dataclass

from models.asset import ActivoDigital
from models.portfolio import Cartera
from patterns.abstract_factory import (
    FabricaExchange,
    FabricaExchangeA,
    FabricaExchangeB,
    FabricaExchangeC,
)
from patterns.bridge import OrdenLimit, OrdenMarket, OrdenStopLoss, OrdenTrading
from patterns.factory_method import (
    CreadorCriptomoneda,
    CreadorNFT,
    CreadorToken,
)
from patterns.prototype import GestorCarteras
from patterns.singleton import ExchangeConnectionManager


@dataclass(slots=True)
class PlataformaTrading:
    """Producto final ensamblado por Builder."""

    sistema_ordenes: ExchangeConnectionManager | None = None
    creador: object | None = None
    activo: ActivoDigital | None = None
    fabrica_exchange: FabricaExchange | None = None
    cartera: Cartera | None = None
    gestor_carteras: GestorCarteras | None = None
    orden: OrdenTrading | None = None

    @property
    def exchange(self) -> str:
        if self.fabrica_exchange is None:
            return ""
        return self.fabrica_exchange.codigo


class PlataformaTradingBuilder:
    """Builder fluido para escenarios de trading completos."""

    def __init__(self) -> None:
        self.sistema_ordenes: ExchangeConnectionManager | None = None
        self.creador = None
        self.activo: ActivoDigital | None = None
        self.fabrica_exchange: FabricaExchange | None = None
        self.cartera: Cartera | None = None
        self.gestor_carteras: GestorCarteras | None = None
        self.orden: OrdenTrading | None = None

    def configurar_singleton(self) -> "PlataformaTradingBuilder":
        self.sistema_ordenes = ExchangeConnectionManager()
        return self

    def configurar_operacion(
        self,
        tipo_activo: str,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> "PlataformaTradingBuilder":
        creadores = {
            "CRIPTO": CreadorCriptomoneda,
            "CRYPTO": CreadorCriptomoneda,
            "TOKEN": CreadorToken,
            "NFT": CreadorNFT,
        }
        key = tipo_activo.upper().strip()
        aliases = {
            "CRIPTOMONEDA": "CRIPTO",
            "CRYPTOCURRENCY": "CRIPTO",
            "TOKEN": "TOKEN",
            "NFT": "NFT",
            "CRYPTO": "CRIPTO",
        }
        key = aliases.get(key, key)
        creador_cls = creadores.get(key)
        if creador_cls is None:
            raise ValueError("Tipo de activo no válido. Use CRIPTO, TOKEN o NFT.")
        self.creador = creador_cls()
        self.activo = self.creador.crear_activo(nombre, precio, simbolo)
        return self

    def configurar_exchange(
        self,
        exchange: str | FabricaExchange,
    ) -> "PlataformaTradingBuilder":
        if isinstance(exchange, FabricaExchange):
            self.fabrica_exchange = exchange
            return self

        factories = {
            "A": FabricaExchangeA,
            "B": FabricaExchangeB,
            "C": FabricaExchangeC,
        }
        factory_cls = factories.get(str(exchange).upper().strip())
        if factory_cls is None:
            raise ValueError("Exchange no válido. Use A, B o C.")
        self.fabrica_exchange = factory_cls()
        return self

    def configurar_cartera(
        self,
        cartera: Cartera,
        gestor_carteras: GestorCarteras | None = None,
    ) -> "PlataformaTradingBuilder":
        self.cartera = cartera
        self.gestor_carteras = gestor_carteras
        return self

    def configurar_orden(
        self,
        tipo_orden: str,
        precio_objetivo: float | None = None,
    ) -> "PlataformaTradingBuilder":
        if self.fabrica_exchange is None:
            raise ValueError("Primero debe configurar el exchange.")

        executor = self.fabrica_exchange.crear_orden()
        key = tipo_orden.upper().replace("-", " ").strip()
        if key == "MARKET":
            self.orden = OrdenMarket(executor)
        elif key == "LIMIT":
            if precio_objetivo is None:
                raise ValueError("La orden Limit requiere un precio objetivo.")
            self.orden = OrdenLimit(executor, precio_objetivo)
        elif key in {"STOP LOSS", "STOPLOSS"}:
            if precio_objetivo is None:
                raise ValueError("La orden Stop Loss requiere un precio de activación.")
            self.orden = OrdenStopLoss(executor, precio_objetivo)
        else:
            raise ValueError("Tipo de orden no válido.")
        return self

    def build(self) -> PlataformaTrading:
        if self.sistema_ordenes is None:
            self.configurar_singleton()
        if self.fabrica_exchange is None:
            raise ValueError("Debe configurar un exchange.")
        if self.cartera is None:
            raise ValueError("Debe configurar una cartera.")

        return PlataformaTrading(
            sistema_ordenes=self.sistema_ordenes,
            creador=self.creador,
            activo=self.activo,
            fabrica_exchange=self.fabrica_exchange,
            cartera=self.cartera,
            gestor_carteras=self.gestor_carteras,
            orden=self.orden,
        )
```

## `patterns/bridge.py`

```python
"""Bridge: tipos de orden desacoplados de exchanges."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.asset import ActivoDigital
from models.order import ExecutionResult, EstadoOrden, LadoOrden, TipoOrden


class EjecutorOrden(ABC):
    """Implementador del Bridge y producto abstracto para Abstract Factory."""

    nombre_exchange = "Exchange"

    @abstractmethod
    def ejecutar(
        self,
        orden: "OrdenTrading",
        activo: ActivoDigital,
        lado: LadoOrden,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        pass

    def _resultado_ejecutado(
        self,
        activo: ActivoDigital,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        return ExecutionResult(
            status=EstadoOrden.EJECUTADA,
            message=(
                f"Orden {activo.nombre} ejecutada en {self.nombre_exchange}."
            ),
            total=precio * cantidad,
        )

    def _resultado_pendiente(self, mensaje: str) -> ExecutionResult:
        return ExecutionResult(
            status=EstadoOrden.PENDIENTE,
            message=mensaje,
            total=0.0,
        )


class OrdenTrading(ABC):
    """Abstracción del Bridge para el tipo de orden."""

    tipo: TipoOrden = TipoOrden.MARKET

    def __init__(self, executor: EjecutorOrden) -> None:
        self.executor = executor

    def cambiar_executor(self, executor: EjecutorOrden) -> None:
        self.executor = executor

    @abstractmethod
    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        pass

    def ejecutar(
        self,
        activo: ActivoDigital,
        lado: LadoOrden,
        cantidad: float,
        precio: float,
    ) -> ExecutionResult:
        lado_enum = lado if isinstance(lado, LadoOrden) else LadoOrden(str(lado).upper())
        activo.validar_cantidad(cantidad)
        self.validar(lado_enum, cantidad, precio)
        return self.executor.ejecutar(self, activo, lado_enum, cantidad, precio)


class OrdenMarket(OrdenTrading):
    tipo = TipoOrden.MARKET

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Market requiere cantidad y precio positivos.")


class OrdenLimit(OrdenTrading):
    tipo = TipoOrden.LIMIT

    def __init__(self, executor: EjecutorOrden, precio_limite: float) -> None:
        super().__init__(executor)
        if precio_limite <= 0:
            raise ValueError("El precio límite debe ser mayor que cero.")
        self.precio_limite = float(precio_limite)

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Limit requiere cantidad y precio positivos.")


class OrdenStopLoss(OrdenTrading):
    tipo = TipoOrden.STOP_LOSS

    def __init__(self, executor: EjecutorOrden, precio_activacion: float) -> None:
        super().__init__(executor)
        if precio_activacion <= 0:
            raise ValueError("El precio de activación debe ser mayor que cero.")
        self.precio_activacion = float(precio_activacion)

    def validar(self, lado: LadoOrden, cantidad: float, precio: float) -> None:
        if cantidad <= 0 or precio <= 0:
            raise ValueError("Una orden Stop Loss requiere cantidad y precio positivos.")


class ExchangeAExecutor(EjecutorOrden):
    nombre_exchange = "Exchange A"

    def ejecutar(self, orden, activo, lado, cantidad, precio) -> ExecutionResult:
        if isinstance(orden, OrdenLimit):
            condicion = precio <= orden.precio_limite if lado == LadoOrden.COMPRA else precio >= orden.precio_limite
            if not condicion:
                return self._resultado_pendiente(
                    f"Orden Limit pendiente: el precio actual (${precio:,.2f}) "
                    f"no cumple el límite (${orden.precio_limite:,.2f})."
                )

        if isinstance(orden, OrdenStopLoss):
            condicion = precio >= orden.precio_activacion if lado == LadoOrden.COMPRA else precio <= orden.precio_activacion
            if not condicion:
                return self._resultado_pendiente(
                    f"Stop Loss pendiente: el precio actual (${precio:,.2f}) "
                    f"no ha alcanzado la activación (${orden.precio_activacion:,.2f})."
                )

        return self._resultado_ejecutado(activo, cantidad, precio)


class ExchangeBExecutor(ExchangeAExecutor):
    nombre_exchange = "Exchange B"


class ExchangeCExecutor(ExchangeAExecutor):
    nombre_exchange = "Exchange C"
```

## `patterns/adapter.py`

```python
"""Adapter: normaliza APIs de exchanges con estructuras incompatibles."""

from __future__ import annotations

from models.asset import ActivoDigital
from patterns.abstract_factory import Mercado
from patterns.singleton import ExchangeConnectionManager


class ApiExchangeA:
    """API externa simulada: devuelve lastPrice."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def get_ticker(self, pair: str) -> dict[str, object]:
        price = self.manager.get_exchange_price("A", pair)
        if price is None:
            raise KeyError(f"El par {pair} no existe en Exchange A.")
        return {"symbol": pair, "lastPrice": price}


class ApiExchangeB:
    """API externa simulada: exige base/quote y entrega data.amount."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def fetch_market(self, base: str, quote: str) -> dict[str, object]:
        pair = f"{base.upper()}/{quote.upper()}"
        price = self.manager.get_exchange_price("B", pair)
        if price is None:
            raise KeyError(f"El par {pair} no existe en Exchange B.")
        return {"data": {"pair": pair, "amount": str(price)}}


class ApiExchangeC:
    """API externa simulada: devuelve ticker.last y un formato alternativo."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def obtener_ticker(self, par: str) -> dict[str, object]:
        price = self.manager.get_exchange_price("C", par)
        if price is None:
            raise KeyError(f"El par {par} no existe en Exchange C.")
        return {"ticker": {"pair": par, "last": price, "currency": "USDT"}}


def _pair_for_asset(activo: ActivoDigital) -> str:
    return f"{activo.simbolo.upper()}/USDT"


def _split_pair(pair: str) -> tuple[str, str]:
    base, quote = pair.split("/", 1)
    return base, quote


class ExchangeAAdapter(Mercado):
    """Target: Mercado.consultar_precio(activo)."""

    def __init__(self, api: ApiExchangeA | None = None) -> None:
        self.api = api or ApiExchangeA()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        response = self.api.get_ticker(_pair_for_asset(activo))
        return float(response["lastPrice"])


class ExchangeBAdapter(Mercado):
    def __init__(self, api: ApiExchangeB | None = None) -> None:
        self.api = api or ApiExchangeB()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        base, quote = _split_pair(_pair_for_asset(activo))
        response = self.api.fetch_market(base, quote)
        return float(response["data"]["amount"])


class ExchangeCAdapter(Mercado):
    def __init__(self, api: ApiExchangeC | None = None) -> None:
        self.api = api or ApiExchangeC()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        response = self.api.obtener_ticker(_pair_for_asset(activo))
        return float(response["ticker"]["last"])
```

## `patterns/composite.py`

```python
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
```

## `patterns/decorator.py`

```python
"""Decorator para añadir trazabilidad a las consultas de mercado."""

from __future__ import annotations

from abc import ABC
from datetime import datetime

from models.asset import ActivoDigital
from patterns.abstract_factory import Mercado


class MercadoDecorator(Mercado, ABC):
    """Decorator base que conserva el contrato de Mercado."""

    def __init__(self, mercado: Mercado) -> None:
        self.mercado = mercado

    def consultar_precio(self, activo: ActivoDigital) -> float:
        return self.mercado.consultar_precio(activo)


class MercadoConAuditoria(MercadoDecorator):
    """Añade historial de consultas sin modificar el adapter original."""

    def __init__(self, mercado: Mercado, exchange: str) -> None:
        super().__init__(mercado)
        self.exchange = str(exchange).upper()
        self._consultas = 0
        self._ultima_consulta: dict[str, object] | None = None

    def consultar_precio(self, activo: ActivoDigital) -> float:
        precio = super().consultar_precio(activo)
        self._consultas += 1
        self._ultima_consulta = {
            "exchange": self.exchange,
            "activo": activo.nombre,
            "simbolo": activo.simbolo,
            "precio": float(precio),
            "timestamp": datetime.now(),
        }
        return float(precio)

    @property
    def consultas(self) -> int:
        return self._consultas

    @property
    def ultima_consulta(self) -> dict[str, object] | None:
        return None if self._ultima_consulta is None else dict(self._ultima_consulta)

    def resumen(self) -> dict[str, object]:
        return {
            "exchange": self.exchange,
            "consultas": self.consultas,
            "ultima_consulta": self.ultima_consulta,
        }
```

## `models/__init__.py`

```python
"""Modelos de dominio de la plataforma."""
```

## `models/asset.py`

```python
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
```

## `models/order.py`

```python
"""Modelos de órdenes e historial."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class TipoOrden(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP LOSS"


class LadoOrden(str, Enum):
    COMPRA = "COMPRA"
    VENTA = "VENTA"


class EstadoOrden(str, Enum):
    EJECUTADA = "EJECUTADA"
    PENDIENTE = "PENDIENTE"
    RECHAZADA = "RECHAZADA"


@dataclass(slots=True)
class ExecutionResult:
    """Resultado normalizado de un executor de exchange."""

    status: EstadoOrden
    message: str
    total: float = 0.0


@dataclass(slots=True)
class OrdenRegistro:
    """Registro inmutable de una operación simulada."""

    id: str = field(default_factory=lambda: uuid4().hex[:10].upper())
    timestamp: datetime = field(default_factory=datetime.now)
    tipo: TipoOrden = TipoOrden.MARKET
    lado: LadoOrden = LadoOrden.COMPRA
    exchange: str = "A"
    cartera: str = "Cartera Principal"
    activo: str = ""
    cantidad: float = 0.0
    precio: float = 0.0
    precio_objetivo: float | None = None
    estado: EstadoOrden = EstadoOrden.PENDIENTE
    total: float = 0.0
    mensaje: str = ""

    def to_row(self) -> list[str]:
        objetivo = "—" if self.precio_objetivo is None else f"${self.precio_objetivo:,.2f}"
        return [
            self.id,
            self.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            self.tipo.value,
            self.lado.value,
            self.exchange,
            self.cartera,
            self.activo,
            f"{self.cantidad:g}",
            f"${self.precio:,.2f}",
            objetivo,
            self.estado.value,
            f"${self.total:,.2f}",
        ]
```

## `models/portfolio.py`

```python
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
```

## `services/__init__.py`

```python
"""Servicios de aplicación."""
```

## `services/market_service.py`

```python
"""Servicio de mercado: única puerta de entrada a precios y activos."""

from __future__ import annotations

from dataclasses import dataclass

from models.asset import ActivoDigital
from patterns.abstract_factory import FabricaExchangeA, FabricaExchangeB, FabricaExchangeC
from patterns.decorator import MercadoConAuditoria
from patterns.factory_method import CreadorCriptomoneda, CreadorNFT, CreadorToken
from patterns.singleton import ExchangeConnectionManager


@dataclass(slots=True)
class MarketRow:
    activo: str
    simbolo: str
    tipo: str
    exchange: str
    precio: float
    variacion: float


class MarketService:
    """Coordina Factory Method, Abstract Factory, Adapter y Singleton."""

    USD_COP = 4000.0

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()
        self.factories = {
            "A": FabricaExchangeA(),
            "B": FabricaExchangeB(),
            "C": FabricaExchangeC(),
        }
        self._markets = {
            codigo: MercadoConAuditoria(factory.crear_mercado(), codigo)
            for codigo, factory in self.factories.items()
        }
        self.creators = {
            "CRIPTO": CreadorCriptomoneda(),
            "CRYPTO": CreadorCriptomoneda(),
            "TOKEN": CreadorToken(),
            "NFT": CreadorNFT(),
        }
        self._assets: dict[str, ActivoDigital] = {}
        self._seed_assets()

    def _seed_assets(self) -> None:
        initial = [
            ("CRIPTO", "Bitcoin", 60000.0, "BTC"),
            ("CRIPTO", "Ethereum", 3000.0, "ETH"),
            ("TOKEN", "Chainlink", 15.0, "LINK"),
            ("TOKEN", "Polygon", 0.5, "MATIC"),
            ("NFT", "CryptoArt #001", 2500.0, "CRYPTOART001"),
            ("CRIPTO", "Solana", 145.2, "SOL"),
        ]
        for kind, name, price, symbol in initial:
            self._assets[name] = self.creators[kind].crear_activo(name, price, symbol)

    def crear_activo(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        simbolo: str | None = None,
    ) -> ActivoDigital:
        kind = tipo.upper().strip()
        creator = self.creators.get(kind)
        if creator is None:
            raise ValueError("Tipo de activo no válido.")
        if nombre in self._assets:
            raise ValueError("Ya existe un activo con ese nombre.")
        if precio <= 0:
            raise ValueError("El precio inicial debe ser mayor que cero.")

        activo = creator.crear_activo(nombre, precio, simbolo)
        self._assets[activo.nombre] = activo
        return activo

    def obtener_activos(self) -> list[ActivoDigital]:
        return list(self._assets.values())

    def obtener_activo(self, nombre: str) -> ActivoDigital:
        try:
            return self._assets[nombre]
        except KeyError as exc:
            raise ValueError(f"No existe el activo {nombre}.") from exc

    def obtener_precio(self, activo: ActivoDigital | str, exchange: str = "A") -> float:
        if isinstance(activo, str):
            activo = self.obtener_activo(activo)
        factory = self.factories.get(str(exchange).upper())
        if factory is None:
            raise ValueError("Exchange no válido.")
        mercado = self._markets[str(exchange).upper()]
        try:
            precio = mercado.consultar_precio(activo)
        except KeyError:
            # Los activos personalizados todavía pueden cotizar con el precio
            # inicial mientras el simulador no tenga un ticker específico.
            precio = activo.precio
        self.manager.set_cached_price(str(exchange).upper(), f"{activo.simbolo}/USDT", precio)
        activo.precio = float(precio)
        return float(precio)

    def obtener_auditoria_mercado(self, exchange: str) -> dict[str, object]:
        """Expone la trazabilidad agregada por el Decorator de mercado."""
        codigo = str(exchange).upper()
        if codigo not in self._markets:
            raise ValueError("Exchange no válido.")
        return self._markets[codigo].resumen()

    def actualizar_mercado(self) -> None:
        """Actualiza el cache de todos los activos con sus adapters."""
        self.manager.simulate_market_update()
        for exchange in self.factories:
            for activo in self._assets.values():
                try:
                    self.obtener_precio(activo, exchange)
                except (ValueError, KeyError):
                    continue

    def tabla_mercado(self, previous: dict[tuple[str, str], float] | None = None) -> list[MarketRow]:
        previous = previous or {}
        rows: list[MarketRow] = []
        for exchange in self.factories:
            for activo in self._assets.values():
                precio = self.obtener_precio(activo, exchange)
                key = (exchange, activo.nombre)
                old = previous.get(key, precio)
                variacion = ((precio - old) / old * 100.0) if old else 0.0
                rows.append(MarketRow(activo.nombre, activo.simbolo, activo.tipo, exchange, precio, variacion))
        return rows
```

## `services/portfolio_service.py`

```python
"""Servicio de gestión de carteras y riesgo."""

from __future__ import annotations

from patterns.composite import construir_composite
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
```

## `services/trading_service.py`

```python
"""Servicio principal de compra, venta, órdenes y ejecución."""

from __future__ import annotations

from models.order import EstadoOrden, LadoOrden, OrdenRegistro, TipoOrden
from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from patterns.builder import PlataformaTrading, PlataformaTradingBuilder


class TradingService:
    """Orquesta Builder, Bridge, Adapter, Abstract Factory, Prototype y Singleton."""

    def __init__(self, market_service: MarketService, portfolio_service: PortfolioService) -> None:
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self._history: list[OrdenRegistro] = []

    def crear_orden(
        self,
        tipo_orden: str,
        lado: str,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str,
        precio_objetivo: float | None = None,
    ) -> tuple[PlataformaTrading, OrdenRegistro]:
        activo = self.market_service.obtener_activo(activo_nombre)
        cartera = self.portfolio_service.obtener_cartera(cartera_nombre)
        exchange = exchange.upper().strip()
        lado_enum = LadoOrden(lado.upper().strip())
        tipo_enum = self._parse_tipo(tipo_orden)

        builder = (
            PlataformaTradingBuilder()
            .configurar_singleton()
            .configurar_operacion(activo.tipo, activo.nombre, activo.precio, activo.simbolo)
            .configurar_exchange(exchange)
            .configurar_cartera(cartera, self.portfolio_service.gestor)
            .configurar_orden(tipo_enum.value, precio_objetivo)
        )
        platform = builder.build()

        registro = OrdenRegistro(
            tipo=tipo_enum,
            lado=lado_enum,
            exchange=exchange,
            cartera=cartera.nombre,
            activo=activo.nombre,
            cantidad=float(cantidad),
            precio=0.0,
            precio_objetivo=precio_objetivo,
        )
        return platform, registro

    def ejecutar_orden(self, platform: PlataformaTrading, registro: OrdenRegistro) -> OrdenRegistro:
        if platform.orden is None or platform.activo is None or platform.cartera is None:
            raise ValueError("La plataforma de trading no tiene una orden completa configurada.")

        activo = platform.activo
        cartera = platform.cartera
        precio = self.market_service.obtener_precio(activo, registro.exchange)
        registro.precio = precio
        activo.precio = precio

        precios_cartera = {
            p.nombre: self.market_service.obtener_precio(p.nombre, registro.exchange)
            for p in cartera.activos
        }
        precios_cartera[activo.nombre] = precio

        if registro.lado == LadoOrden.COMPRA:
            self.portfolio_service.validar_compra(
                cartera,
                activo.nombre,
                registro.cantidad,
                precio,
                precios_cartera,
            )
        else:
            self.portfolio_service.validar_venta(cartera, activo.nombre, registro.cantidad)

        resultado = platform.orden.ejecutar(
            activo,
            registro.lado,
            registro.cantidad,
            precio,
        )
        registro.estado = resultado.status
        registro.total = resultado.total
        registro.mensaje = resultado.message

        if resultado.status == EstadoOrden.EJECUTADA:
            if registro.lado == LadoOrden.COMPRA:
                cartera.saldo_usd -= resultado.total
                cartera.registrar_compra(activo, registro.cantidad, precio)
            else:
                vendido = cartera.registrar_venta(activo.nombre, registro.cantidad)
                if not vendido:
                    registro.estado = EstadoOrden.RECHAZADA
                    registro.mensaje = "La venta no pudo actualizar la cartera."
                    registro.total = 0.0
                else:
                    cartera.saldo_usd += resultado.total

        self._history.insert(0, registro)
        return registro

    def comprar_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        platform, registro = self.crear_orden(
            TipoOrden.MARKET.value,
            LadoOrden.COMPRA.value,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
        )
        return self.ejecutar_orden(platform, registro)

    def vender_activo(
        self,
        exchange: str,
        activo_nombre: str,
        cantidad: float,
        cartera_nombre: str = "Cartera Principal",
    ) -> OrdenRegistro:
        platform, registro = self.crear_orden(
            TipoOrden.MARKET.value,
            LadoOrden.VENTA.value,
            exchange,
            activo_nombre,
            cantidad,
            cartera_nombre,
        )
        return self.ejecutar_orden(platform, registro)

    def historial(self) -> list[OrdenRegistro]:
        return list(self._history)

    @staticmethod
    def _parse_tipo(tipo_orden: str) -> TipoOrden:
        key = str(tipo_orden).upper().replace("-", " ").strip()
        aliases = {
            "MARKET": TipoOrden.MARKET,
            "LIMIT": TipoOrden.LIMIT,
            "STOP LOSS": TipoOrden.STOP_LOSS,
            "STOPLOSS": TipoOrden.STOP_LOSS,
        }
        try:
            return aliases[key]
        except KeyError as exc:
            raise ValueError("Tipo de orden no válido.") from exc
```

## `ui/__init__.py`

```python
"""Interfaz gráfica PySide6."""
```

## `ui/assets_page.py`

```python
"""Gestión visual de activos mediante Factory Method."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDoubleSpinBox,
)


class AssetsPage(QWidget):
    def __init__(self, market_service, on_change) -> None:
        super().__init__()
        self.market_service = market_service
        self.on_change = on_change
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        title = QLabel("Activos digitales")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Crear Criptomonedas, Tokens y NFT con Factory Method")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        group = QGroupBox("Nuevo activo")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignLeft)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["CRIPTO", "TOKEN", "NFT"])
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej. Cardano")
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Ej. ADA")
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0001, 1_000_000_000)
        self.price_input.setDecimals(4)
        self.price_input.setValue(10.0)

        form.addRow("Tipo", self.type_combo)
        form.addRow("Nombre", self.name_input)
        form.addRow("Símbolo", self.symbol_input)
        form.addRow("Precio inicial (USD)", self.price_input)

        button_row = QHBoxLayout()
        button_row.addStretch()
        create = QPushButton("Crear activo")
        create.setObjectName("primaryButton")
        create.clicked.connect(self.create_asset)
        button_row.addWidget(create)
        form.addRow("", button_row)
        layout.addWidget(group)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Nombre", "Símbolo", "Tipo", "Precio base", "Acción"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def create_asset(self) -> None:
        try:
            activo = self.market_service.crear_activo(
                self.type_combo.currentText(),
                self.name_input.text(),
                self.price_input.value(),
                self.symbol_input.text() or None,
            )
        except ValueError as exc:
            QMessageBox.warning(self, "No se pudo crear", str(exc))
            return
        QMessageBox.information(self, "Activo creado", f"{activo.nombre} fue agregado a la plataforma.")
        self.name_input.clear()
        self.symbol_input.clear()
        self.refresh()
        self.on_change()

    def refresh(self) -> None:
        assets = self.market_service.obtener_activos()
        self.table.setRowCount(len(assets))
        for row, asset in enumerate(assets):
            values = [asset.nombre, asset.simbolo, asset.tipo, f"${asset.precio:,.2f}", "Disponible"]
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
```

## `ui/dashboard_page.py`

```python
"""Dashboard financiero académico."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from services.trading_service import TradingService


class DashboardPage(QWidget):
    def __init__(self, market_service, portfolio_service, trading_service, on_change) -> None:
        super().__init__()
        self.market_service: MarketService = market_service
        self.portfolio_service: PortfolioService = portfolio_service
        self.trading_service: TradingService = trading_service
        self.on_change = on_change
        self.cards: dict[str, QLabel] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()
        action = QPushButton("Actualizar mercado")
        action.setObjectName("primaryButton")
        action.clicked.connect(self.on_change)
        header.addWidget(action)
        layout.addLayout(header)

        subtitle = QLabel("Vista general del mercado y del capital simulado")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for idx, (key, label) in enumerate([
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("SOL", "Solana"),
            ("TOTAL", "Valor total cartera"),
            ("ASSETS", "Cantidad de activos"),
            ("PNL", "Ganancia simulada"),
        ]):
            frame, value = self._metric_card(label)
            self.cards[key] = value
            grid.addWidget(frame, idx // 3, idx % 3)
        layout.addLayout(grid)

        section = QLabel("Composición de la cartera principal")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Activo", "Cantidad", "Precio promedio", "Precio actual", "Valor"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        note = QLabel(
            "Los precios son simulados localmente. No se envían órdenes a exchanges reales."
        )
        note.setObjectName("infoBanner")
        note.setAlignment(Qt.AlignCenter)
        layout.addWidget(note)

    def _metric_card(self, label: str):
        frame = QFrame()
        frame.setObjectName("metricCard")
        box = QVBoxLayout(frame)
        box.setContentsMargins(18, 18, 18, 18)
        caption = QLabel(label)
        caption.setObjectName("metricCaption")
        value = QLabel("—")
        value.setObjectName("metricValue")
        box.addWidget(caption)
        box.addWidget(value)
        return frame, value

    def refresh(self) -> None:
        cartera = self.portfolio_service.obtener_cartera("Cartera Principal")
        precios = {}
        for position in cartera.activos:
            try:
                precios[position.nombre] = self.market_service.obtener_precio(position.nombre, "A")
            except ValueError:
                precios[position.nombre] = position.precio_promedio
        resumen = self.portfolio_service.obtener_balance(cartera.nombre, precios)

        btc = self.market_service.obtener_precio("Bitcoin", "A")
        eth = self.market_service.obtener_precio("Ethereum", "A")
        sol = self.market_service.obtener_precio("Solana", "A")

        self.cards["BTC"].setText(f"${btc:,.2f}")
        self.cards["ETH"].setText(f"${eth:,.2f}")
        self.cards["SOL"].setText(f"${sol:,.2f}")
        self.cards["TOTAL"].setText(f"${resumen['valor_total']:,.2f} USD")
        self.cards["ASSETS"].setText(str(resumen["cantidad_activos"]))
        pnl = resumen["valor_total"] - cartera.capital_referencia_usd
        self.cards["PNL"].setText(f"${pnl:,.2f} USD")

        self.table.setRowCount(len(cartera.activos))
        for row, position in enumerate(cartera.activos):
            actual = precios.get(position.nombre, position.precio_promedio)
            values = [
                position.nombre,
                f"{position.cantidad:g}",
                f"${position.precio_promedio:,.2f}",
                f"${actual:,.2f}",
                f"${position.cantidad * actual:,.2f}",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
```

## `ui/main_window.py`

```python
"""Ventana principal y navegación de la aplicación."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from patterns.singleton import ExchangeConnectionManager
from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from services.trading_service import TradingService
from ui.assets_page import AssetsPage
from ui.dashboard_page import DashboardPage
from ui.market_page import MarketPage
from ui.orders_page import OrdersPage
from ui.portfolios_page import PortfoliosPage


class MainWindow(QMainWindow):
    """Shell visual de la plataforma."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Trading MultiExchange | Plataforma Académica")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 720)

        self.manager = ExchangeConnectionManager()
        self.market_service = MarketService(self.manager)
        self.portfolio_service = PortfolioService()
        self.trading_service = TradingService(self.market_service, self.portfolio_service)

        self.manager.start()
        self._build_ui()
        self._load_styles()
        self._start_timer()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(22, 24, 22, 22)
        sidebar_layout.setSpacing(10)

        brand = QLabel("TRADE\nMULTIEXCHANGE")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)

        subtitle = QLabel("Simulación académica")
        subtitle.setObjectName("sidebarSubtitle")
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(24)

        self.nav_buttons: list[QPushButton] = []
        pages = [
            ("⌂   Dashboard", 0),
            ("◈   Mercado", 1),
            ("◆   Activos", 2),
            ("⇄   Órdenes", 3),
            ("▣   Carteras & Riesgo", 4),
        ]
        for label, index in pages:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda checked=False, i=index: self.select_page(i))
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_layout.addStretch(1)

        status = QLabel("●  Simulación activa")
        status.setObjectName("statusBadge")
        sidebar_layout.addWidget(status)

        footer = QLabel("Local • Sin fondos reales")
        footer.setObjectName("sidebarFooter")
        sidebar_layout.addWidget(footer)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(
            self.market_service,
            self.portfolio_service,
            self.trading_service,
            self.refresh_all,
        )
        self.market_page = MarketPage(self.market_service)
        self.assets_page = AssetsPage(self.market_service, self.refresh_all)
        self.orders_page = OrdersPage(
            self.market_service,
            self.portfolio_service,
            self.trading_service,
            self.refresh_all,
        )
        self.portfolios_page = PortfoliosPage(
            self.market_service,
            self.portfolio_service,
            self.refresh_all,
        )

        for page in [
            self.dashboard_page,
            self.market_page,
            self.assets_page,
            self.orders_page,
            self.portfolios_page,
        ]:
            self.stack.addWidget(page)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.select_page(0)

    def _load_styles(self) -> None:
        qss = Path(__file__).with_name("styles.qss")
        self.setStyleSheet(qss.read_text(encoding="utf-8"))

    def _start_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start()

    def select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_all(self) -> None:
        self.market_service.actualizar_mercado()
        self.dashboard_page.refresh()
        self.market_page.refresh()
        self.assets_page.refresh()
        self.orders_page.refresh()
        self.portfolios_page.refresh()

    def closeEvent(self, event) -> None:
        self.manager.stop()
        event.accept()
```

## `ui/market_page.py`

```python
"""Pantalla de mercado."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class MarketPage(QWidget):
    def __init__(self, market_service) -> None:
        super().__init__()
        self.market_service = market_service
        self.previous: dict[tuple[str, str], float] = {}
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(14)
        title = QLabel("Mercado")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Precios normalizados mediante Adapter desde tres APIs simuladas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Activo", "Símbolo", "Tipo", "Exchange", "Precio", "Variación"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        rows = self.market_service.tabla_mercado(self.previous)
        self.table.setRowCount(len(rows))
        current: dict[tuple[str, str], float] = {}
        for row_index, row in enumerate(rows):
            current[(row.exchange, row.activo)] = row.precio
            values = [
                row.activo,
                row.simbolo,
                row.tipo,
                f"Exchange {row.exchange}",
                f"${row.precio:,.2f}",
                f"{row.variacion:+.2f}%",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row_index, col, QTableWidgetItem(text))
        self.previous = current
        self.table.resizeColumnsToContents()
```

## `ui/orders_page.py`

```python
"""Pantalla de órdenes y Bridge."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class OrdersPage(QWidget):
    HEADERS = [
        "ID",
        "Fecha",
        "Tipo",
        "Lado",
        "Exchange",
        "Cartera",
        "Activo",
        "Cantidad",
        "Precio",
        "Objetivo",
        "Estado",
        "Total",
    ]

    def __init__(self, market_service, portfolio_service, trading_service, on_change) -> None:
        super().__init__()
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self.trading_service = trading_service
        self.on_change = on_change
        self._build()
        self._refresh_combos()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        title = QLabel("Órdenes")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Bridge separa tipo de orden y exchange; el formulario nunca conoce sus clases concretas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        group = QGroupBox("Nueva operación simulada")
        form = QFormLayout(group)
        self.side_combo = QComboBox()
        self.side_combo.addItems(["COMPRA", "VENTA"])
        self.type_combo = QComboBox()
        self.type_combo.addItems(["MARKET", "LIMIT", "STOP LOSS"])
        self.exchange_combo = QComboBox()
        self.portfolio_combo = QComboBox()
        self.asset_combo = QComboBox()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.000001, 1_000_000_000)
        self.quantity.setDecimals(6)
        self.quantity.setValue(0.1)
        self.target = QDoubleSpinBox()
        self.target.setRange(0.0001, 1_000_000_000)
        self.target.setDecimals(4)
        self.target.setSpecialValueText("Sin objetivo")
        self.target.setValue(0.0001)

        form.addRow("Lado", self.side_combo)
        form.addRow("Tipo de orden", self.type_combo)
        form.addRow("Exchange", self.exchange_combo)
        form.addRow("Cartera", self.portfolio_combo)
        form.addRow("Activo", self.asset_combo)
        form.addRow("Cantidad", self.quantity)
        form.addRow("Precio objetivo / activación", self.target)

        controls = QHBoxLayout()
        controls.addStretch()
        execute = QPushButton("Crear y ejecutar")
        execute.setObjectName("primaryButton")
        execute.clicked.connect(self.submit)
        controls.addWidget(execute)
        form.addRow("", controls)
        layout.addWidget(group)

        history_label = QLabel("Historial")
        history_label.setObjectName("sectionTitle")
        layout.addWidget(history_label)
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        self.type_combo.currentTextChanged.connect(self._toggle_target)
        self._toggle_target(self.type_combo.currentText())

    def _toggle_target(self, text: str) -> None:
        enabled = text != "MARKET"
        self.target.setEnabled(enabled)
        self.target.setVisible(enabled)

    def _refresh_combos(self) -> None:
        current_exchange = self.exchange_combo.currentText() or "A"
        current_portfolio = self.portfolio_combo.currentText()
        current_asset = self.asset_combo.currentText()

        self.exchange_combo.blockSignals(True)
        self.exchange_combo.clear()
        self.exchange_combo.addItems(["A", "B", "C"])
        exchange_index = self.exchange_combo.findText(current_exchange)
        self.exchange_combo.setCurrentIndex(exchange_index if exchange_index >= 0 else 0)
        self.exchange_combo.blockSignals(False)

        self.portfolio_combo.clear()
        self.portfolio_combo.addItems([p.nombre for p in self.portfolio_service.listar_carteras()])
        portfolio_index = self.portfolio_combo.findText(current_portfolio)
        if portfolio_index >= 0:
            self.portfolio_combo.setCurrentIndex(portfolio_index)

        self.asset_combo.clear()
        self.asset_combo.addItems([a.nombre for a in self.market_service.obtener_activos()])
        asset_index = self.asset_combo.findText(current_asset)
        if asset_index >= 0:
            self.asset_combo.setCurrentIndex(asset_index)

    def submit(self) -> None:
        type_text = self.type_combo.currentText()
        target = None if type_text == "MARKET" else self.target.value()
        try:
            platform, registro = self.trading_service.crear_orden(
                type_text,
                self.side_combo.currentText(),
                self.exchange_combo.currentText(),
                self.asset_combo.currentText(),
                self.quantity.value(),
                self.portfolio_combo.currentText(),
                target,
            )
            self.trading_service.ejecutar_orden(platform, registro)
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(self, "Orden rechazada", str(exc))
            return

        message = registro.mensaje or "Operación procesada."
        if registro.estado.value == "EJECUTADA":
            QMessageBox.information(self, "Orden procesada", message)
        else:
            QMessageBox.information(self, "Orden pendiente", message)
        self.refresh()
        self.on_change()

    def refresh(self) -> None:
        self._refresh_combos()
        history = self.trading_service.historial()
        self.table.setRowCount(len(history))
        for row, order in enumerate(history):
            values = order.to_row()
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
```

## `ui/portfolios_page.py`

```python
"""Carteras, Prototype y módulo de riesgo."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QLineEdit,
)


class PortfoliosPage(QWidget):
    def __init__(self, market_service, portfolio_service, on_change) -> None:
        super().__init__()
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self.on_change = on_change
        # Controla si los campos de riesgo contienen cambios que todavía
        # no deben ser reemplazados por el refresco periódico de la UI.
        self._risk_dirty = False
        self._editing_portfolio: str | None = None
        self._loading_risk_fields = False
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        title = QLabel("Carteras & Riesgo")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Prototype para clonar estrategias y configurar límites de exposición y pérdidas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        top = QHBoxLayout()
        top.setSpacing(14)

        clone_group = QGroupBox("Clonar cartera")
        clone_form = QFormLayout(clone_group)
        self.clone_name = QLineEdit()
        self.clone_name.setPlaceholderText("Ej. Cartera Conservadora")
        self.clone_pct = QDoubleSpinBox()
        self.clone_pct.setRange(0, 100)
        self.clone_pct.setSuffix(" %")
        self.clone_pct.setValue(50)
        clone_button = QPushButton("Clonar")
        clone_button.setObjectName("primaryButton")
        clone_button.clicked.connect(self.clone)
        clone_form.addRow("Nombre", self.clone_name)
        clone_form.addRow("Porcentaje", self.clone_pct)
        clone_form.addRow("", clone_button)

        risk_group = QGroupBox("Configuración de riesgo")
        risk_form = QFormLayout(risk_group)
        self.portfolio_combo = QComboBox()
        self.exposure = self._percent_spin(50)
        self.loss = self._percent_spin(10)
        self.stop_loss = self._percent_spin(5)
        self.take_profit = self._percent_spin(10)
        save_button = QPushButton("Guardar riesgo")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.save_risk)
        risk_form.addRow("Cartera", self.portfolio_combo)
        risk_form.addRow("Límite exposición", self.exposure)
        risk_form.addRow("Límite pérdida", self.loss)
        risk_form.addRow("Stop Loss", self.stop_loss)
        risk_form.addRow("Take Profit", self.take_profit)
        risk_form.addRow("", save_button)

        top.addWidget(clone_group, 1)
        top.addWidget(risk_group, 1)
        layout.addLayout(top)

        summary = QHBoxLayout()
        self.balance_label = QLabel("—")
        self.risk_label = QLabel("—")
        self.balance_label.setObjectName("infoCard")
        self.risk_label.setObjectName("infoCard")
        summary.addWidget(self.balance_label)
        summary.addWidget(self.risk_label)
        layout.addLayout(summary)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Activo", "Cantidad", "Precio promedio", "Valor mercado", "% cartera"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        self.portfolio_combo.currentTextChanged.connect(self._on_portfolio_changed)
        for field in (self.exposure, self.loss, self.stop_loss, self.take_profit):
            field.valueChanged.connect(self._mark_risk_dirty)

    @staticmethod
    def _percent_spin(value: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 100)
        spin.setDecimals(2)
        spin.setSuffix(" %")
        spin.setValue(value)
        return spin

    def clone(self) -> None:
        try:
            clone = self.portfolio_service.clonar_cartera(self.clone_name.text(), self.clone_pct.value())
        except ValueError as exc:
            QMessageBox.warning(self, "No se pudo clonar", str(exc))
            return
        QMessageBox.information(self, "Prototype", f"{clone.nombre} fue creada desde la cartera prototipo.")
        self.clone_name.clear()
        self.refresh()
        cloned_index = self.portfolio_combo.findText(clone.nombre)
        if cloned_index >= 0:
            self.portfolio_combo.setCurrentIndex(cloned_index)
        self.on_change()

    def _mark_risk_dirty(self) -> None:
        if self._loading_risk_fields:
            return
        self._risk_dirty = True
        self._editing_portfolio = self.portfolio_combo.currentText() or None

    def _set_risk_fields_from_model(self, cartera) -> None:
        """Carga los valores persistidos sin generar cambios pendientes."""
        self._loading_risk_fields = True
        try:
            self.exposure.setValue(cartera.limite_exposicion)
            self.loss.setValue(cartera.limite_perdida)
            self.stop_loss.setValue(cartera.stop_loss)
            self.take_profit.setValue(cartera.take_profit)
        finally:
            self._loading_risk_fields = False
        self._risk_dirty = False
        self._editing_portfolio = cartera.nombre

    def _on_portfolio_changed(self) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            return

        # Cambiar de cartera significa trabajar con la configuración de esa
        # cartera. Los cambios no guardados se descartan únicamente al
        # seleccionar otra cartera; el refresco automático nunca los pisa.
        cartera = self.portfolio_service.obtener_cartera(name)
        self._set_risk_fields_from_model(cartera)
        self._refresh_table(cartera)

    def save_risk(self) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            QMessageBox.warning(self, "Riesgo inválido", "Selecciona una cartera antes de guardar.")
            return

        try:
            self.portfolio_service.configurar_riesgo(
                name,
                self.exposure.value(),
                self.loss.value(),
                self.stop_loss.value(),
                self.take_profit.value(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Riesgo inválido", str(exc))
            return

        # Los valores ya están escritos en la instancia Cartera concreta.
        # Al marcar como limpio antes del refresco, el QTimer puede actualizar
        # la tabla sin volver a tratar la edición como si fueran valores nuevos.
        self._risk_dirty = False
        self._editing_portfolio = name
        QMessageBox.information(self, "Riesgo", f"La configuración de {name} fue actualizada y guardada.")
        self.refresh()
        self.on_change()

    def load_selected(self, force: bool = False) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            return
        cartera = self.portfolio_service.obtener_cartera(name)

        # Durante la edición, el refresco periódico solo actualiza la información
        # calculada. No vuelve a escribir los controles con los valores del modelo.
        editing_same_portfolio = self._risk_dirty and self._editing_portfolio == name
        if force or not editing_same_portfolio:
            self._set_risk_fields_from_model(cartera)

        self._refresh_table(cartera)

    def _refresh_table(self, cartera) -> None:
        prices = {
            position.nombre: self.market_service.obtener_precio(position.nombre, "A")
            for position in cartera.activos
        }
        total = cartera.valor_total_usd(prices)
        activos_valor = cartera.valor_activos(prices)
        self.balance_label.setText(
            f"Saldo: ${cartera.saldo_usd:,.2f} USD  •  Activos: ${activos_valor:,.2f} USD  •  Total: ${total:,.2f} USD"
        )
        riesgo = self.portfolio_service.evaluar_riesgo(cartera, prices)
        self.risk_label.setText(
            f"Exposición: {riesgo['exposicion_pct']:.2f}%  •  Drawdown: {riesgo['drawdown_pct']:.2f}%  •  SL {cartera.stop_loss:.2f}%  •  TP {cartera.take_profit:.2f}%"
        )

        self.table.setRowCount(len(cartera.activos))
        for row, position in enumerate(cartera.activos):
            actual = prices.get(position.nombre, position.precio_promedio)
            value = position.cantidad * actual
            exposure = value / activos_valor * 100 if activos_valor else 0.0
            values = [
                position.nombre,
                f"{position.cantidad:g}",
                f"${position.precio_promedio:,.2f}",
                f"${value:,.2f}",
                f"{exposure:.2f}%",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def refresh(self) -> None:
        current = self.portfolio_combo.currentText()
        self.portfolio_combo.blockSignals(True)
        self.portfolio_combo.clear()
        self.portfolio_combo.addItems([p.nombre for p in self.portfolio_service.listar_carteras()])
        if current:
            index = self.portfolio_combo.findText(current)
            if index >= 0:
                self.portfolio_combo.setCurrentIndex(index)
        self.portfolio_combo.blockSignals(False)

        self.load_selected()
```

## `tests/test_patterns.py`

```python
from models.asset import Criptomoneda, NFT
from models.portfolio import Cartera, Posicion
from patterns.abstract_factory import FabricaExchangeA, FabricaExchangeB
from patterns.bridge import ExchangeAExecutor, ExchangeBExecutor, OrdenLimit, OrdenMarket
from patterns.composite import GrupoActivos, PosicionActivo, construir_composite
from patterns.decorator import MercadoConAuditoria
from patterns.factory_method import CreadorCriptomoneda, CreadorNFT
from patterns.prototype import clonar_cartera, crear_cartera_principal, crear_gestor_carteras
from patterns.singleton import ExchangeConnectionManager


def test_singleton_is_unique():
    ExchangeConnectionManager.reset_for_tests()
    a = ExchangeConnectionManager()
    b = ExchangeConnectionManager()
    assert a is b


def test_factory_method_creates_expected_products():
    btc = CreadorCriptomoneda().crear_activo("Bitcoin", 60000, "BTC")
    nft = CreadorNFT().crear_activo("Art", 100, "ART")
    assert isinstance(btc, Criptomoneda)
    assert isinstance(nft, NFT)


def test_abstract_factory_creates_market_and_executor():
    factory = FabricaExchangeA()
    assert factory.crear_mercado() is not None
    assert isinstance(factory.crear_orden(), ExchangeAExecutor)
    assert isinstance(FabricaExchangeB().crear_orden(), ExchangeBExecutor)


def test_bridge_market_executes_without_exchange_specific_class():
    factory = FabricaExchangeA()
    order = OrdenMarket(factory.crear_orden())
    asset = Criptomoneda("Bitcoin", 60000, "BTC")
    result = order.ejecutar(asset, "COMPRA", 0.1, 60000)
    assert result.status.value == "EJECUTADA"


def test_limit_order_can_remain_pending():
    factory = FabricaExchangeA()
    order = OrdenLimit(factory.crear_orden(), 59000)
    asset = Criptomoneda("Bitcoin", 60000, "BTC")
    result = order.ejecutar(asset, "COMPRA", 0.1, 60000)
    assert result.status.value == "PENDIENTE"


def test_prototype_clone_is_independent():
    principal = crear_cartera_principal()
    principal.recargar(1000, "USD")
    gestor = crear_gestor_carteras(principal)
    clon = clonar_cartera(gestor, "Conservadora", 50)
    clon.saldo_usd = 10
    assert principal.saldo_usd == 1000
    assert clon.saldo_usd == 10


def test_nft_rejects_quantity_other_than_one():
    factory = FabricaExchangeA()
    order = OrdenMarket(factory.crear_orden())
    nft = CreadorNFT().crear_activo("Art", 100, "ART")
    try:
        order.ejecutar(nft, "COMPRA", 2, 100)
    except ValueError as exc:
        assert "uno en uno" in str(exc)
    else:
        raise AssertionError("NFT should reject quantity different from 1")


def test_cloned_portfolio_keeps_own_risk_configuration():
    from services.portfolio_service import PortfolioService

    service = PortfolioService()
    conservadora = service.clonar_cartera("Conservadora", 50)
    agresiva = service.clonar_cartera("Agresiva", 80)

    service.configurar_riesgo("Conservadora", 35, 8, 4, 12)
    service.configurar_riesgo("Agresiva", 80, 25, 10, 30)

    assert conservadora.limite_exposicion == 35
    assert conservadora.limite_perdida == 8
    assert conservadora.stop_loss == 4
    assert conservadora.take_profit == 12

    assert agresiva.limite_exposicion == 80
    assert agresiva.limite_perdida == 25
    assert agresiva.stop_loss == 10
    assert agresiva.take_profit == 30

    principal = service.obtener_cartera("Cartera Principal")
    assert principal.limite_exposicion == 50
    assert principal.limite_perdida == 10
    assert principal.stop_loss == 5
    assert principal.take_profit == 10


def test_composite_aggregates_leaf_positions_and_nested_groups():
    cartera = Cartera("Cartera de prueba")
    cartera.activos.extend([
        Posicion("Bitcoin", 0.1, 60000),
        Posicion("Ethereum", 2, 3000),
    ])

    root = construir_composite(cartera)
    grupo_crypto = GrupoActivos("Cripto")
    for componente in root.componentes:
        grupo_crypto.agregar(componente)

    nested = GrupoActivos("Resumen")
    nested.agregar(grupo_crypto)

    assert root.valor({"Bitcoin": 61000, "Ethereum": 3200}) == 12500
    assert nested.valor({"Bitcoin": 61000, "Ethereum": 3200}) == 12500
    assert nested.cantidad_componentes() == 2


def test_decorator_adds_market_audit_without_changing_price():
    from patterns.adapter import ExchangeAAdapter

    manager = ExchangeConnectionManager()
    manager.reset_for_tests()
    from patterns.adapter import ApiExchangeA

    manager = ExchangeConnectionManager()
    adapter = ExchangeAAdapter(ApiExchangeA(manager))
    decorated = MercadoConAuditoria(adapter, "A")
    asset = Criptomoneda("Bitcoin", 60000, "BTC")

    price = decorated.consultar_precio(asset)
    audit = decorated.resumen()

    assert price == 60000.0
    assert audit["exchange"] == "A"
    assert audit["consultas"] == 1
    assert audit["ultima_consulta"]["activo"] == "Bitcoin"
```
