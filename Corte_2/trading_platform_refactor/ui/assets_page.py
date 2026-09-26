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
