# Trading MultiExchange — Refactor académico

Aplicación local de simulación de trading para criptomonedas, tokens y NFT.
La refactorización parte de los ejercicios del proyecto original y los convierte
en una arquitectura modular con PySide6, servicios y catorce patrones GoF.

## Estructura

```text
trading_platform/
├── main.py
├── patterns/
│   ├── singleton.py
│   ├── factory_method.py
│   ├── abstract_factory.py
│   ├── prototype.py
│   ├── builder.py
│   ├── bridge.py
│   ├── adapter.py
│   ├── composite.py
│   ├── decorator.py
│   ├── facade.py
│   ├── flyweight.py
│   ├── proxy.py
│   ├── command.py
│   └── chain_of_responsibility.py
├── services/
│   ├── trading_service.py
│   ├── market_service.py
│   ├── portfolio_service.py
│   └── order_pattern_service.py
├── models/
│   ├── asset.py
│   ├── order.py
│   └── portfolio.py
├── ui/
│   ├── main_window.py
│   ├── dashboard_page.py
│   ├── assets_page.py
│   ├── orders_page.py
│   ├── portfolios_page.py
│   ├── market_page.py
│   └── styles.qss
├── docs/
│   └── uml/
│       ├── flyweight.dot
│       ├── flyweight.png
│       ├── proxy.dot
│       ├── proxy.png
│       ├── command.dot
│       ├── command.png
│       ├── chain_of_responsibility.dot
│       └── chain_of_responsibility.png
├── resources/
│   ├── icons/
│   └── images/
├── requirements.txt
└── README.md
```

## Ejecución

Requiere Python 3.10+.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar:

```bash
python main.py
```

No se utiliza ninguna entrada de consola para operar la plataforma.

## Integración de patrones

### Singleton — `ExchangeConnectionManager`
Mantiene una única instancia, un caché centralizado de precios simulados y la
actualización del mercado. Los demás componentes consultan este administrador
en vez de abrir múltiples fuentes de datos.

### Factory Method
`CreadorCriptomoneda`, `CreadorToken` y `CreadorNFT` encapsulan la creación de
`ActivoDigital`. La interfaz gráfica solicita el tipo y delega la construcción
al servicio.

### Abstract Factory
`FabricaExchangeA`, `FabricaExchangeB` y `FabricaExchangeC` crean familias de
productos compatibles: mercado + executor. A y B conservan los nombres del
avance original; C se incorpora para completar la demostración del Adapter.

### Prototype
`Cartera` implementa `clonar()` y `GestorCarteras` crea variantes como cartera
conservadora/agresiva sin reconstruir la composición base.

### Builder
`PlataformaTradingBuilder` integra Singleton, Factory Method, Abstract Factory,
Prototype y Bridge para ensamblar escenarios de trading completos.

### Bridge
`OrdenMarket`, `OrdenLimit` y `OrdenStopLoss` son la abstracción. `ExchangeAExecutor`,
`ExchangeBExecutor` y `ExchangeCExecutor` son implementaciones independientes.
No existen clases combinadas del tipo `OrdenMarketExchangeA`.

### Adapter
`ApiExchangeA`, `ApiExchangeB` y `ApiExchangeC` simulan APIs con estructuras
incompatibles. Sus adapters normalizan todo a `Mercado.consultar_precio(activo)`.

### Composite
`GrupoActivos` compone `PosicionActivo` para representar las posiciones de una
cartera mediante una estructura jerárquica. `PortfolioService` usa el árbol para
calcular de forma uniforme el valor y la cantidad de posiciones, dejando abierta
la posibilidad de agrupar futuras subcarteras o categorías.

### Decorator
`MercadoConAuditoria` envuelve el contrato `Mercado` sin modificar los adapters.
Añade trazabilidad de las consultas de precio (exchange, activo, precio, cantidad
de consultas y última consulta) y `MarketService` utiliza el mercado decorado como
punto de acceso a los precios. Esta auditoría también se visualiza directamente en
el Dashboard principal mediante la tabla **Auditoría de mercado (Decorator)**,
donde se muestran las consultas acumuladas, el último activo consultado, el último
precio y la fecha/hora de la última consulta para cada exchange.

### Facade — `TradingPlatformFacade`
Centraliza el acceso de la interfaz a `MarketService`, `PortfolioService` y
`TradingService`. `MainWindow` construye una sola fachada y la comparte con todas
las páginas; así la interfaz no instancia ni coordina los servicios por separado.
El método `crear_y_ejecutar_orden()` reúne la creación y ejecución de una orden en
una operación de alto nivel, mientras la validación de riesgo, el Builder y los
patrones especializados permanecen en sus servicios originales.


### Flyweight — `ParMercadoFlyweight` y `ParMercadoFactory`
La fábrica conserva una instancia inmutable por combinación de símbolo base y moneda de cotización. Los adapters de los exchanges reutilizan el mismo objeto para pares como `BTC/USDT`, mientras que cada adapter sigue consultando los precios de su propio exchange. El registro compartido está protegido frente a accesos concurrentes.

### Proxy — `MercadoProxy`
El servicio de mercado coloca un proxy virtual antes de cada adapter y mantiene la misma interfaz `Mercado.consultar_precio(activo)`. El proxy valida el tipo de activo y crea el adapter real solo cuando llega la primera consulta válida; las siguientes llamadas reutilizan el objeto inicializado. `MercadoConAuditoria` permanece por fuera para registrar las consultas completadas, manteniendo separadas la inicialización diferida y la trazabilidad.

### Command — `ComandoEjecutarOrden` e `InvocadorOrdenes`
El comando encapsula los parámetros de compra o venta y delega la creación y ejecución a `TradingPlatformFacade`, que actúa como receptor utilizando sus operaciones públicas existentes (`crear_orden()` y `ejecutar_orden()`). `InvocadorOrdenes` centraliza el despacho y mantiene un historial de comandos completados; cada objeto conserva su resultado para evitar que la misma instancia vuelva a ejecutar una operación. `ServicioDespachoOrdenes` conecta el comando con la pantalla después de superar la cadena de validación.

### Chain of Responsibility — `CadenaValidacionOrden`
La cadena de validación previa revisa los datos generales de la solicitud, las reglas de cantidad del activo, la cartera seleccionada y el precio objetivo de las órdenes Limit y Stop Loss. Cada manejador detiene la solicitud cuando encuentra un error o la delega al siguiente. `ServicioDespachoOrdenes` ejecuta estas comprobaciones antes de crear el comando; las validaciones de saldo y riesgo existentes permanecen en `PortfolioService`.

## Capas

```text
PySide6 UI
   ↓
TradingPlatformFacade
   ↓
MarketService · TradingService · PortfolioService
   ↓
Patterns + Models
```

Para la pantalla de órdenes se incorpora un flujo específico: `OrdersPage` delega en
`ServicioDespachoOrdenes`, que ejecuta primero Chain of Responsibility y, si la
solicitud es válida, despacha un `ComandoEjecutarOrden`. El comando utiliza las
operaciones públicas ya existentes de `TradingPlatformFacade`; no reemplaza ni
modifica `TradingService`, `Bridge` ni los demás patrones establecidos.

La lógica de negocio no usa `input()`, `print()`, menús de consola ni ciclos
`while True`. `main.py` se limita a inicializar la aplicación Qt.

## Persistencia de riesgo durante la edición

Cada instancia de `Cartera` mantiene su propia configuración de exposición,
pérdida, Stop Loss y Take Profit. El refresco periódico de mercado no reemplaza
los valores que el usuario está editando; estos solo pasan a estado persistido
en memoria de la cartera concreta al pulsar **Guardar riesgo**. Al cambiar de
cartera, la interfaz carga la configuración propia de esa cartera.

Después de crear una cartera clonada, la interfaz la selecciona automáticamente
para que pueda configurarse de inmediato.

## Alcance académico

La plataforma es una simulación local. No envía órdenes reales, no custodia
credenciales de exchanges y no gestiona fondos financieros reales.

