"""Carteras, Prototype y módulo de riesgo."""

from __future__ import annotations

from PySide6.QtWidgets import (
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
    QComboBox,
    QLineEdit,
)


class PortfoliosPage(QWidget):
    def __init__(self, market_service, portfolio_service, on_change) -> None:
        super().__init__()
        self.market_service = market_service
        self.portfolio_service = portfolio_service
        self.on_change = on_change
        # Controla si los campos de riesgo contienen cambios que todavía
        # no deben ser reemplazados por el refresco periódico de la UI.
        self._risk_dirty = False
        self._editing_portfolio: str | None = None
        self._loading_risk_fields = False
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        title = QLabel("Carteras & Riesgo")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Prototype para clonar estrategias y configurar límites de exposición y pérdidas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        top = QHBoxLayout()
        top.setSpacing(14)

        clone_group = QGroupBox("Clonar cartera")
        clone_form = QFormLayout(clone_group)
        self.clone_name = QLineEdit()
        self.clone_name.setPlaceholderText("Ej. Cartera Conservadora")
        self.clone_pct = QDoubleSpinBox()
        self.clone_pct.setRange(0, 100)
        self.clone_pct.setSuffix(" %")
        self.clone_pct.setValue(50)
        clone_button = QPushButton("Clonar")
        clone_button.setObjectName("primaryButton")
        clone_button.clicked.connect(self.clone)
        clone_form.addRow("Nombre", self.clone_name)
        clone_form.addRow("Porcentaje", self.clone_pct)
        clone_form.addRow("", clone_button)

        risk_group = QGroupBox("Configuración de riesgo")
        risk_form = QFormLayout(risk_group)
        self.portfolio_combo = QComboBox()
        self.exposure = self._percent_spin(50)
        self.loss = self._percent_spin(10)
        self.stop_loss = self._percent_spin(5)
        self.take_profit = self._percent_spin(10)
        save_button = QPushButton("Guardar riesgo")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.save_risk)
        risk_form.addRow("Cartera", self.portfolio_combo)
        risk_form.addRow("Límite exposición", self.exposure)
        risk_form.addRow("Límite pérdida", self.loss)
        risk_form.addRow("Stop Loss", self.stop_loss)
        risk_form.addRow("Take Profit", self.take_profit)
        risk_form.addRow("", save_button)

        top.addWidget(clone_group, 1)
        top.addWidget(risk_group, 1)
        layout.addLayout(top)

        summary = QHBoxLayout()
        self.balance_label = QLabel("—")
        self.risk_label = QLabel("—")
        self.balance_label.setObjectName("infoCard")
        self.risk_label.setObjectName("infoCard")
        summary.addWidget(self.balance_label)
        summary.addWidget(self.risk_label)
        layout.addLayout(summary)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Activo", "Cantidad", "Precio promedio", "Valor mercado", "% cartera"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        self.portfolio_combo.currentTextChanged.connect(self._on_portfolio_changed)
        for field in (self.exposure, self.loss, self.stop_loss, self.take_profit):
            field.valueChanged.connect(self._mark_risk_dirty)

    @staticmethod
    def _percent_spin(value: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 100)
        spin.setDecimals(2)
        spin.setSuffix(" %")
        spin.setValue(value)
        return spin

    def clone(self) -> None:
        try:
            clone = self.portfolio_service.clonar_cartera(self.clone_name.text(), self.clone_pct.value())
        except ValueError as exc:
            QMessageBox.warning(self, "No se pudo clonar", str(exc))
            return
        QMessageBox.information(self, "Prototype", f"{clone.nombre} fue creada desde la cartera prototipo.")
        self.clone_name.clear()
        self.refresh()
        cloned_index = self.portfolio_combo.findText(clone.nombre)
        if cloned_index >= 0:
            self.portfolio_combo.setCurrentIndex(cloned_index)
        self.on_change()

    def _mark_risk_dirty(self) -> None:
        if self._loading_risk_fields:
            return
        self._risk_dirty = True
        self._editing_portfolio = self.portfolio_combo.currentText() or None

    def _set_risk_fields_from_model(self, cartera) -> None:
        """Carga los valores persistidos sin generar cambios pendientes."""
        self._loading_risk_fields = True
        try:
            self.exposure.setValue(cartera.limite_exposicion)
            self.loss.setValue(cartera.limite_perdida)
            self.stop_loss.setValue(cartera.stop_loss)
            self.take_profit.setValue(cartera.take_profit)
        finally:
            self._loading_risk_fields = False
        self._risk_dirty = False
        self._editing_portfolio = cartera.nombre

    def _on_portfolio_changed(self) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            return

        # Cambiar de cartera significa trabajar con la configuración de esa
        # cartera. Los cambios no guardados se descartan únicamente al
        # seleccionar otra cartera; el refresco automático nunca los pisa.
        cartera = self.portfolio_service.obtener_cartera(name)
        self._set_risk_fields_from_model(cartera)
        self._refresh_table(cartera)

    def save_risk(self) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            QMessageBox.warning(self, "Riesgo inválido", "Selecciona una cartera antes de guardar.")
            return

        try:
            self.portfolio_service.configurar_riesgo(
                name,
                self.exposure.value(),
                self.loss.value(),
                self.stop_loss.value(),
                self.take_profit.value(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Riesgo inválido", str(exc))
            return

        # Los valores ya están escritos en la instancia Cartera concreta.
        # Al marcar como limpio antes del refresco, el QTimer puede actualizar
        # la tabla sin volver a tratar la edición como si fueran valores nuevos.
        self._risk_dirty = False
        self._editing_portfolio = name
        QMessageBox.information(self, "Riesgo", f"La configuración de {name} fue actualizada y guardada.")
        self.refresh()
        self.on_change()

    def load_selected(self, force: bool = False) -> None:
        name = self.portfolio_combo.currentText()
        if not name:
            return
        cartera = self.portfolio_service.obtener_cartera(name)

        # Durante la edición, el refresco periódico solo actualiza la información
        # calculada. No vuelve a escribir los controles con los valores del modelo.
        editing_same_portfolio = self._risk_dirty and self._editing_portfolio == name
        if force or not editing_same_portfolio:
            self._set_risk_fields_from_model(cartera)

        self._refresh_table(cartera)

    def _refresh_table(self, cartera) -> None:
        prices = {
            position.nombre: self.market_service.obtener_precio(position.nombre, "A")
            for position in cartera.activos
        }
        total = cartera.valor_total_usd(prices)
        activos_valor = cartera.valor_activos(prices)
        self.balance_label.setText(
            f"Saldo: ${cartera.saldo_usd:,.2f} USD  •  Activos: ${activos_valor:,.2f} USD  •  Total: ${total:,.2f} USD"
        )
        riesgo = self.portfolio_service.evaluar_riesgo(cartera, prices)
        self.risk_label.setText(
            f"Exposición: {riesgo['exposicion_pct']:.2f}%  •  Drawdown: {riesgo['drawdown_pct']:.2f}%  •  SL {cartera.stop_loss:.2f}%  •  TP {cartera.take_profit:.2f}%"
        )

        self.table.setRowCount(len(cartera.activos))
        for row, position in enumerate(cartera.activos):
            actual = prices.get(position.nombre, position.precio_promedio)
            value = position.cantidad * actual
            exposure = value / activos_valor * 100 if activos_valor else 0.0
            values = [
                position.nombre,
                f"{position.cantidad:g}",
                f"${position.precio_promedio:,.2f}",
                f"${value:,.2f}",
                f"{exposure:.2f}%",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def refresh(self) -> None:
        current = self.portfolio_combo.currentText()
        self.portfolio_combo.blockSignals(True)
        self.portfolio_combo.clear()
        self.portfolio_combo.addItems([p.nombre for p in self.portfolio_service.listar_carteras()])
        if current:
            index = self.portfolio_combo.findText(current)
            if index >= 0:
                self.portfolio_combo.setCurrentIndex(index)
        self.portfolio_combo.blockSignals(False)

        self.load_selected()
