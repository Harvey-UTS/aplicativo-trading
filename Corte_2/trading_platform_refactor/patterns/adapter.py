"""Adapter: normaliza APIs de exchanges con estructuras incompatibles."""

from __future__ import annotations

from models.asset import ActivoDigital
from patterns.abstract_factory import Mercado
from patterns.singleton import ExchangeConnectionManager


class ApiExchangeA:
    """API externa simulada: devuelve lastPrice."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def get_ticker(self, pair: str) -> dict[str, object]:
        price = self.manager.get_exchange_price("A", pair)
        if price is None:
            raise KeyError(f"El par {pair} no existe en Exchange A.")
        return {"symbol": pair, "lastPrice": price}


class ApiExchangeB:
    """API externa simulada: exige base/quote y entrega data.amount."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def fetch_market(self, base: str, quote: str) -> dict[str, object]:
        pair = f"{base.upper()}/{quote.upper()}"
        price = self.manager.get_exchange_price("B", pair)
        if price is None:
            raise KeyError(f"El par {pair} no existe en Exchange B.")
        return {"data": {"pair": pair, "amount": str(price)}}


class ApiExchangeC:
    """API externa simulada: devuelve ticker.last y un formato alternativo."""

    def __init__(self, manager: ExchangeConnectionManager | None = None) -> None:
        self.manager = manager or ExchangeConnectionManager()

    def obtener_ticker(self, par: str) -> dict[str, object]:
        price = self.manager.get_exchange_price("C", par)
        if price is None:
            raise KeyError(f"El par {par} no existe en Exchange C.")
        return {"ticker": {"pair": par, "last": price, "currency": "USDT"}}


def _pair_for_asset(activo: ActivoDigital) -> str:
    return f"{activo.simbolo.upper()}/USDT"


def _split_pair(pair: str) -> tuple[str, str]:
    base, quote = pair.split("/", 1)
    return base, quote


class ExchangeAAdapter(Mercado):
    """Target: Mercado.consultar_precio(activo)."""

    def __init__(self, api: ApiExchangeA | None = None) -> None:
        self.api = api or ApiExchangeA()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        response = self.api.get_ticker(_pair_for_asset(activo))
        return float(response["lastPrice"])


class ExchangeBAdapter(Mercado):
    def __init__(self, api: ApiExchangeB | None = None) -> None:
        self.api = api or ApiExchangeB()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        base, quote = _split_pair(_pair_for_asset(activo))
        response = self.api.fetch_market(base, quote)
        return float(response["data"]["amount"])


class ExchangeCAdapter(Mercado):
    def __init__(self, api: ApiExchangeC | None = None) -> None:
        self.api = api or ApiExchangeC()

    def consultar_precio(self, activo: ActivoDigital) -> float:
        response = self.api.obtener_ticker(_pair_for_asset(activo))
        return float(response["ticker"]["last"])
