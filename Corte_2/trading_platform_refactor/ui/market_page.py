"""Pantalla de mercado."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MarketPage(QWidget):
    def __init__(self, facade) -> None:
        super().__init__()
        self.facade = facade
        self.previous: dict[tuple[str, str], float] = {}
        self._selected_market_item: tuple[str, str] | None = None
        self._latest_events: dict[tuple[str, str], object] = {}
        self._build()
        self.facade.suscribir_observador_mercado(self)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(14)
        title = QLabel("Mercado")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Precios normalizados mediante Adapter desde tres APIs simuladas")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)
        self.last_update = QLabel("Observer: esperando la primera notificación de precio.")
        self.last_update.setObjectName("pageSubtitle")
        layout.addWidget(self.last_update)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Activo", "Símbolo", "Tipo", "Exchange", "Precio", "Variación"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        layout.addWidget(self.table, 1)

    def actualizar(self, evento) -> None:
        """Recibe notificaciones y prioriza el activo seleccionado en la tabla."""
        key = (evento.exchange, evento.activo)
        self._latest_events[key] = evento

        # Sin una fila seleccionada se conserva el comportamiento Observer original.
        # Al seleccionar una fila, las cotizaciones de otros activos no reemplazan su ficha.
        if self._selected_market_item is not None and key != self._selected_market_item:
            return

        self._mostrar_evento(evento)

    def _mostrar_evento(self, evento) -> None:
        self.last_update.setText(
            f"Observer · {evento.exchange} · {evento.activo} ({evento.simbolo}): "
            f"${evento.precio:,.4f} · {evento.fecha:%H:%M:%S}"
        )

    def _selection_changed(self) -> None:
        """Actualiza el mensaje superior según la fila seleccionada en Mercado."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self._selected_market_item = None
            return

        row = selected_rows[0].row()
        asset_item = self.table.item(row, 0)
        exchange_item = self.table.item(row, 3)
        if asset_item is None or exchange_item is None:
            return

        exchange = exchange_item.text().removeprefix("Exchange ")
        key = (exchange, asset_item.text())
        self._selected_market_item = key

        evento = self._latest_events.get(key)
        if evento is not None:
            self._mostrar_evento(evento)

    def cerrar(self) -> None:
        self.facade.cancelar_suscripcion_mercado(self)

    def refresh(self) -> None:
        rows = self.facade.tabla_mercado(self.previous)
        selected_key = self._selected_market_item
        current: dict[tuple[str, str], float] = {}

        # Evita perder la selección al reconstruir la tabla en cada actualización
        # automática del mercado.
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(len(rows))
            selected_row = None
            for row_index, row in enumerate(rows):
                key = (row.exchange, row.activo)
                current[key] = row.precio
                if key == selected_key:
                    selected_row = row_index

                values = [
                    row.activo,
                    row.simbolo,
                    row.tipo,
                    f"Exchange {row.exchange}",
                    f"${row.precio:,.2f}",
                    f"{row.variacion:+.2f}%",
                ]
                for col, text in enumerate(values):
                    self.table.setItem(row_index, col, QTableWidgetItem(text))
        finally:
            self.table.blockSignals(False)

        self.previous = current
        self.table.resizeColumnsToContents()
        if selected_key is not None and selected_row is not None:
            self.table.selectRow(selected_row)
        elif selected_key is not None:
            self._selected_market_item = None
