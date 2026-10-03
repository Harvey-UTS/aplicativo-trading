from models.asset import Criptomoneda, NFT
from models.portfolio import Cartera, Posicion
from patterns.abstract_factory import FabricaExchangeA, FabricaExchangeB
from patterns.bridge import ExchangeAExecutor, ExchangeBExecutor, OrdenLimit, OrdenMarket
from patterns.composite import GrupoActivos, PosicionActivo, construir_composite
from patterns.decorator import MercadoConAuditoria
from patterns.factory_method import CreadorCriptomoneda, CreadorNFT
from patterns.prototype import clonar_cartera, crear_cartera_principal, crear_gestor_carteras
from patterns.singleton import ExchangeConnectionManager


def test_singleton_is_unique():
    ExchangeConnectionManager.reset_for_tests()
    a = ExchangeConnectionManager()
    b = ExchangeConnectionManager()
    assert a is b


def test_factory_method_creates_expected_products():
    btc = CreadorCriptomoneda().crear_activo("Bitcoin", 60000, "BTC")
    nft = CreadorNFT().crear_activo("Art", 100, "ART")
    assert isinstance(btc, Criptomoneda)
    assert isinstance(nft, NFT)


def test_abstract_factory_creates_market_and_executor():
    factory = FabricaExchangeA()
    assert factory.crear_mercado() is not None
    assert isinstance(factory.crear_orden(), ExchangeAExecutor)
    assert isinstance(FabricaExchangeB().crear_orden(), ExchangeBExecutor)


def test_bridge_market_executes_without_exchange_specific_class():
    factory = FabricaExchangeA()
    order = OrdenMarket(factory.crear_orden())
    asset = Criptomoneda("Bitcoin", 60000, "BTC")
    result = order.ejecutar(asset, "COMPRA", 0.1, 60000)
    assert result.status.value == "EJECUTADA"


def test_limit_order_can_remain_pending():
    factory = FabricaExchangeA()
    order = OrdenLimit(factory.crear_orden(), 59000)
    asset = Criptomoneda("Bitcoin", 60000, "BTC")
    result = order.ejecutar(asset, "COMPRA", 0.1, 60000)
    assert result.status.value == "PENDIENTE"


def test_prototype_clone_is_independent():
    principal = crear_cartera_principal()
    principal.recargar(1000, "USD")
    gestor = crear_gestor_carteras(principal)
    clon = clonar_cartera(gestor, "Conservadora", 50)
    clon.saldo_usd = 10
    assert principal.saldo_usd == 1000
    assert clon.saldo_usd == 10


def test_nft_rejects_quantity_other_than_one():
    factory = FabricaExchangeA()
    order = OrdenMarket(factory.crear_orden())
    nft = CreadorNFT().crear_activo("Art", 100, "ART")
    try:
        order.ejecutar(nft, "COMPRA", 2, 100)
    except ValueError as exc:
        assert "uno en uno" in str(exc)
    else:
        raise AssertionError("NFT should reject quantity different from 1")


def test_cloned_portfolio_keeps_own_risk_configuration():
    from services.portfolio_service import PortfolioService

    service = PortfolioService()
    conservadora = service.clonar_cartera("Conservadora", 50)
    agresiva = service.clonar_cartera("Agresiva", 80)

    service.configurar_riesgo("Conservadora", 35, 8, 4, 12)
    service.configurar_riesgo("Agresiva", 80, 25, 10, 30)

    assert conservadora.limite_exposicion == 35
    assert conservadora.limite_perdida == 8
    assert conservadora.stop_loss == 4
    assert conservadora.take_profit == 12

    assert agresiva.limite_exposicion == 80
    assert agresiva.limite_perdida == 25
    assert agresiva.stop_loss == 10
    assert agresiva.take_profit == 30

    principal = service.obtener_cartera("Cartera Principal")
    assert principal.limite_exposicion == 50
    assert principal.limite_perdida == 10
    assert principal.stop_loss == 5
    assert principal.take_profit == 10


def test_composite_aggregates_leaf_positions_and_nested_groups():
    cartera = Cartera("Cartera de prueba")
    cartera.activos.extend([
        Posicion("Bitcoin", 0.1, 60000),
        Posicion("Ethereum", 2, 3000),
    ])

    root = construir_composite(cartera)
    grupo_crypto = GrupoActivos("Cripto")
    for componente in root.componentes:
        grupo_crypto.agregar(componente)

    nested = GrupoActivos("Resumen")
    nested.agregar(grupo_crypto)

    assert root.valor({"Bitcoin": 61000, "Ethereum": 3200}) == 12500
    assert nested.valor({"Bitcoin": 61000, "Ethereum": 3200}) == 12500
    assert nested.cantidad_componentes() == 2


def test_decorator_adds_market_audit_without_changing_price():
    from patterns.adapter import ExchangeAAdapter

    manager = ExchangeConnectionManager()
    manager.reset_for_tests()
    from patterns.adapter import ApiExchangeA

    manager = ExchangeConnectionManager()
    adapter = ExchangeAAdapter(ApiExchangeA(manager))
    decorated = MercadoConAuditoria(adapter, "A")
    asset = Criptomoneda("Bitcoin", 60000, "BTC")

    price = decorated.consultar_precio(asset)
    audit = decorated.resumen()

    assert price == 60000.0
    assert audit["exchange"] == "A"
    assert audit["consultas"] == 1
    assert audit["ultima_consulta"]["activo"] == "Bitcoin"
