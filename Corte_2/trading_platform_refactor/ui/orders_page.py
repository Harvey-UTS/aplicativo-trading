"""Pantalla de órdenes y Bridge."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class OrdersPage(QWidget):
    HEADERS = [
        "ID",
        "Fecha",
        "Tipo",
        "Lado",
        "Exchange",
        "Cartera",
        "Activo",
        "Cantidad",
        "Precio",
        "Objetivo",
        "Estado",
        "Total",
    ]

    def __init__(self, market_service, portfolio_service, trading_service, on_change) -> None:
        super().__init__()
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self.trading_service = trading_service
        self.on_change = on_change
        self._build()
        self._refresh_combos()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        title = QLabel("Órdenes")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Bridge separa tipo de orden y exchange; el formulario nunca conoce sus clases concretas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        group = QGroupBox("Nueva operación simulada")
        form = QFormLayout(group)
        self.side_combo = QComboBox()
        self.side_combo.addItems(["COMPRA", "VENTA"])
        self.type_combo = QComboBox()
        self.type_combo.addItems(["MARKET", "LIMIT", "STOP LOSS"])
        self.exchange_combo = QComboBox()
        self.portfolio_combo = QComboBox()
        self.asset_combo = QComboBox()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.000001, 1_000_000_000)
        self.quantity.setDecimals(6)
        self.quantity.setValue(0.1)
        self.target = QDoubleSpinBox()
        self.target.setRange(0.0001, 1_000_000_000)
        self.target.setDecimals(4)
        self.target.setSpecialValueText("Sin objetivo")
        self.target.setValue(0.0001)

        form.addRow("Lado", self.side_combo)
        form.addRow("Tipo de orden", self.type_combo)
        form.addRow("Exchange", self.exchange_combo)
        form.addRow("Cartera", self.portfolio_combo)
        form.addRow("Activo", self.asset_combo)
        form.addRow("Cantidad", self.quantity)
        form.addRow("Precio objetivo / activación", self.target)

        controls = QHBoxLayout()
        controls.addStretch()
        execute = QPushButton("Crear y ejecutar")
        execute.setObjectName("primaryButton")
        execute.clicked.connect(self.submit)
        controls.addWidget(execute)
        form.addRow("", controls)
        layout.addWidget(group)

        history_label = QLabel("Historial")
        history_label.setObjectName("sectionTitle")
        layout.addWidget(history_label)
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        self.type_combo.currentTextChanged.connect(self._toggle_target)
        self._toggle_target(self.type_combo.currentText())

    def _toggle_target(self, text: str) -> None:
        enabled = text != "MARKET"
        self.target.setEnabled(enabled)
        self.target.setVisible(enabled)

    def _refresh_combos(self) -> None:
        current_exchange = self.exchange_combo.currentText() or "A"
        current_portfolio = self.portfolio_combo.currentText()
        current_asset = self.asset_combo.currentText()

        self.exchange_combo.blockSignals(True)
        self.exchange_combo.clear()
        self.exchange_combo.addItems(["A", "B", "C"])
        exchange_index = self.exchange_combo.findText(current_exchange)
        self.exchange_combo.setCurrentIndex(exchange_index if exchange_index >= 0 else 0)
        self.exchange_combo.blockSignals(False)

        self.portfolio_combo.clear()
        self.portfolio_combo.addItems([p.nombre for p in self.portfolio_service.listar_carteras()])
        portfolio_index = self.portfolio_combo.findText(current_portfolio)
        if portfolio_index >= 0:
            self.portfolio_combo.setCurrentIndex(portfolio_index)

        self.asset_combo.clear()
        self.asset_combo.addItems([a.nombre for a in self.market_service.obtener_activos()])
        asset_index = self.asset_combo.findText(current_asset)
        if asset_index >= 0:
            self.asset_combo.setCurrentIndex(asset_index)

    def submit(self) -> None:
        type_text = self.type_combo.currentText()
        target = None if type_text == "MARKET" else self.target.value()
        try:
            platform, registro = self.trading_service.crear_orden(
                type_text,
                self.side_combo.currentText(),
                self.exchange_combo.currentText(),
                self.asset_combo.currentText(),
                self.quantity.value(),
                self.portfolio_combo.currentText(),
                target,
            )
            self.trading_service.ejecutar_orden(platform, registro)
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(self, "Orden rechazada", str(exc))
            return

        message = registro.mensaje or "Operación procesada."
        if registro.estado.value == "EJECUTADA":
            QMessageBox.information(self, "Orden procesada", message)
        else:
            QMessageBox.information(self, "Orden pendiente", message)
        self.refresh()
        self.on_change()

    def refresh(self) -> None:
        self._refresh_combos()
        history = self.trading_service.historial()
        self.table.setRowCount(len(history))
        for row, order in enumerate(history):
            values = order.to_row()
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
