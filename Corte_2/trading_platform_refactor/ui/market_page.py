"""Pantalla de mercado."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class MarketPage(QWidget):
    def __init__(self, market_service) -> None:
        super().__init__()
        self.market_service = market_service
        self.previous: dict[tuple[str, str], float] = {}
        self._build()

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

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Activo", "Símbolo", "Tipo", "Exchange", "Precio", "Variación"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        rows = self.market_service.tabla_mercado(self.previous)
        self.table.setRowCount(len(rows))
        current: dict[tuple[str, str], float] = {}
        for row_index, row in enumerate(rows):
            current[(row.exchange, row.activo)] = row.precio
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
        self.previous = current
        self.table.resizeColumnsToContents()
