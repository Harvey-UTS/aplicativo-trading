"""Dashboard financiero académico."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from services.trading_service import TradingService


class DashboardPage(QWidget):
    def __init__(self, market_service, portfolio_service, trading_service, on_change) -> None:
        super().__init__()
        self.market_service: MarketService = market_service
        self.portfolio_service: PortfolioService = portfolio_service
        self.trading_service: TradingService = trading_service
        self.on_change = on_change
        self.cards: dict[str, QLabel] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()
        action = QPushButton("Actualizar mercado")
        action.setObjectName("primaryButton")
        action.clicked.connect(self.on_change)
        header.addWidget(action)
        layout.addLayout(header)

        subtitle = QLabel("Vista general del mercado y del capital simulado")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for idx, (key, label) in enumerate([
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("SOL", "Solana"),
            ("TOTAL", "Valor total cartera"),
            ("ASSETS", "Cantidad de activos"),
            ("PNL", "Ganancia simulada"),
        ]):
            frame, value = self._metric_card(label)
            self.cards[key] = value
            grid.addWidget(frame, idx // 3, idx % 3)
        layout.addLayout(grid)

        section = QLabel("Composición de la cartera principal")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Activo", "Cantidad", "Precio promedio", "Precio actual", "Valor"])
        self.table.setObjectName("dataTable")
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        note = QLabel(
            "Los precios son simulados localmente. No se envían órdenes a exchanges reales."
        )
        note.setObjectName("infoBanner")
        note.setAlignment(Qt.AlignCenter)
        layout.addWidget(note)

    def _metric_card(self, label: str):
        frame = QFrame()
        frame.setObjectName("metricCard")
        box = QVBoxLayout(frame)
        box.setContentsMargins(18, 18, 18, 18)
        caption = QLabel(label)
        caption.setObjectName("metricCaption")
        value = QLabel("—")
        value.setObjectName("metricValue")
        box.addWidget(caption)
        box.addWidget(value)
        return frame, value

    def refresh(self) -> None:
        cartera = self.portfolio_service.obtener_cartera("Cartera Principal")
        precios = {}
        for position in cartera.activos:
            try:
                precios[position.nombre] = self.market_service.obtener_precio(position.nombre, "A")
            except ValueError:
                precios[position.nombre] = position.precio_promedio
        resumen = cartera.resumen(precios)

        btc = self.market_service.obtener_precio("Bitcoin", "A")
        eth = self.market_service.obtener_precio("Ethereum", "A")
        sol = self.market_service.obtener_precio("Solana", "A")

        self.cards["BTC"].setText(f"${btc:,.2f}")
        self.cards["ETH"].setText(f"${eth:,.2f}")
        self.cards["SOL"].setText(f"${sol:,.2f}")
        self.cards["TOTAL"].setText(f"${resumen['valor_total']:,.2f} USD")
        self.cards["ASSETS"].setText(str(resumen["cantidad_activos"]))
        pnl = resumen["valor_total"] - cartera.capital_referencia_usd
        self.cards["PNL"].setText(f"${pnl:,.2f} USD")

        self.table.setRowCount(len(cartera.activos))
        for row, position in enumerate(cartera.activos):
            actual = precios.get(position.nombre, position.precio_promedio)
            values = [
                position.nombre,
                f"{position.cantidad:g}",
                f"${position.precio_promedio:,.2f}",
                f"${actual:,.2f}",
                f"${position.cantidad * actual:,.2f}",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
