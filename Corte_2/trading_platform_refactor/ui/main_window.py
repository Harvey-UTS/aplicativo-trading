"""Ventana principal y navegación de la aplicación."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from patterns.singleton import ExchangeConnectionManager
from services.market_service import MarketService
from services.portfolio_service import PortfolioService
from services.trading_service import TradingService
from ui.assets_page import AssetsPage
from ui.dashboard_page import DashboardPage
from ui.market_page import MarketPage
from ui.orders_page import OrdersPage
from ui.portfolios_page import PortfoliosPage


class MainWindow(QMainWindow):
    """Shell visual de la plataforma."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Trading MultiExchange | Plataforma Académica")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 720)

        self.manager = ExchangeConnectionManager()
        self.market_service = MarketService(self.manager)
        self.portfolio_service = PortfolioService()
        self.trading_service = TradingService(self.market_service, self.portfolio_service)

        self.manager.start()
        self._build_ui()
        self._load_styles()
        self._start_timer()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(22, 24, 22, 22)
        sidebar_layout.setSpacing(10)

        brand = QLabel("TRADE\nMULTIEXCHANGE")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)

        subtitle = QLabel("Simulación académica")
        subtitle.setObjectName("sidebarSubtitle")
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(24)

        self.nav_buttons: list[QPushButton] = []
        pages = [
            ("⌂   Dashboard", 0),
            ("◈   Mercado", 1),
            ("◆   Activos", 2),
            ("⇄   Órdenes", 3),
            ("▣   Carteras & Riesgo", 4),
        ]
        for label, index in pages:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda checked=False, i=index: self.select_page(i))
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_layout.addStretch(1)

        status = QLabel("●  Simulación activa")
        status.setObjectName("statusBadge")
        sidebar_layout.addWidget(status)

        footer = QLabel("Local • Sin fondos reales")
        footer.setObjectName("sidebarFooter")
        sidebar_layout.addWidget(footer)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(
            self.market_service,
            self.portfolio_service,
            self.trading_service,
            self.refresh_all,
        )
        self.market_page = MarketPage(self.market_service)
        self.assets_page = AssetsPage(self.market_service, self.refresh_all)
        self.orders_page = OrdersPage(
            self.market_service,
            self.portfolio_service,
            self.trading_service,
            self.refresh_all,
        )
        self.portfolios_page = PortfoliosPage(
            self.market_service,
            self.portfolio_service,
            self.refresh_all,
        )

        for page in [
            self.dashboard_page,
            self.market_page,
            self.assets_page,
            self.orders_page,
            self.portfolios_page,
        ]:
            self.stack.addWidget(page)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.select_page(0)

    def _load_styles(self) -> None:
        qss = Path(__file__).with_name("styles.qss")
        self.setStyleSheet(qss.read_text(encoding="utf-8"))

    def _start_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start()

    def select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_all(self) -> None:
        self.market_service.actualizar_mercado()
        self.dashboard_page.refresh()
        self.market_page.refresh()
        self.assets_page.refresh()
        self.orders_page.refresh()
        self.portfolios_page.refresh()

    def closeEvent(self, event) -> None:
        self.manager.stop()
        event.accept()
