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
