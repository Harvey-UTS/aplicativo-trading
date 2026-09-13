import importlib.util
import os


# ============================================================
# CARGAR LOS CUATRO PATRONES EXISTENTES
# ============================================================

def cargar_modulo(nombre, archivo):
    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        archivo
    )

    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No se encontró el archivo requerido: {ruta}"
        )

    spec = importlib.util.spec_from_file_location(nombre, ruta)

    if spec is None or spec.loader is None:
        raise ImportError(
            f"No se pudo cargar el módulo: {ruta}"
        )

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    return modulo


singleton = cargar_modulo(
    "singleton",
    "1_Ejercicio.py"
)

factory_method = cargar_modulo(
    "factory_method",
    "2_Ejercicio.py"
)

abstract_factory = cargar_modulo(
    "abstract_factory",
    "3_Ejercicio.py"
)

prototype = cargar_modulo(
    "prototype",
    "4_Ejercicio.py"
)


# ============================================================
# COMPONENTES EXISTENTES
# ============================================================

# Singleton
ExchangeConnectionManager = singleton.ExchangeConnectionManager

# Factory Method
CreadorCriptomoneda = factory_method.CreadorCriptomoneda
CreadorToken = factory_method.CreadorToken
CreadorNFT = factory_method.CreadorNFT

# Abstract Factory
FabricaExchangeA = abstract_factory.FabricaExchangeA
FabricaExchangeB = abstract_factory.FabricaExchangeB

# Prototype
crear_cartera_principal = prototype.crear_cartera_principal
crear_gestor_carteras = prototype.crear_gestor_carteras
clonar_cartera = prototype.clonar_cartera


# ============================================================
# PRODUCTO FINAL
# ============================================================

class PlataformaTrading:
    """
    Producto construido mediante Builder.

    Mantiene las referencias de los componentes creados
    mediante los cuatro patrones existentes.
    """

    def __init__(
        self,
        sistema_ordenes=None,
        creador=None,
        activo=None,
        fabrica_exchange=None,
        cartera=None,
        gestor_carteras=None
    ):
        self.sistema_ordenes = sistema_ordenes
        self.creador = creador
        self.activo = activo
        self.fabrica_exchange = fabrica_exchange
        self.cartera = cartera
        self.gestor_carteras = gestor_carteras

    def recargar_cartera(self, monto, moneda):
        if self.cartera is None:
            print("\nNo existe una cartera configurada.")
            return

        self.cartera.recargar(monto, moneda)

    def configurar_riesgo(self, limite_exposicion, limite_perdida):
        if self.cartera is None:
            print("\nNo existe una cartera configurada.")
            return

        self.cartera.configurar_riesgo(
            limite_exposicion,
            limite_perdida
        )

        print("\nConfiguración de riesgo actualizada.")

    def clonar_cartera(self, nombre, porcentaje):
        if self.gestor_carteras is None:
            print("\nNo existe un gestor de carteras.")
            return None

        clon = clonar_cartera(
            self.gestor_carteras,
            nombre,
            porcentaje
        )

        if clon is not None:
            print("\nCartera clonada correctamente.")
            clon.mostrar()

        return clon

    def ejecutar_operacion(self, tipo, cantidad):
        if self.activo is None:
            print("\nNo existe un activo configurado.")
            return

        if self.fabrica_exchange is None:
            print("\nNo existe un exchange configurado.")
            return

        if self.cartera is None:
            print("\nNo existe una cartera configurada.")
            return

        mercado = self.fabrica_exchange.crear_mercado()
        orden = self.fabrica_exchange.crear_orden()

        precio = mercado.consultar_precio(self.activo)

        if precio == 0:
            print(
                "\nEl activo no está disponible "
                "en este exchange."
            )
            return

        self.activo.precio = precio

        print(
            f"\nPrecio del exchange: "
            f"${precio:,.2f}"
        )

        orden.ejecutar(
            self.activo,
            tipo,
            cantidad
        )

        if tipo.upper() == "COMPRA":
            self.cartera.registrar_compra(
                self.activo,
                cantidad,
                precio
            )

        elif tipo.upper() == "VENTA":
            self.cartera.registrar_venta(
                self.activo.nombre,
                cantidad
            )

    def mostrar(self):
        print("\n========================================")
        print("       PLATAFORMA DE TRADING")
        print("========================================")

        if self.activo is not None:
            print(
                f"Activo: {self.activo.nombre}"
            )
            print(
                f"Tipo: {type(self.activo).__name__}"
            )

        if self.fabrica_exchange is not None:
            print(
                "Exchange: "
                f"{type(self.fabrica_exchange).__name__}"
            )

        if self.cartera is not None:
            self.cartera.mostrar()


# ============================================================
# BUILDER
# ============================================================

class PlataformaTradingBuilder:
    """
    Builder encargado únicamente de ensamblar los componentes
    de los patrones existentes.
    """

    def __init__(self):
        self.sistema_ordenes = None
        self.creador = None
        self.activo = None
        self.fabrica_exchange = None
        self.cartera = None
        self.gestor_carteras = None

    # Singleton
    def configurar_singleton(self):
        self.sistema_ordenes = ExchangeConnectionManager()
        return self

    # Factory Method
    def configurar_operacion(
        self,
        tipo_activo,
        nombre,
        precio
    ):
        tipo_activo = tipo_activo.upper()

        if tipo_activo == "CRIPTO":
            self.creador = CreadorCriptomoneda()

        elif tipo_activo == "TOKEN":
            self.creador = CreadorToken()

        elif tipo_activo == "NFT":
            self.creador = CreadorNFT()

        else:
            raise ValueError(
                "Tipo de activo no válido. "
                "Use: CRIPTO, TOKEN o NFT."
            )

        self.activo = self.creador.crear_activo(
            nombre,
            precio
        )

        return self

    # Abstract Factory
    def configurar_exchange(self, exchange):
        exchange = str(exchange).upper()

        if exchange in ("A", "EXCHANGE A", "1"):
            self.fabrica_exchange = FabricaExchangeA()

        elif exchange in ("B", "EXCHANGE B", "2"):
            self.fabrica_exchange = FabricaExchangeB()

        else:
            raise ValueError(
                "Exchange no válido. Use A o B."
            )

        return self

    # Prototype
    def configurar_cartera(
        self,
        nombre="Cartera Principal",
        limite_exposicion=50.0,
        limite_perdida=10.0
    ):
        self.cartera = crear_cartera_principal(
            nombre,
            limite_exposicion,
            limite_perdida
        )

        self.gestor_carteras = crear_gestor_carteras(
            self.cartera
        )

        return self

    # Prototype - recarga mediante método existente
    def recargar_cartera(self, monto, moneda):
        if self.cartera is None:
            raise ValueError(
                "Primero debe configurar una cartera."
            )

        self.cartera.recargar(
            monto,
            moneda
        )

        return self

    # Prototype - clonación mediante función existente
    def clonar_cartera(self, nombre, porcentaje):
        if self.gestor_carteras is None:
            raise ValueError(
                "Primero debe configurar una cartera."
            )

        return clonar_cartera(
            self.gestor_carteras,
            nombre,
            porcentaje
        )

    def build(self):
        return PlataformaTrading(
            sistema_ordenes=self.sistema_ordenes,
            creador=self.creador,
            activo=self.activo,
            fabrica_exchange=self.fabrica_exchange,
            cartera=self.cartera,
            gestor_carteras=self.gestor_carteras
        )


# ============================================================
# FUNCIONES DE APOYO PARA LA DEMOSTRACIÓN
# ============================================================

def seleccionar_activo():
    print("\n========================================")
    print("       ACTIVOS DIGITALES DISPONIBLES")
    print("========================================")
    print("1. Bitcoin (Criptomoneda)")
    print("2. Ethereum (Criptomoneda)")
    print("3. Chainlink (Token)")
    print("4. Polygon (Token)")
    print("5. CryptoArt #001 (NFT)")

    opcion = input(
        "\nSeleccione un activo: "
    ).strip()

    activos = {
        "1": (
            "CRIPTO",
            "Bitcoin",
            60000.00
        ),
        "2": (
            "CRIPTO",
            "Ethereum",
            3000.00
        ),
        "3": (
            "TOKEN",
            "Chainlink",
            15.00
        ),
        "4": (
            "TOKEN",
            "Polygon",
            0.50
        ),
        "5": (
            "NFT",
            "CryptoArt #001",
            2500.00
        )
    }

    return activos.get(opcion)


def seleccionar_exchange():
    print("\n========================================")
    print("             EXCHANGE")
    print("========================================")
    print("1. Exchange A")
    print("2. Exchange B")

    opcion = input(
        "\nSeleccione el exchange: "
    ).strip()

    if opcion == "1":
        return "A"

    if opcion == "2":
        return "B"

    return None


def seleccionar_operacion():
    print("\n========================================")
    print("             OPERACIÓN")
    print("========================================")
    print("1. Comprar")
    print("2. Vender")

    opcion = input(
        "\nSeleccione una opción: "
    ).strip()

    if opcion == "1":
        return "COMPRA"

    if opcion == "2":
        return "VENTA"

    return None


# ============================================================
# FUNCIONES DEL MENÚ PRINCIPAL
# ============================================================

def confirmar_recarga():
    while True:
        respuesta = input(
            "\n¿Desea realizar una recarga? (s/n): "
        ).strip().lower()

        if respuesta in ("s", "n"):
            return respuesta == "s"

        print("Ingrese 's' para sí o 'n' para no.")


def recargar_desde_menu(plataforma):
    if not confirmar_recarga():
        print("\nRecarga cancelada.")
        return

    print("\n========================================")
    print("          RECARGAR CARTERA")
    print("========================================")
    print("1. Pesos colombianos (COP)")
    print("2. Dólares estadounidenses (USD)")

    opcion = input(
        "\nSeleccione la moneda: "
    ).strip()

    monedas = {
        "1": "COP",
        "2": "USD"
    }

    moneda = monedas.get(opcion)

    if moneda is None:
        print("\nMoneda no válida.")
        return

    try:
        monto = float(
            input("Ingrese el monto: ")
        )
    except ValueError:
        print("\nIngrese un monto numérico válido.")
        return

    if monto <= 0:
        print("\nEl monto debe ser mayor que cero.")
        return

    plataforma.recargar_cartera(
        monto,
        moneda
    )


def solicitar_cantidad(mensaje="\nIngrese la cantidad: "):
    try:
        cantidad = float(
            input(mensaje)
        )
    except ValueError:
        print("\nCantidad no válida.")
        return None

    if cantidad <= 0:
        print("\nLa cantidad debe ser mayor que cero.")
        return None

    return cantidad


def seleccionar_activo_en_cartera(cartera):
    if not cartera.activos:
        print("\nLa cartera está vacía.")
        return None

    print("\n========================================")
    print("          ACTIVOS EN CARTERA")
    print("========================================")

    for i, registro in enumerate(
        cartera.activos,
        start=1
    ):
        print(
            f"{i}. {registro[0]} | "
            f"Cantidad: {registro[1]}"
        )

    try:
        indice = int(
            input("\nSeleccione el activo: ")
        )
    except ValueError:
        print("\nSelección no válida.")
        return None

    if indice < 1 or indice > len(cartera.activos):
        print("\nActivo no válido.")
        return None

    return cartera.activos[indice - 1]


def obtener_tipo_activo(nombre):
    tipos = {
        "Bitcoin": "CRIPTO",
        "Ethereum": "CRIPTO",
        "Chainlink": "TOKEN",
        "Polygon": "TOKEN",
        "CryptoArt #001": "NFT"
    }

    return tipos.get(nombre)


def configurar_riesgo_desde_menu(plataforma):
    cartera = plataforma.cartera

    print("\n========================================")
    print("          CONFIGURAR RIESGO")
    print("========================================")
    print(
        f"Límite de exposición actual: "
        f"{cartera.limite_exposicion}%"
    )
    print(
        f"Límite de pérdida actual: "
        f"{cartera.limite_perdida}%"
    )

    try:
        exposicion = float(
            input("\nNuevo límite de exposición (%): ")
        )
        perdida = float(
            input("Nuevo límite de pérdida (%): ")
        )
    except ValueError:
        print("\nIngrese valores numéricos válidos.")
        return

    if not 0 <= exposicion <= 100:
        print("\nEl límite de exposición debe estar entre 0 y 100%.")
        return

    if not 0 <= perdida <= 100:
        print("\nEl límite de pérdida debe estar entre 0 y 100%.")
        return

    plataforma.configurar_riesgo(
        exposicion,
        perdida
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n========================================")
    print("       PLATAFORMA DE TRADING")
    print("          BUILDER - EJERCICIO 5")
    print("========================================")

    # La plataforma se construye una sola vez con los componentes
    # permanentes. El activo y el exchange se configuran únicamente
    # cuando el usuario compra o vende.
    builder = (
        PlataformaTradingBuilder()
        .configurar_singleton()
        .configurar_cartera(
            "Cartera Principal",
            50.0,
            10.0
        )
    )

    plataforma = builder.build()

    while True:
        print("\n========================================")
        print("               MENÚ")
        print("========================================")
        print("1. Recargar cartera")
        print("2. Comprar activo")
        print("3. Vender activo")
        print("4. Ver cartera")
        print("5. Clonar cartera")
        print("6. Configurar riesgo")
        print("7. Salir")
        print("========================================")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        # ----------------------------------------------------
        # 1. RECARGAR CARTERA
        # ----------------------------------------------------
        if opcion == "1":
            recargar_desde_menu(
                plataforma
            )

        # ----------------------------------------------------
        # 2. COMPRAR ACTIVO
        # ----------------------------------------------------
        elif opcion == "2":
            resultado_activo = seleccionar_activo()

            if resultado_activo is None:
                print("\nActivo no válido.")
                continue

            tipo_activo, nombre, precio = resultado_activo

            exchange = seleccionar_exchange()

            if exchange is None:
                print("\nExchange no válido.")
                continue

            cantidad = solicitar_cantidad()

            if cantidad is None:
                continue

            plataforma = (
                builder
                .configurar_operacion(
                    tipo_activo,
                    nombre,
                    precio
                )
                .configurar_exchange(exchange)
                .build()
            )

            plataforma.ejecutar_operacion(
                "COMPRA",
                cantidad
            )

        # ----------------------------------------------------
        # 3. VENDER ACTIVO
        # ----------------------------------------------------
        elif opcion == "3":
            registro = seleccionar_activo_en_cartera(
                plataforma.cartera
            )

            if registro is None:
                continue

            nombre = registro[0]
            cantidad_disponible = registro[1]
            precio_registrado = registro[2]

            cantidad = solicitar_cantidad(
                "Ingrese la cantidad a vender: "
            )

            if cantidad is None:
                continue

            if cantidad > cantidad_disponible:
                print(
                    "\nNo posee suficiente cantidad "
                    "del activo."
                )
                continue

            tipo_activo = obtener_tipo_activo(nombre)

            if tipo_activo is None:
                print("\nTipo de activo no reconocido.")
                continue

            exchange = seleccionar_exchange()

            if exchange is None:
                print("\nExchange no válido.")
                continue

            plataforma = (
                builder
                .configurar_operacion(
                    tipo_activo,
                    nombre,
                    precio_registrado
                )
                .configurar_exchange(exchange)
                .build()
            )

            plataforma.ejecutar_operacion(
                "VENTA",
                cantidad
            )

        # ----------------------------------------------------
        # 4. VER CARTERA
        # ----------------------------------------------------
        elif opcion == "4":
            plataforma.cartera.mostrar()

        # ----------------------------------------------------
        # 5. CLONAR CARTERA
        # ----------------------------------------------------
        elif opcion == "5":
            nombre_clon = input(
                "\nIngrese el nombre de la cartera clon: "
            ).strip()

            if not nombre_clon:
                print("\nEl nombre no puede estar vacío.")
                continue

            try:
                porcentaje = float(
                    input(
                        "Ingrese el porcentaje del saldo "
                        "para el clon (%): "
                    )
                )
            except ValueError:
                print("\nPorcentaje no válido.")
                continue

            if porcentaje < 0 or porcentaje > 100:
                print(
                    "\nEl porcentaje debe estar "
                    "entre 0% y 100%."
                )
                continue

            clon = plataforma.clonar_cartera(
                nombre_clon,
                porcentaje
            )

            if clon is None:
                print(
                    "\nNo fue posible crear "
                    "la cartera clon."
                )

        # ----------------------------------------------------
        # 6. CONFIGURAR RIESGO / MODIFICAR LÍMITES
        # ----------------------------------------------------
        elif opcion == "6":
            configurar_riesgo_desde_menu(
                plataforma
            )

        # ----------------------------------------------------
        # 7. SALIR
        # ----------------------------------------------------
        elif opcion == "7":
            if plataforma.sistema_ordenes is not None:
                plataforma.sistema_ordenes.stop()

            print("\nGracias por utilizar la plataforma.")
            break

        else:
            print("\nOpción no válida. Intente nuevamente.")


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()