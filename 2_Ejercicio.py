from abc import ABC, abstractmethod


# ============================================================
# PRODUCTO ABSTRACTO
# ============================================================

class ActivoDigital(ABC):
    """
    Clase abstracta que representa un activo digital.

    Es el PRODUCTO ABSTRACTO del patrón Factory Method.
    Todas las clases de activos digitales deben implementar
    las operaciones definidas aquí.
    """

    def __init__(self, nombre: str, precio: float):
        self.nombre = nombre
        self.precio = precio

    @abstractmethod
    def comprar(self, cantidad: float) -> None:
        """
        Realiza una operación de compra.
        """
        pass

    @abstractmethod
    def vender(self, cantidad: float) -> None:
        """
        Realiza una operación de venta.
        """
        pass

    @abstractmethod
    def mostrar_informacion(self) -> None:
        """
        Muestra la información del activo.
        """
        pass


# ============================================================
# PRODUCTOS CONCRETOS
# ============================================================

class Criptomoneda(ActivoDigital):
    """
    Producto concreto que representa una criptomoneda.
    """

    def comprar(self, cantidad: float) -> None:
        total = cantidad * self.precio

        print("\n--- COMPRA REALIZADA ---")
        print(f"Activo: {self.nombre}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${self.precio:,.2f}")
        print(f"Total: ${total:,.2f}")

    def vender(self, cantidad: float) -> None:
        total = cantidad * self.precio

        print("\n--- VENTA REALIZADA ---")
        print(f"Activo: {self.nombre}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${self.precio:,.2f}")
        print(f"Total: ${total:,.2f}")

    def mostrar_informacion(self) -> None:
        print(f"\nCriptomoneda: {self.nombre}")
        print(f"Precio: ${self.precio:,.2f}")


class Token(ActivoDigital):
    """
    Producto concreto que representa un token.
    """

    def comprar(self, cantidad: float) -> None:
        total = cantidad * self.precio

        print("\n--- COMPRA REALIZADA ---")
        print(f"Token: {self.nombre}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${self.precio:,.2f}")
        print(f"Total: ${total:,.2f}")

    def vender(self, cantidad: float) -> None:
        total = cantidad * self.precio

        print("\n--- VENTA REALIZADA ---")
        print(f"Token: {self.nombre}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${self.precio:,.2f}")
        print(f"Total: ${total:,.2f}")

    def mostrar_informacion(self) -> None:
        print(f"\nToken: {self.nombre}")
        print(f"Precio: ${self.precio:,.2f}")


class NFT(ActivoDigital):
    """
    Producto concreto que representa un NFT.

    Para simplificar la simulación, cada NFT se maneja
    como una unidad individual.
    """

    def comprar(self, cantidad: float) -> None:
        if cantidad != 1:
            print("\nUn NFT se debe comprar de uno en uno.")
            return

        print("\n--- COMPRA REALIZADA ---")
        print(f"NFT: {self.nombre}")
        print(f"Precio: ${self.precio:,.2f}")

    def vender(self, cantidad: float) -> None:
        if cantidad != 1:
            print("\nUn NFT se debe vender de uno en uno.")
            return

        print("\n--- VENTA REALIZADA ---")
        print(f"NFT: {self.nombre}")
        print(f"Precio: ${self.precio:,.2f}")

    def mostrar_informacion(self) -> None:
        print(f"\nNFT: {self.nombre}")
        print(f"Precio: ${self.precio:,.2f}")


# ============================================================
# CREADOR ABSTRACTO
# ============================================================

class CreadorActivo(ABC):
    """
    Creator abstracto del patrón Factory Method.

    Declara el Factory Method crear_activo(), pero no decide
    qué tipo concreto de activo se debe crear.
    """

    @abstractmethod
    def crear_activo(
        self,
        nombre: str,
        precio: float
    ) -> ActivoDigital:
        """
        FACTORY METHOD.

        Las clases hijas decidirán qué producto concreto crear.
        """
        pass

    def comprar_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float
    ) -> None:
        """
        Crea un activo utilizando el Factory Method
        y posteriormente realiza la compra.
        """

        activo = self.crear_activo(nombre, precio)

        activo.comprar(cantidad)

    def vender_activo(
        self,
        nombre: str,
        precio: float,
        cantidad: float
    ) -> None:
        """
        Crea un activo utilizando el Factory Method
        y posteriormente realiza la venta.
        """

        activo = self.crear_activo(nombre, precio)

        activo.vender(cantidad)

    def mostrar_activo(
        self,
        nombre: str,
        precio: float
    ) -> None:
        """
        Crea un activo y muestra su información.
        """

        activo = self.crear_activo(nombre, precio)

        activo.mostrar_informacion()


# ============================================================
# CREADORES CONCRETOS
# ============================================================

class CreadorCriptomoneda(CreadorActivo):
    """
    Concrete Creator encargado de crear criptomonedas.
    """

    def crear_activo(
        self,
        nombre: str,
        precio: float
    ) -> ActivoDigital:

        return Criptomoneda(nombre, precio)


class CreadorToken(CreadorActivo):
    """
    Concrete Creator encargado de crear tokens.
    """

    def crear_activo(
        self,
        nombre: str,
        precio: float
    ) -> ActivoDigital:

        return Token(nombre, precio)


class CreadorNFT(CreadorActivo):
    """
    Concrete Creator encargado de crear NFT.
    """

    def crear_activo(
        self,
        nombre: str,
        precio: float
    ) -> ActivoDigital:

        return NFT(nombre, precio)


# ============================================================
# FUNCIONES DEL MENÚ
# ============================================================

def mostrar_menu_activos():
    """
    Muestra el menú de selección de activos disponibles.
    """

    print("\n========================================")
    print("       ACTIVOS DIGITALES DISPONIBLES")
    print("========================================")
    print("1. Bitcoin (Criptomoneda)")
    print("2. Ethereum (Criptomoneda)")
    print("3. Chainlink (Token)")
    print("4. Polygon (Token)")
    print("5. CryptoArt #001 (NFT)")
    print("6. Salir")
    print("========================================")


def seleccionar_activo():
    """
    Permite al usuario seleccionar un activo.

    Retorna:
        tuple: creador, nombre y precio.
        None si el usuario decide salir.
    """

    while True:

        mostrar_menu_activos()

        opcion = input("Seleccione un activo: ").strip()

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

        elif opcion == "6":
            return None

        else:
            print("\nOpción no válida. Intente nuevamente.")


def seleccionar_operacion():
    """
    Permite seleccionar entre comprar y vender.

    Retorna:
        str: 'comprar' o 'vender'.
    """

    while True:

        print("\n========================================")
        print("             TIPO DE OPERACIÓN")
        print("========================================")
        print("1. Comprar")
        print("2. Vender")
        print("========================================")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            return "comprar"

        elif opcion == "2":
            return "vender"

        else:
            print("\nOpción no válida. Intente nuevamente.")


def solicitar_cantidad():
    """
    Solicita al usuario la cantidad del activo que desea operar.

    Retorna:
        float: cantidad ingresada por el usuario.
    """

    while True:

        try:
            cantidad = float(
                input("\nIngrese la cantidad que desea operar: ")
            )

            if cantidad <= 0:
                print("La cantidad debe ser mayor que cero.")
                continue

            return cantidad

        except ValueError:
            print("Ingrese un valor numérico válido.")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    """
    Ejecuta el sistema de compra y venta de activos digitales.

    El usuario puede:

    1. Seleccionar un activo.
    2. Seleccionar comprar o vender.
    3. Ingresar la cantidad.
    4. Ejecutar la operación.

    El código cliente no crea directamente objetos como
    Criptomoneda(), Token() o NFT().

    La creación se realiza mediante Factory Method.
    """

    print("\n")
    print("========================================")
    print("     PLATAFORMA DE ACTIVOS DIGITALES")
    print("========================================")

    while True:

        # ----------------------------------------------------
        # SELECCIONAR ACTIVO
        # ----------------------------------------------------

        resultado = seleccionar_activo()

        if resultado is None:
            print("\nGracias por utilizar la plataforma.")
            break

        creador, nombre, precio = resultado

        # ----------------------------------------------------
        # MOSTRAR INFORMACIÓN
        # ----------------------------------------------------

        creador.mostrar_activo(
            nombre,
            precio
        )

        # ----------------------------------------------------
        # SELECCIONAR OPERACIÓN
        # ----------------------------------------------------

        operacion = seleccionar_operacion()

        # ----------------------------------------------------
        # SOLICITAR CANTIDAD
        # ----------------------------------------------------

        cantidad = solicitar_cantidad()

        # ----------------------------------------------------
        # EJECUTAR OPERACIÓN
        # ----------------------------------------------------

        if operacion == "comprar":

            creador.comprar_activo(
                nombre,
                precio,
                cantidad
            )

        elif operacion == "vender":

            creador.vender_activo(
                nombre,
                precio,
                cantidad
            )

        # ----------------------------------------------------
        # CONTINUAR
        # ----------------------------------------------------

        print("\n========================================")
        print("Operación finalizada.")
        print("========================================")

        continuar = input(
            "\n¿Desea realizar otra operación? (s/n): "
        ).strip().lower()

        if continuar != "s":
            print("\nGracias por utilizar la plataforma.")
            break


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()