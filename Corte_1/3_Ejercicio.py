from abc import ABC, abstractmethod
import importlib.util


# ============================================================
# IMPORTAR FACTORY METHOD DESDE 2_Ejercicio.py
# ============================================================

ruta_factory = "2_Ejercicio.py"

spec = importlib.util.spec_from_file_location(
    "factory_method",
    ruta_factory
)

factory_method = importlib.util.module_from_spec(spec)

spec.loader.exec_module(factory_method)


# ============================================================
# CLASES IMPORTADAS DEL FACTORY METHOD
# ============================================================

ActivoDigital = factory_method.ActivoDigital

Criptomoneda = factory_method.Criptomoneda
Token = factory_method.Token
NFT = factory_method.NFT

CreadorActivo = factory_method.CreadorActivo
CreadorCriptomoneda = factory_method.CreadorCriptomoneda
CreadorToken = factory_method.CreadorToken
CreadorNFT = factory_method.CreadorNFT


# ============================================================
# ABSTRACT FACTORY
# PRODUCTOS ABSTRACTOS
# ============================================================

class Mercado(ABC):

    @abstractmethod
    def consultar_precio(self, activo):
        pass


class EjecutorOrden(ABC):

    @abstractmethod
    def ejecutar(self, activo, tipo, cantidad):
        pass


# ============================================================
# ABSTRACT FACTORY
# PRODUCTOS CONCRETOS - EXCHANGE A
# ============================================================

class MercadoExchangeA(Mercado):

    def consultar_precio(self, activo):

        precios = {
            "Bitcoin": 60000.00,
            "Ethereum": 3000.00,
            "Chainlink": 15.00,
            "Polygon": 0.50,
            "CryptoArt #001": 2500.00
        }

        return precios.get(activo.nombre, 0)


class OrdenExchangeA(EjecutorOrden):

    def ejecutar(self, activo, tipo, cantidad):

        precio = activo.precio
        total = precio * cantidad

        print("\n========================================")
        print("             EXCHANGE A")
        print("========================================")

        print(f"Activo: {activo.nombre}")
        print(f"Tipo: {type(activo).__name__}")
        print(f"Operación: {tipo}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio: ${precio:,.2f}")
        print(f"Total: ${total:,.2f}")

        print("\nOperación simulada correctamente.")


# ============================================================
# ABSTRACT FACTORY
# PRODUCTOS CONCRETOS - EXCHANGE B
# ============================================================

class MercadoExchangeB(Mercado):

    def consultar_precio(self, activo):

        precios = {
            "Bitcoin": 60500.00,
            "Ethereum": 3050.00,
            "Chainlink": 15.50,
            "Polygon": 0.55,
            "CryptoArt #001": 2600.00
        }

        return precios.get(activo.nombre, 0)


class OrdenExchangeB(EjecutorOrden):

    def ejecutar(self, activo, tipo, cantidad):

        precio = activo.precio
        total = precio * cantidad

        print("\n========================================")
        print("             EXCHANGE B")
        print("========================================")

        print(f"Activo: {activo.nombre}")
        print(f"Tipo: {type(activo).__name__}")
        print(f"Operación: {tipo}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio: ${precio:,.2f}")
        print(f"Total: ${total:,.2f}")

        print("\nOperación simulada correctamente.")


# ============================================================
# ABSTRACT FACTORY
# FABRICA ABSTRACTA
# ============================================================

class FabricaExchange(ABC):

    @abstractmethod
    def crear_mercado(self):
        pass

    @abstractmethod
    def crear_orden(self):
        pass


# ============================================================
# FABRICAS CONCRETAS
# ============================================================

class FabricaExchangeA(FabricaExchange):

    def crear_mercado(self):
        return MercadoExchangeA()

    def crear_orden(self):
        return OrdenExchangeA()


class FabricaExchangeB(FabricaExchange):

    def crear_mercado(self):
        return MercadoExchangeB()

    def crear_orden(self):
        return OrdenExchangeB()


# ============================================================
# CLIENTE
# ============================================================

class PlataformaTrading:

    def __init__(self, fabrica):

        self.mercado = fabrica.crear_mercado()
        self.orden = fabrica.crear_orden()

    def ejecutar_operacion(
        self,
        activo,
        tipo,
        cantidad
    ):

        # El activo viene del Factory Method
        precio = self.mercado.consultar_precio(activo)

        if precio == 0:

            print(
                "\nEl activo no está disponible "
                "en este exchange."
            )

            return

        # Actualizamos el precio con el precio
        # correspondiente al exchange.
        activo.precio = precio

        print(
            f"\nPrecio en el exchange: "
            f"${precio:,.2f}"
        )

        # Ejecutamos la operación
        # utilizando Abstract Factory.
        self.orden.ejecutar(
            activo,
            tipo,
            cantidad
        )


# ============================================================
# SELECCIONAR EXCHANGE
# ============================================================

def seleccionar_exchange():

    print("\n========================================")
    print("          SELECCIONE EXCHANGE")
    print("========================================")

    print("1. Exchange A")
    print("2. Exchange B")

    opcion = input(
        "\nSeleccione una opción: "
    ).strip()

    if opcion == "1":
        return FabricaExchangeA()

    elif opcion == "2":
        return FabricaExchangeB()

    print("\nOpción no válida.")

    return None


# ============================================================
# SELECCIONAR ACTIVO
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
        return CreadorCriptomoneda(), "Bitcoin", 60000.00

    elif opcion == "2":
        return CreadorCriptomoneda(), "Ethereum", 3000.00

    elif opcion == "3":
        return CreadorToken(), "Chainlink", 15.00

    elif opcion == "4":
        return CreadorToken(), "Polygon", 0.50

    elif opcion == "5":
        return CreadorNFT(), "CryptoArt #001", 2500.00

    print("\nOpción no válida.")

    return None


# ============================================================
# SELECCIONAR OPERACION
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
# SOLICITAR CANTIDAD
# ============================================================

def solicitar_cantidad():

    while True:

        try:

            cantidad = float(
                input(
                    "\nIngrese la cantidad: "
                )
            )

            if cantidad <= 0:

                print(
                    "La cantidad debe ser "
                    "mayor que cero."
                )

                continue

            return cantidad

        except ValueError:

            print(
                "Ingrese un valor numérico válido."
            )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("\n========================================")
    print("      ABSTRACT FACTORY")
    print(" PLATAFORMA DE TRADING MULTIEXCHANGE")
    print("========================================")


    # --------------------------------------------------------
    # 1. ABSTRACT FACTORY
    # Seleccionar el exchange
    # --------------------------------------------------------

    fabrica = seleccionar_exchange()

    if fabrica is None:
        return


    plataforma = PlataformaTrading(fabrica)


    # --------------------------------------------------------
    # 2. FACTORY METHOD
    # Utilizamos el creador del archivo externo
    # --------------------------------------------------------

    resultado = seleccionar_activo()

    if resultado is None:
        return


    creador, nombre, precio = resultado


    # --------------------------------------------------------
    # 3. Factory Method crea el activo
    # --------------------------------------------------------

    activo = creador.crear_activo(
        nombre,
        precio
    )


    # El objeto pertenece al Factory Method
    activo.mostrar_informacion()


    # --------------------------------------------------------
    # 4. Seleccionar operación
    # --------------------------------------------------------

    operacion = seleccionar_operacion()

    if operacion is None:
        return


    cantidad = solicitar_cantidad()


    # --------------------------------------------------------
    # 5. ABSTRACT FACTORY
    # Recibe el objeto creado externamente
    # --------------------------------------------------------

    plataforma.ejecutar_operacion(
        activo,
        operacion,
        cantidad
    )


# ============================================================
# EJECUCION
# ============================================================

if __name__ == "__main__":
    main()