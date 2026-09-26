# Arquitectura e integración de patrones

## Flujo principal

```text
PySide6
  │
  ▼
UI pages
  │
  ▼
Services
  │
  ├── TradingService
  ├── MarketService
  └── PortfolioService
  │
  ▼
Patterns + Models
```

La UI nunca instancia directamente `Criptomoneda`, `Token`, `NFT`, APIs externas o executors de exchange.

## Mapa de la refactorización

| Ejercicio original | Refactor | Conservación |
|---|---|---|
| `1_Ejercicio.py` | `patterns/singleton.py` | `ExchangeConnectionManager` |
| `2_Ejercicio.py` | `models/asset.py` + `patterns/factory_method.py` | `ActivoDigital`, creadores y productos |
| `3_Ejercicio.py` | `patterns/abstract_factory.py` + `patterns/adapter.py` | `FabricaExchangeA/B`, mercado y executor |
| `4_Ejercicio.py` | `models/portfolio.py` + `patterns/prototype.py` | `Cartera`, `GestorCarteras`, helpers |
| `5_Ejercicio.py` | `patterns/builder.py` + `services/*` | `PlataformaTradingBuilder` y ensamblaje |

## Singleton

`ExchangeConnectionManager` mantiene un solo caché y la simulación de precios.
El servicio de mercado y los adapters consultan la misma instancia, evitando fuentes de datos independientes dentro de la aplicación.

## Factory Method

`CreadorCriptomoneda`, `CreadorToken` y `CreadorNFT` crean objetos mediante `crear_activo`.
La capa UI solo entrega datos al `MarketService`.

## Abstract Factory

Cada fábrica entrega una familia coherente:

```text
FabricaExchangeA ──► Mercado A + ExchangeAExecutor
FabricaExchangeB ──► Mercado B + ExchangeBExecutor
FabricaExchangeC ──► Mercado C + ExchangeCExecutor
```

Exchange C se agrega como extensión para completar la demostración de Adapter, sin sustituir A ni B.

## Prototype

`Cartera.clonar()` usa copia profunda. `GestorCarteras` conserva la cartera principal como prototipo y crea variantes a partir de ella.

## Builder

`PlataformaTradingBuilder` permite ensamblar:

1. Singleton
2. activo mediante Factory Method
3. fábrica de exchange mediante Abstract Factory
4. cartera/prototipo
5. orden Bridge

El resultado es `PlataformaTrading`.

## Bridge

La abstracción variable es el tipo de orden:

```text
OrdenTrading
 ├── OrdenMarket
 ├── OrdenLimit
 └── OrdenStopLoss
```

La implementación variable es el executor:

```text
EjecutorOrden
 ├── ExchangeAExecutor
 ├── ExchangeBExecutor
 └── ExchangeCExecutor
```

No existen combinaciones `OrdenMarketExchangeA`, etc.

## Adapter

Cada API simulada utiliza una estructura incompatible:

```text
ApiExchangeA → { lastPrice: ... }
ApiExchangeB → { data: { amount: ... } }
ApiExchangeC → { ticker: { last: ... } }
```

Los adapters transforman esas respuestas al contrato `Mercado.consultar_precio(activo)`.

## Servicios

### `MarketService`
Controla el catálogo de activos, Factory Method, fábricas de mercado, adapters y caché Singleton.

### `TradingService`
Construye y ejecuta órdenes, valida riesgo/capital, actualiza carteras y conserva historial.

### `PortfolioService`
Administra carteras, Prototype, saldos, posiciones y configuración de riesgo.

## Riesgo simulado

Se soportan:

- límite de exposición
- límite de pérdida
- Stop Loss por porcentaje de cartera
- Take Profit por porcentaje de cartera
- validación de saldo antes de compra
- validación de posición antes de venta

Los límites son de simulación académica; no representan órdenes financieras reales.

## Consola eliminada

La lógica de negocio no contiene:

- `input()`
- `print()`
- menús de consola
- `while True`

El único ciclo de eventos es el de Qt, gestionado por `QApplication`.

## Limitación de la validación en este entorno

El entorno de generación no dispone de `PySide6` instalado y no puede descargar dependencias externas. Por eso se verificaron sintaxis, imports estructurales, patrones y servicios mediante pruebas automatizadas; la ejecución visual de Qt queda para el entorno donde se instale `requirements.txt`.
