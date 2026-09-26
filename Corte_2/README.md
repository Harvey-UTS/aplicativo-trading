# Plataforma de Trading Multiexchange

Proyecto académico para el diseño y desarrollo de una plataforma local de simulación de operaciones de trading con criptomonedas, tokens y NFT.

El repositorio se encuentra organizado por cortes académicos:

```text
aplicativo-trading/
├── Corte_1/
├── Corte_2/
└── README.md
```

Este documento presenta la información general del proyecto y, principalmente, el procedimiento completo para **clonar, configurar y ejecutar el Segundo Corte**.

---

## 1. Repositorio

Repositorio oficial del proyecto:

**https://github.com/Harvey-UTS/aplicativo-trading.git**

El repositorio contiene actualmente las carpetas `Corte_1` y `Corte_2`.

---

## 2. Descripción del Segundo Corte

El Segundo Corte contiene una versión refactorizada de la plataforma de trading, estructurada de forma modular y orientada a la aplicación de patrones de diseño.

La aplicación es **local y de carácter académico**. Permite simular la gestión de activos digitales, carteras y operaciones de compra y venta sin utilizar dinero real ni ejecutar órdenes reales en exchanges.

La implementación utiliza **Python** y una interfaz gráfica desarrollada con **PySide6**. El proyecto requiere Python 3.10 o superior y su archivo `requirements.txt` contiene la dependencia principal `PySide6>=6.7,<7`.

---

## 3. Estructura del Segundo Corte

La estructura relevante para ejecutar la aplicación es la siguiente:

```text
Corte_2/
└── trading_platform_refactor/
    ├── main.py
    ├── patterns/
    │   ├── singleton.py
    │   ├── factory_method.py
    │   ├── abstract_factory.py
    │   ├── prototype.py
    │   ├── builder.py
    │   ├── bridge.py
    │   └── adapter.py
    ├── services/
    │   ├── trading_service.py
    │   ├── market_service.py
    │   └── portfolio_service.py
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
    ├── resources/
    │   ├── icons/
    │   └── images/
    ├── tests/
    ├── requirements.txt
    ├── ARCHITECTURE.md
    └── README.md
```

Los archivos `main.py`, `requirements.txt` y la arquitectura modular hacen parte del Segundo Corte publicado en el repositorio.

---

# 4. Requisitos previos

Antes de comenzar, es necesario tener instalado en el equipo:

- **Git** para clonar el repositorio.
- **Python 3.10 o superior**.
- **CMD de Windows** o una terminal equivalente.

Para comprobar que las herramientas están instaladas correctamente, abrir CMD y ejecutar:

```cmd
git --version
python --version
```

Debería mostrarse una versión de Git y una versión de Python igual o superior a 3.10.

> **Nota:** si el comando `python` no funciona, en algunos equipos de Windows puede utilizarse `py` en su lugar.

---

# 5. Clonar el repositorio desde GitHub

Abrir **CMD** y ubicarse en la carpeta donde se desea guardar el proyecto.

Por ejemplo:

```cmd
cd C:\Users\TuUsuario\Documents
```

Luego clonar el repositorio:

```cmd
git clone https://github.com/Harvey-UTS/aplicativo-trading.git
```

Cuando termine el proceso, Git habrá creado una carpeta llamada:

```text
aplicativo-trading
```

---

# 6. Entrar al Segundo Corte

Entrar primero al repositorio:

```cmd
cd aplicativo-trading
```

Después entrar a la carpeta del Segundo Corte:

```cmd
cd Corte_2
```

Finalmente, entrar a la carpeta que contiene la aplicación Python:

```cmd
cd trading_platform_refactor
```

La ruta final debe tener una estructura similar a:

```text
...
\aplicativo-trading\Corte_2\trading_platform_refactor
```

Para verificar que se encuentra en la ubicación correcta, ejecutar:

```cmd
dir
```

Entre los archivos mostrados deben aparecer, como mínimo:

```text
main.py
requirements.txt
```

> **Importante:** el comando para ejecutar la aplicación debe realizarse desde `trading_platform_refactor`, porque allí se encuentra `main.py`.

---

# 7. Crear el entorno virtual

Se recomienda utilizar un entorno virtual para mantener aisladas las dependencias del proyecto.

Desde la carpeta `trading_platform_refactor`, ejecutar:

```cmd
python -m venv .venv
```

Esto creará una carpeta llamada `.venv` dentro del proyecto.

La estructura quedará aproximadamente así:

```text
trading_platform_refactor/
├── .venv/
├── main.py
├── requirements.txt
├── patterns/
├── services/
├── models/
└── ui/
```

---

# 8. Activar el entorno virtual en Windows CMD

Ejecutar:

```cmd
.venv\Scripts\activate
```

Si la activación fue correcta, normalmente aparecerá `(.venv)` al inicio de la línea de comandos. Por ejemplo:

```text
(.venv) C:\Users\TuUsuario\Documents\aplicativo-trading\Corte_2\trading_platform_refactor>
```

A partir de este momento, los paquetes instalados quedarán asociados al entorno virtual del proyecto.

---

# 9. Instalar las dependencias

Con el entorno virtual activo, ejecutar:

```cmd
python -m pip install -r requirements.txt
```

El archivo `requirements.txt` del Segundo Corte especifica actualmente:

```txt
PySide6>=6.7,<7
```

Por lo tanto, se instalará una versión compatible de PySide6 dentro del rango definido por el proyecto.

Para comprobar que PySide6 quedó instalado, puede ejecutarse:

```cmd
python -c "import PySide6; print(PySide6.__version__)"
```

Si el comando devuelve un número de versión, la dependencia está disponible correctamente.

---

# 10. Ejecutar la aplicación

Con el entorno virtual activo y las dependencias instaladas, ejecutar:

```cmd
python main.py
```

La aplicación abrirá su interfaz gráfica de escritorio mediante **PySide6**. El `main.py` funciona como punto de entrada de la aplicación e inicializa la interfaz Qt.

La ejecución normal no requiere introducir comandos, opciones ni datos mediante la consola; la interacción se realiza desde la interfaz gráfica.

---

# 11. Flujo completo en CMD

Para ejecutar el Segundo Corte desde un equipo nuevo, la secuencia completa puede realizarse de esta manera:

```cmd
git clone https://github.com/Harvey-UTS/aplicativo-trading.git
cd aplicativo-trading
cd Corte_2
cd trading_platform_refactor
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Este es el procedimiento recomendado para una instalación limpia en Windows.

---

# 12. Ejecución posterior del proyecto

Después de realizar la instalación inicial, **no es necesario volver a crear el entorno virtual ni reinstalar las dependencias cada vez**.

En futuras ejecuciones, basta con:

```cmd
cd ruta\al\proyecto\aplicativo-trading\Corte_2\trading_platform_refactor
.venv\Scripts\activate
python main.py
```

Al finalizar el trabajo, el entorno virtual puede cerrarse con:

```cmd
deactivate
```

---

# 13. Patrones de diseño implementados

El Segundo Corte integra diferentes patrones de diseño GoF dentro de la arquitectura de la plataforma:

### Singleton
`ExchangeConnectionManager` centraliza la gestión de la información de mercado simulada y mantiene una única instancia compartida.

### Factory Method
Los creadores de criptomonedas, tokens y NFT encapsulan la creación de los activos digitales.

### Abstract Factory
Las fábricas de exchange permiten crear familias compatibles de productos relacionados, como componentes de mercado y ejecución de órdenes.

### Prototype
`Cartera` permite crear nuevas carteras a partir de una existente mediante clonación.

### Builder
`PlataformaTradingBuilder` permite ensamblar diferentes componentes de la plataforma de forma estructurada.

### Bridge
Separa la abstracción del tipo de orden de la implementación encargada de ejecutar la orden en cada exchange simulado.

### Adapter
Adapta las diferentes estructuras de respuesta de las APIs simuladas para exponer una interfaz común de consulta de precios.

La documentación técnica y el mapa de integración de estos patrones se encuentran en `ARCHITECTURE.md`.

---

# 14. Arquitectura general

La aplicación está organizada por capas para separar la interfaz, los servicios, los patrones de diseño y los modelos:

```text
┌─────────────────────────────┐
│          PySide6 UI         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Services           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Patterns + Models       │
└─────────────────────────────┘
```

Esta separación facilita la organización, mantenimiento y reutilización de los componentes del proyecto.

---

# 15. Solución de problemas frecuentes

## `git` no se reconoce como comando

Verificar que Git esté instalado y disponible en el `PATH` del sistema. Después de instalarlo, cerrar y volver a abrir CMD.

## `python` no se reconoce como comando

Verificar la instalación de Python y su inclusión en el `PATH`. También puede probarse:

```cmd
py --version
```

Si `py` funciona, la creación del entorno puede realizarse con:

```cmd
py -m venv .venv
```

Y posteriormente:

```cmd
.venv\Scripts\activate
py -m pip install -r requirements.txt
py main.py
```

## Error al ejecutar `main.py`

Verificar que la terminal se encuentre dentro de:

```text
aplicativo-trading\Corte_2\trading_platform_refactor
```

Puede comprobarse con:

```cmd
cd
```

También revisar que exista el archivo `main.py`:

```cmd
dir main.py
```

## Error relacionado con `PySide6`

Verificar primero que el entorno virtual esté activo:

```cmd
.venv\Scripts\activate
```

Después reinstalar las dependencias:

```cmd
python -m pip install -r requirements.txt
```

---

# 16. Pruebas

El proyecto incluye una carpeta `tests` para las pruebas automatizadas asociadas a la implementación.

Con las dependencias instaladas, las pruebas pueden ejecutarse mediante:

```cmd
python -m pytest
```

Si `pytest` no está instalado en el entorno y se desea ejecutar estas pruebas, primero será necesario instalarlo por separado o agregarlo a las dependencias del proyecto.

---

# 17. Alcance académico

Esta aplicación corresponde a una **simulación local con fines académicos**.

El proyecto no realiza operaciones financieras reales, no administra fondos reales y no requiere credenciales reales de exchanges para su ejecución. Su finalidad es demostrar el funcionamiento de la arquitectura, los patrones de diseño y la simulación de operaciones dentro de un entorno controlado.

---

# 18. Autores

**Harvey David Redondo Méndez**  
**Arturo Hernandez Hernandez**

---

## Referencias del proyecto

- Repositorio: https://github.com/Harvey-UTS/aplicativo-trading
- Documentación de arquitectura: `Corte_2/trading_platform_refactor/ARCHITECTURE.md`
- Dependencias: `Corte_2/trading_platform_refactor/requirements.txt`
- Punto de entrada: `Corte_2/trading_platform_refactor/main.py`
