from abc import ABC, abstractmethod
from copy import deepcopy
import importlib.util
import os


# ============================================================
# CARGAR ARCHIVOS ANTERIORES
# ============================================================

def cargar_modulo(nombre_modulo, archivo):
    """
    Carga un archivo .py externo sin copiar su código.
    """

    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        archivo
    )

    spec = importlib.util.spec_from_file_location(
        nombre_modulo,
        ruta
    )

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    return modulo


# ============================================================
# IMPORTAR SINGLETON
# 1_Ejercicio.py
# ============================================================

singleton = cargar_modulo(
    "singleton",
    "1_Ejercicio.py"
)

ExchangeConnectionManager = (
    singleton.ExchangeConnectionManager
)


# ============================================================
# IMPORTAR FACTORY METHOD
# 2_Ejercicio.py
# ============================================================

factory_method = cargar_modulo(
    "factory_method",
    "2_Ejercicio.py"
)

ActivoDigital = factory_method.ActivoDigital

Criptomoneda = factory_method.Criptomoneda
Token = factory_method.Token
NFT = factory_method.NFT

CreadorCriptomoneda = (
    factory_method.CreadorCriptomoneda
)

CreadorToken = (
    factory_method.CreadorToken
)

CreadorNFT = (
    factory_method.CreadorNFT
)


# ============================================================
# IMPORTAR ABSTRACT FACTORY
# 3_Ejercicio.py
# ============================================================

abstract_factory = cargar_modulo(
    "abstract_factory",
    "3_Ejercicio.py"
)

FabricaExchangeA = (
    abstract_factory.FabricaExchangeA
)

FabricaExchangeB = (
    abstract_factory.FabricaExchangeB
)


# ============================================================
# PROTOTYPE
# ============================================================

class Prototype(ABC):

    @abstractmethod
    def clonar(self):
        pass


# ============================================================
# CARTERA - PROTOTIPO CONCRETO
# ============================================================

class Cartera(Prototype):

    def __init__(
        self,
        nombre="Cartera Base"
    ):

        self.nombre = nombre

        # Cada elemento de esta lista representa
        # un registro independiente del activo.
        #
        # Ejemplo:
        # ["Bitcoin", 0.5, 64500.50]
        self.activos = []

        # Saldos de la cartera
        self.saldo_cop = 0.0
        self.saldo_usd = 0.0

        # Parámetros básicos de riesgo
        self.limite_exposicion = 100.0
        self.limite_perdida = 10.0

        # Porcentaje del saldo de la cartera principal
        # que posee esta cartera (100% para la principal).
        self.porcentaje_recargado = 100.0


    # ========================================================
    # CLONACIÓN - PROTOTYPE
    # ========================================================

    def clonar(self):

        # Se crea una copia completamente independiente
        # de la cartera original.
        return deepcopy(self)


    # ========================================================
    # REGISTRAR COMPRA
    # ========================================================

    def registrar_compra(
        self,
        activo,
        cantidad,
        precio
    ):

        # Buscar si el activo ya está registrado
        for registro in self.activos:

            if registro[0] == activo.nombre:

                registro[1] += cantidad

                return

        # Si no existe, se crea un nuevo arreglo
        nuevo_registro = [
            activo.nombre,
            cantidad,
            precio
        ]

        self.activos.append(
            nuevo_registro
        )


    # ========================================================
    # REGISTRAR VENTA
    # ========================================================

    def registrar_venta(
        self,
        nombre,
        cantidad
    ):

        for registro in self.activos:

            if registro[0] == nombre:

                if cantidad > registro[1]:

                    print(
                        "\nNo posee suficiente "
                        "cantidad del activo."
                    )

                    return False

                registro[1] -= cantidad

                if registro[1] == 0:

                    self.activos.remove(
                        registro
                    )

                return True

        print(
            "\nEl activo no se encuentra "
            "en la cartera."
        )

        return False


    # ========================================================
    # RECARGAR CARTERA
    # ========================================================

    def recargar(
        self,
        monto,
        moneda
    ):

        moneda = moneda.upper()

        if moneda == "COP":

            self.saldo_cop += monto

            print(
                f"\nRecarga realizada: "
                f"${monto:,.2f} COP"
            )

        elif moneda == "USD":

            self.saldo_usd += monto

            print(
                f"\nRecarga realizada: "
                f"${monto:,.2f} USD"
            )

        else:

            print(
                "\nMoneda no válida."
            )


    # ========================================================
    # CONFIGURAR RIESGO
    # ========================================================

    def configurar_riesgo(
        self,
        limite_exposicion,
        limite_perdida
    ):

        self.limite_exposicion = (
            limite_exposicion
        )

        self.limite_perdida = (
            limite_perdida
        )


    # ========================================================
    # MOSTRAR CARTERA
    # ========================================================

    def mostrar(self):

        print("\n========================================")
        print(f"          {self.nombre}")
        print("========================================")

        print(
            f"Saldo COP: "
            f"${self.saldo_cop:,.2f}"
        )

        print(
            f"Saldo USD: "
            f"${self.saldo_usd:,.2f}"
        )

        print(
            f"Límite exposición: "
            f"{self.limite_exposicion}%"
        )

        print(
            f"Límite pérdida: "
            f"{self.limite_perdida}%"
        )

        print(
            f"Porcentaje del saldo principal: "
            f"{self.porcentaje_recargado}%"
        )

        print("\n--- ACTIVOS ---")

        if not self.activos:

            print(
                "No hay activos registrados."
            )

            return

        for i, registro in enumerate(
            self.activos,
            start=1
        ):

            print(
                f"{i}. "
                f"{registro[0]} | "
                f"Cantidad: {registro[1]} | "
                f"Precio pagado: "
                f"${registro[2]:,.2f}"
            )


# ============================================================
# GESTOR DEL PROTOTYPE
# ============================================================

class GestorCarteras:

    def __init__(self):

        self.prototipo = None

    def establecer_prototipo(
        self,
        cartera
    ):

        self.prototipo = cartera

    def crear_copia(
        self,
        nombre,
        porcentaje_recargado=100.0
    ):

        if self.prototipo is None:

            print(
                "\nNo existe un prototipo."
            )

            return None

        # Clonación profunda: conserva la misma estructura de la
        # cartera principal y mantiene independientes sus datos.
        nueva_cartera = (
            self.prototipo.clonar()
        )

        nueva_cartera.nombre = nombre
        nueva_cartera.porcentaje_recargado = porcentaje_recargado

        # El clon recibe el mismo porcentaje del saldo recargado
        # en la cartera principal, tanto en COP como en USD.
        factor = porcentaje_recargado / 100.0

        nueva_cartera.saldo_cop = (
            self.prototipo.saldo_cop * factor
        )

        nueva_cartera.saldo_usd = (
            self.prototipo.saldo_usd * factor
        )

        return nueva_cartera


# ============================================================
# SERVICIOS DE CARTERAS PARA OTROS EJERCICIOS
# ============================================================

def crear_cartera_principal(
    nombre="Cartera Principal",
    limite_exposicion=50.0,
    limite_perdida=10.0
):
    """
    Crea la cartera principal usando la lógica definida por Prototype.
    Otros ejercicios deben usar esta función en lugar de construir
    la cartera directamente, para mantener una única fuente de lógica.
    """

    cartera = Cartera(nombre)

    cartera.configurar_riesgo(
        limite_exposicion,
        limite_perdida
    )

    return cartera


def crear_gestor_carteras(cartera):
    """
    Crea el gestor y establece la cartera indicada como prototipo.
    """

    gestor = GestorCarteras()

    gestor.establecer_prototipo(
        cartera
    )

    return gestor


def clonar_cartera(
    gestor,
    nombre,
    porcentaje_recargado
):
    """
    Clona una cartera mediante la lógica central del Prototype.
    El porcentaje se aplica al saldo COP y al saldo USD.
    """

    try:
        porcentaje_recargado = float(
            porcentaje_recargado
        )
    except (TypeError, ValueError):
        print(
            "\nEl porcentaje debe ser numérico."
        )
        return None

    if porcentaje_recargado < 0 or porcentaje_recargado > 100:
        print(
            "\nEl porcentaje debe estar entre 0% y 100%."
        )
        return None

    return gestor.crear_copia(
        nombre,
        porcentaje_recargado
    )


# ============================================================
# OBTENER PRECIO DEL SINGLETON
# ============================================================

def obtener_precio_singleton(
    nombre,
    api
):

    pares = {
        "Bitcoin": "BTC/USDT",
        "Ethereum": "ETH/USDT",
        "Solana": "SOL/USDT"
    }

    par = pares.get(nombre)

    if par is None:
        return None

    return api.get_price(par)


# ============================================================
# MENU DE ACTIVOS
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

    if opcion == "1":

        return (
            CreadorCriptomoneda(),
            "Bitcoin"
        )

    elif opcion == "2":

        return (
            CreadorCriptomoneda(),
            "Ethereum"
        )

    elif opcion == "3":

        return (
            CreadorToken(),
            "Chainlink"
        )

    elif opcion == "4":

        return (
            CreadorToken(),
            "Polygon"
        )

    elif opcion == "5":

        return (
            CreadorNFT(),
            "CryptoArt #001"
        )

    print("\nOpción no válida.")

    return None


# ============================================================
# MENU DE EXCHANGE
# ============================================================

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

        return FabricaExchangeA()

    elif opcion == "2":

        return FabricaExchangeB()

    print("\nOpción no válida.")

    return None


# ============================================================
# MENU DE OPERACION
# ============================================================

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

    elif opcion == "2":
        return "VENTA"

    print("\nOpción no válida.")

    return None


# ============================================================
# RECARGA
# ============================================================

def recargar_cartera(cartera):

    print("\n========================================")
    print("          RECARGAR CARTERA")
    print("========================================")

    print("1. Pesos colombianos (COP)")
    print("2. Dólares estadounidenses (USD)")

    opcion = input(
        "\nSeleccione la moneda: "
    ).strip()

    try:

        monto = float(
            input("Ingrese el monto: ")
        )

    except ValueError:

        print(
            "\nIngrese un valor válido."
        )

        return

    if monto <= 0:

        print(
            "\nEl monto debe ser mayor "
            "que cero."
        )

        return

    if opcion == "1":

        cartera.recargar(
            monto,
            "COP"
        )

    elif opcion == "2":

        cartera.recargar(
            monto,
            "USD"
        )

    else:

        print("\nMoneda no válida.")


# ============================================================
# CREAR ACTIVO MEDIANTE FACTORY METHOD
# ============================================================

def crear_activo(
    creador,
    nombre,
    precio
):

    return creador.crear_activo(
        nombre,
        precio
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n========================================")
    print("       PLATAFORMA DE TRADING")
    print("       GESTIÓN DE CARTERAS")
    print("             PROTOTYPE")
    print("========================================")


    # ========================================================
    # SINGLETON
    # ========================================================

    api = ExchangeConnectionManager()


    # ========================================================
    # CREAR CARTERA PROTOTIPO
    # ========================================================

    cartera_base = crear_cartera_principal(
        "Cartera Base",
        50.0,
        10.0
    )

    gestor = crear_gestor_carteras(
        cartera_base
    )


    # ========================================================
    # MENU PRINCIPAL
    # ========================================================

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


        # ====================================================
        # RECARGA
        # ====================================================

        if opcion == "1":

            recargar_cartera(
                cartera_base
            )


        # ====================================================
        # COMPRA
        # ====================================================

        elif opcion == "2":

            resultado = (
                seleccionar_activo()
            )

            if resultado is None:
                continue

            creador, nombre = resultado


            # -----------------------------------------------
            # Factory Method
            # -----------------------------------------------

            # Obtener precio actualizado del Singleton
            precio_singleton = (
                obtener_precio_singleton(
                    nombre,
                    api
                )
            )

            # Si Singleton no maneja ese activo,
            # se utiliza un precio base.
            if precio_singleton is None:

                precios_base = {
                    "Chainlink": 15.00,
                    "Polygon": 0.50,
                    "CryptoArt #001": 2500.00
                }

                precio_singleton = (
                    precios_base.get(
                        nombre,
                        0
                    )
                )


            activo = crear_activo(
                creador,
                nombre,
                precio_singleton
            )


            # -----------------------------------------------
            # Cantidad
            # -----------------------------------------------

            try:

                cantidad = float(
                    input(
                        "\nIngrese la cantidad: "
                    )
                )

            except ValueError:

                print(
                    "\nCantidad no válida."
                )

                continue


            if cantidad <= 0:

                print(
                    "\nLa cantidad debe ser "
                    "mayor que cero."
                )

                continue


            # -----------------------------------------------
            # Registrar cartera
            # -----------------------------------------------

            cartera_base.registrar_compra(
                activo,
                cantidad,
                precio_singleton
            )


            # -----------------------------------------------
            # Abstract Factory
            # -----------------------------------------------

            fabrica = seleccionar_exchange()

            if fabrica is not None:

                mercado = (
                    fabrica.crear_mercado()
                )

                orden = (
                    fabrica.crear_orden()
                )


                # El Abstract Factory trabaja con
                # el activo creado anteriormente.
                precio_exchange = (
                    mercado.consultar_precio(
                        activo
                    )
                )


                if precio_exchange != 0:

                    activo.precio = (
                        precio_exchange
                    )

                    orden.ejecutar(
                        activo,
                        "COMPRA",
                        cantidad
                    )


        # ====================================================
        # VENTA
        # ====================================================

        elif opcion == "3":

            if not cartera_base.activos:

                print(
                    "\nLa cartera está vacía."
                )

                continue


            print(
                "\n--- ACTIVOS EN CARTERA ---"
            )

            for i, registro in enumerate(
                cartera_base.activos,
                start=1
            ):

                print(
                    f"{i}. "
                    f"{registro[0]} | "
                    f"Cantidad: {registro[1]}"
                )


            try:

                indice = int(
                    input(
                        "\nSeleccione el activo: "
                    )
                )

                cantidad = float(
                    input(
                        "Ingrese la cantidad a vender: "
                    )
                )

            except ValueError:

                print(
                    "\nDato inválido."
                )

                continue


            if indice < 1 or indice > len(
                cartera_base.activos
            ):

                print(
                    "\nActivo no válido."
                )

                continue


            registro = (
                cartera_base.activos[
                    indice - 1
                ]
            )

            nombre = registro[0]


            if cartera_base.registrar_venta(
                nombre,
                cantidad
            ):

                print(
                    f"\nVenta de {nombre} "
                    "registrada correctamente."
                )


        # ====================================================
        # MOSTRAR CARTERA
        # ====================================================

        elif opcion == "4":

            cartera_base.mostrar()


        # ====================================================
        # PROTOTYPE
        # CLONAR CARTERA
        # ====================================================

        elif opcion == "5":

            nombre_clon = input(
                "\nIngrese el nombre de la "
                "nueva cartera: "
            ).strip()


            if not nombre_clon:

                print(
                    "\nDebe ingresar un nombre."
                )

                continue


            # Porcentaje del saldo recargado que tendrá el clon.
            try:

                porcentaje = float(
                    input(
                        "Ingrese el porcentaje del saldo "
                        "recargado para la cartera clon (%): "
                    )
                )

            except ValueError:

                print(
                    "\nIngrese un porcentaje numérico válido."
                )

                continue


            if porcentaje < 0 or porcentaje > 100:

                print(
                    "\nEl porcentaje debe estar entre 0% y 100%."
                )

                continue


            cartera_clon = clonar_cartera(
                gestor,
                nombre_clon,
                porcentaje
            )

            if cartera_clon is None:
                continue


            print(
                "\n========================================"
            )
            print(
                "      CARTERA CLONADA CORRECTAMENTE"
            )
            print(
                "========================================"
            )

            cartera_clon.mostrar()


            # Mostrar que es independiente
            print(
                "\nLa cartera clonada es "
                "independiente de la original."
            )


        # ====================================================
        # RIESGO
        # ====================================================

        elif opcion == "6":

            try:

                exposicion = float(
                    input(
                        "\nLímite de exposición (%): "
                    )
                )

                perdida = float(
                    input(
                        "Límite de pérdida (%): "
                    )
                )

                cartera_base.configurar_riesgo(
                    exposicion,
                    perdida
                )

                print(
                    "\nConfiguración de riesgo "
                    "actualizada."
                )

            except ValueError:

                print(
                    "\nIngrese valores numéricos."
                )


        # ====================================================
        # SALIR
        # ====================================================

        elif opcion == "7":

            print(
                "\nCerrando Prototype..."
            )

            break


        else:

            print(
                "\nOpción no válida."
            )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()