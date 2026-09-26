"""Singleton: fuente única de verdad para precios simulados."""

from __future__ import annotations

import random
import threading
import time
from typing import ClassVar


class ExchangeConnectionManager:
    """Administra una única instancia del caché de mercado.

    No conoce PySide6 y no imprime en consola. Puede ejecutar una pequeña
    simulación en segundo plano para mantener el comportamiento dinámico del
    ejercicio original.
    """

    _instance: ClassVar["ExchangeConnectionManager | None"] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    _initial_exchange_prices = {
        "A": {
            "BTC/USDT": 60000.00,
            "ETH/USDT": 3000.00,
            "SOL/USDT": 145.20,
            "LINK/USDT": 15.00,
            "MATIC/USDT": 0.50,
            "CRYPTOART001/USDT": 2500.00,
        },
        "B": {
            "BTC/USDT": 60500.00,
            "ETH/USDT": 3050.00,
            "SOL/USDT": 146.10,
            "LINK/USDT": 15.50,
            "MATIC/USDT": 0.55,
            "CRYPTOART001/USDT": 2600.00,
        },
        "C": {
            "BTC/USDT": 61000.00,
            "ETH/USDT": 3095.00,
            "SOL/USDT": 147.40,
            "LINK/USDT": 16.00,
            "MATIC/USDT": 0.57,
            "CRYPTOART001/USDT": 2700.00,
        },
    }

    _canonical_prices = {
        "BTC/USDT": 64500.50,
        "ETH/USDT": 3450.75,
        "SOL/USDT": 145.20,
    }

    def __new__(cls) -> "ExchangeConnectionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self) -> None:
        self._prices = {
            exchange: dict(prices)
            for exchange, prices in self._initial_exchange_prices.items()
        }
        self._canonical = dict(self._canonical_prices)
        self._data_lock = threading.RLock()
        self.running = False
        self._thread: threading.Thread | None = None

    def start(self, interval: float = 1.0) -> None:
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(
            target=self._update_loop,
            args=(interval,),
            daemon=True,
            name="market-simulator",
        )
        self._thread.start()

    def _update_loop(self, interval: float) -> None:
        while self.running:
            time.sleep(max(0.25, interval))
            self.simulate_market_update()

    def simulate_market_update(self) -> None:
        with self._data_lock:
            for exchange_prices in self._prices.values():
                for pair, value in list(exchange_prices.items()):
                    exchange_prices[pair] = round(
                        max(0.0001, value * (1.0 + random.uniform(-0.003, 0.003))),
                        4 if value < 1 else 2,
                    )

            for pair, value in list(self._canonical.items()):
                self._canonical[pair] = round(
                    max(0.0001, value * (1.0 + random.uniform(-0.003, 0.003))),
                    4 if value < 1 else 2,
                )

    def get_price(self, pair: str) -> float | None:
        """Mantiene el contrato original para el precio canónico."""
        with self._data_lock:
            return self._canonical.get(pair)

    def get_exchange_price(self, exchange: str, pair: str) -> float | None:
        exchange = str(exchange).upper()
        with self._data_lock:
            return self._prices.get(exchange, {}).get(pair)

    def set_cached_price(self, exchange: str, pair: str, price: float) -> None:
        with self._data_lock:
            self._prices.setdefault(exchange.upper(), {})[pair] = float(price)

    def snapshot(self, exchange: str | None = None) -> dict:
        with self._data_lock:
            if exchange is None:
                return {key: dict(value) for key, value in self._prices.items()}
            return dict(self._prices.get(exchange.upper(), {}))

    def stop(self) -> None:
        self.running = False

    @classmethod
    def reset_for_tests(cls) -> None:
        """Reinicia el Singleton únicamente para pruebas automatizadas."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.stop()
            cls._instance = None
