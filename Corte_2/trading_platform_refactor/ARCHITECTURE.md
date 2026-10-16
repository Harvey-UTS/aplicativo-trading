# Arquitectura e integración de patrones

## Flujo principal

```text
PySide6
  │
  ▼
UI pages
  │
  ▼
TradingPlatformFacade
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
| Nuevo patrón | `patterns/composite.py` + `services/portfolio_service.py` | agrupación jerárquica de posiciones |
| Nuevo patrón | `patterns/decorator.py` + `services/market_service.py` | trazabilidad de consultas de mercado |
| Nuevo patrón | `patterns/facade.py` + `ui/main_window.py` y páginas | punto de acceso unificado a mercado, órdenes y carteras |
| Nuevo patrón | `patterns/flyweight.py` + `patterns/adapter.py` | reutilización de metadata inmutable de pares de mercado |
| Nuevo patrón | `patterns/proxy.py` + `services/market_service.py` | acceso validado e inicialización diferida de adapters |

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

## Composite
`PosicionActivo` es la hoja del árbol y `GrupoActivos` es el compuesto. `PortfolioService` construye el árbol de la cartera y lo utiliza para calcular valor y cantidad de posiciones mediante una interfaz común.

## Decorator
`MercadoConAuditoria` envuelve cualquier implementación de `Mercado` y registra las consultas realizadas sin modificar `ExchangeAAdapter`, `ExchangeBAdapter` ni `ExchangeCAdapter`. `MarketService` conserva una instancia decorada por exchange.

## Facade
`TradingPlatformFacade` crea y coordina `MarketService`, `TradingService` y
`PortfolioService`, y ofrece a las páginas una interfaz de alto nivel. La UI deja
de instanciar o coordinar directamente los servicios. `crear_y_ejecutar_orden()`
encapsula la secuencia habitual de construcción y ejecución, sin duplicar la
lógica de validación ni los patrones que ya utilizan los servicios.

## Flyweight
`ParMercadoFactory` mantiene una caché thread-safe de objetos inmutables `ParMercadoFlyweight`, identificados por símbolo base y divisa de cotización. Los tres adapters obtienen el par normalizado desde la fábrica; la selección del exchange y el precio continúan siendo estado externo al flyweight.

## Proxy
`MarketService` construye un `MercadoProxy` por exchange y lo envuelve con `MercadoConAuditoria`. El proxy valida el activo y crea el adapter real durante la primera consulta válida. Después reutiliza el target ya creado; el Decorator registra las consultas sin asumir la responsabilidad de inicialización.

## Servicios

### `MarketService`
Controla el catálogo de activos, Factory Method, fábricas de mercado, Flyweight, Proxy, adapters, Decorator y caché Singleton.

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
