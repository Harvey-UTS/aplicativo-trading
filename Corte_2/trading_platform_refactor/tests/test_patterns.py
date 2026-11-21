from models.asset import Criptomoneda, NFT
from models.portfolio import Cartera, Posicion
from patterns.abstract_factory import FabricaExchangeA, FabricaExchangeB
from patterns.bridge import ExchangeAExecutor, ExchangeBExecutor, OrdenLimit, OrdenMarket
from patterns.composite import GrupoActivos, PosicionActivo, construir_composite
from patterns.decorator import MercadoConAuditoria
from patterns.flyweight import ParMercadoFactory
from patterns.factory_method import CreadorCriptomoneda, CreadorNFT
from patterns.prototype import clonar_cartera, crear_cartera_principal, crear_gestor_carteras
from patterns.proxy import MercadoProxy
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


def test_facade_unifies_market_portfolio_and_order_flow():
    from models.order import EstadoOrden
    from patterns.facade import TradingPlatformFacade

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()

    assert any(asset.nombre == "Bitcoin" for asset in facade.obtener_activos())
    assert any(portfolio.nombre == "Cartera Principal" for portfolio in facade.listar_carteras())

    registro = facade.crear_y_ejecutar_orden(
        "MARKET",
        "COMPRA",
        "A",
        "Bitcoin",
        0.001,
        "Cartera Principal",
    )

    assert registro.estado == EstadoOrden.EJECUTADA
    assert registro.total > 0
    assert facade.historial_ordenes()[0].id == registro.id
    assert facade.obtener_cartera("Cartera Principal").buscar_posicion("Bitcoin") is not None


def test_flyweight_reuses_normalized_market_pairs():
    ParMercadoFactory.limpiar_cache()
    try:
        btc_a = ParMercadoFactory.obtener("btc", "usdt")
        btc_b = ParMercadoFactory.obtener("BTC", "USDT")
        eth = ParMercadoFactory.obtener("ETH", "USDT")

        assert btc_a is btc_b
        assert btc_a is not eth
        assert btc_a.par == "BTC/USDT"
        assert ParMercadoFactory.cantidad_compartidos() == 2
        for invalid_symbol in (None, "", "BTC/USDT"):
            try:
                ParMercadoFactory.obtener(invalid_symbol, "USDT")
            except ValueError:
                pass
            else:
                raise AssertionError("El Flyweight debe rechazar símbolos inválidos")
    finally:
        ParMercadoFactory.limpiar_cache()


def test_proxy_validates_and_lazily_creates_market_only_once():
    from patterns.abstract_factory import Mercado

    class MercadoFalso(Mercado):
        def consultar_precio(self, activo):
            return 125.0

    creados = []

    def crear_mercado():
        mercado = MercadoFalso()
        creados.append(mercado)
        return mercado

    proxy = MercadoProxy(crear_mercado)
    assert proxy.inicializado is False

    try:
        proxy.consultar_precio("Bitcoin")
    except TypeError:
        pass
    else:
        raise AssertionError("El proxy debe rechazar objetos que no sean ActivoDigital")

    assert creados == []
    activo = Criptomoneda("Bitcoin", 60000, "BTC")
    assert proxy.consultar_precio(activo) == 125.0
    assert proxy.consultar_precio(activo) == 125.0
    assert proxy.inicializado is True
    assert len(creados) == 1


def test_market_service_integrates_proxy_before_audited_adapter():
    from patterns.decorator import MercadoConAuditoria
    from services.market_service import MarketService

    ExchangeConnectionManager.reset_for_tests()
    service = MarketService()
    mercado_decorado = service._markets["A"]
    assert isinstance(mercado_decorado, MercadoConAuditoria)
    proxy = mercado_decorado.mercado
    assert isinstance(proxy, MercadoProxy)
    assert proxy.inicializado is False

    assert service.obtener_precio("Bitcoin", "A") == 60000.0
    assert proxy.inicializado is True
    assert service.obtener_auditoria_mercado("A")["consultas"] == 1


def test_chain_of_responsibility_rejects_invalid_request_before_command_dispatch():
    from patterns.facade import TradingPlatformFacade
    from services.order_pattern_service import ServicioDespachoOrdenes

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    despachador = ServicioDespachoOrdenes(facade)

    try:
        despachador.ejecutar_orden(
            "MARKET",
            "COMPRA",
            "A",
            "Bitcoin",
            0,
            "Cartera Principal",
        )
    except ValueError as exc:
        assert "cantidad" in str(exc).lower()
    else:
        raise AssertionError("La cadena debe detener una orden con cantidad inválida")

    assert despachador.historial_comandos() == ()
    assert facade.historial_ordenes() == []


def test_command_dispatches_order_once_and_keeps_command_history():
    from models.order import EstadoOrden
    from patterns.facade import TradingPlatformFacade
    from services.order_pattern_service import ServicioDespachoOrdenes

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    despachador = ServicioDespachoOrdenes(facade)

    registro = despachador.ejecutar_orden(
        "MARKET",
        "COMPRA",
        "A",
        "Bitcoin",
        0.001,
        "Cartera Principal",
    )

    comandos = despachador.historial_comandos()
    assert registro.estado == EstadoOrden.EJECUTADA
    assert len(comandos) == 1
    assert comandos[0].resultado is registro

    # Repetir el mismo comando devuelve el resultado existente y no duplica
    # la operación en el historial ni vuelve a descontar saldo de la cartera.
    saldo_despues_de_compra = facade.obtener_cartera("Cartera Principal").saldo_usd
    resultado_repetido = comandos[0].ejecutar()
    assert resultado_repetido is registro
    assert facade.obtener_cartera("Cartera Principal").saldo_usd == saldo_despues_de_compra
    assert len(facade.historial_ordenes()) == 1
    assert len(despachador.historial_comandos()) == 1


def test_mediator_notifies_only_registered_receptors():
    from patterns.mediator import MediadorTrading

    mediator = MediadorTrading()
    received = []
    mediator.registrar("orden", lambda **data: received.append(data["id"]))
    mediator.notificar("orden", id="ABC123")

    assert received == ["ABC123"]
    assert mediator.notificar("sin_receptores") == ()


def test_memento_restores_complete_portfolio_state_without_replacing_instance():
    from patterns.memento import HistorialCartera

    cartera = Cartera("Cartera Memento")
    cartera.recargar(1000, "USD")
    cartera.activos.append(Posicion("Bitcoin", 0.1, 60000))
    historial = HistorialCartera(capacidad=2)
    identidad = id(cartera)
    historial.guardar(cartera, "Estado inicial")

    cartera.saldo_usd = 25
    cartera.activos[0].cantidad = 2
    cartera.configurar_riesgo(30, 5, 3, 8)
    restaurado = historial.deshacer(cartera)

    assert id(cartera) == identidad
    assert cartera.saldo_usd == 1000
    assert cartera.activos[0].cantidad == 0.1
    assert cartera.limite_exposicion == 100
    assert restaurado.motivo == "Estado inicial"
    assert len(historial) == 0


def test_iterator_traverses_a_stable_reusable_snapshot():
    from patterns.iterator import ColeccionTrading

    originales = ["Bitcoin", "Ethereum"]
    coleccion = ColeccionTrading(originales)
    originales.append("Solana")

    assert list(coleccion) == ["Bitcoin", "Ethereum"]
    assert list(coleccion) == ["Bitcoin", "Ethereum"]
    assert len(coleccion) == 2


def test_mediator_and_memento_integrate_with_successful_order_execution():
    from patterns.facade import TradingPlatformFacade

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    cartera = facade.obtener_cartera("Cartera Principal")
    saldo_inicial = cartera.saldo_usd

    registro = facade.crear_y_ejecutar_orden(
        "MARKET", "COMPRA", "A", "Bitcoin", 0.001, cartera.nombre
    )

    portfolio_service = facade._trading.portfolio_service
    assert registro.estado.value == "EJECUTADA"
    assert cartera.saldo_usd < saldo_inicial
    assert len(portfolio_service.listar_puntos_control(cartera.nombre)) == 1
    assert portfolio_service.eventos_trading()[-1]["orden_id"] == registro.id

    portfolio_service.restaurar_ultimo_estado(cartera.nombre)
    assert cartera.saldo_usd == saldo_inicial
    assert cartera.buscar_posicion("Bitcoin") is None


def test_iterator_integrates_with_portfolio_positions_and_order_history():
    from patterns.facade import TradingPlatformFacade

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    facade.crear_y_ejecutar_orden(
        "MARKET", "COMPRA", "A", "Bitcoin", 0.001, "Cartera Principal"
    )

    positions = facade._trading.portfolio_service.iterar_posiciones("Cartera Principal")
    history = facade._trading.iterar_historial()

    assert [position.nombre for position in positions] == ["Bitcoin"]
    assert [order.activo for order in history] == ["Bitcoin"]


def test_mediator_rolls_back_portfolio_when_order_update_fails(monkeypatch):
    from patterns.facade import TradingPlatformFacade

    def fail_purchase(_cartera, _activo, _cantidad, _precio):
        raise RuntimeError("Fallo simulado al actualizar la posición")

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    cartera = facade.obtener_cartera("Cartera Principal")
    saldo_inicial = cartera.saldo_usd
    monkeypatch.setattr(Cartera, "registrar_compra", fail_purchase)

    try:
        facade.crear_y_ejecutar_orden(
            "MARKET", "COMPRA", "A", "Bitcoin", 0.001, cartera.nombre
        )
    except RuntimeError as exc:
        assert "Fallo simulado" in str(exc)
    else:
        raise AssertionError("La actualización simulada debía fallar")

    assert cartera.saldo_usd == saldo_inicial
    assert cartera.buscar_posicion("Bitcoin") is None
    assert facade._trading.portfolio_service.listar_puntos_control(cartera.nombre) == ()


def test_observer_notifies_market_subscribers_and_supports_unsubscribe():
    from services.market_service import MarketService

    class ObservadorPrueba:
        def __init__(self):
            self.eventos = []

        def actualizar(self, evento):
            self.eventos.append(evento)

    ExchangeConnectionManager.reset_for_tests()
    market = MarketService()
    observer = ObservadorPrueba()
    market.suscribir_observador(observer)

    price = market.obtener_precio("Bitcoin", "A")
    assert len(observer.eventos) == 1
    assert observer.eventos[0].activo == "Bitcoin"
    assert observer.eventos[0].exchange == "A"
    assert observer.eventos[0].precio == price
    assert market.cancelar_suscripcion(observer) is True

    market.obtener_precio("Ethereum", "A")
    assert len(observer.eventos) == 1


def test_observer_failure_does_not_interrupt_market_price_retrieval():
    from patterns.observer import PublicadorMercado, EventoPrecioMercado
    from datetime import datetime

    class ObservadorDefectuoso:
        def actualizar(self, _evento):
            raise RuntimeError("Fallo aislado del observador")

    publisher = PublicadorMercado()
    publisher.suscribir(ObservadorDefectuoso())
    event = EventoPrecioMercado("A", "Bitcoin", "BTC", 60000.0, datetime.now())
    errors = publisher.notificar(event)
    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)


def test_state_pattern_controls_order_transitions_and_terminal_states():
    from models.order import ExecutionResult, EstadoOrden, OrdenRegistro
    from patterns.state import MaquinaEstadoOrden

    registro = OrdenRegistro()
    machine = MaquinaEstadoOrden(registro)
    pending = ExecutionResult(EstadoOrden.PENDIENTE, "Esperando precio", 0)
    machine.procesar(pending)
    assert machine.estado_actual == EstadoOrden.PENDIENTE
    assert machine.es_terminal is False

    executed = ExecutionResult(EstadoOrden.EJECUTADA, "Ejecutada", 125.0)
    machine.procesar(executed)
    assert machine.estado_actual == EstadoOrden.EJECUTADA
    assert machine.es_terminal is True
    assert registro.total == 125.0
    assert registro.mensaje == "Ejecutada"

    try:
        machine.procesar(pending)
    except ValueError as exc:
        assert "estado final" in str(exc)
    else:
        raise AssertionError("Una orden ejecutada no debe volver a pendiente")


def test_strategy_pattern_preserves_default_risk_and_supports_preventive_policy():
    from models.portfolio import Posicion
    from patterns.strategy import EstrategiaRiesgoPreventiva
    from services.portfolio_service import PortfolioService

    service = PortfolioService()
    cartera = service.obtener_cartera("Cartera Principal")
    cartera.activos.append(Posicion("Bitcoin", 0.1, 40900.0))
    precios = {"Bitcoin": 40900.0}

    default_result = service.evaluar_riesgo(cartera, precios)
    assert default_result["alertas"] == []
    assert default_result["advertencias"] == []

    service.configurar_estrategia_riesgo(
        cartera.nombre, EstrategiaRiesgoPreventiva()
    )
    preventive_result = service.evaluar_riesgo(cartera, precios)
    assert preventive_result["alertas"] == []
    assert any("se aproxima" in warning for warning in preventive_result["advertencias"])


def test_strategy_can_be_selected_from_ui_keys_and_is_scoped_per_portfolio():
    from models.portfolio import Posicion
    from services.portfolio_service import PortfolioService

    service = PortfolioService()
    principal = service.obtener_cartera("Cartera Principal")
    principal.activos.append(Posicion("Bitcoin", 0.1, 40900.0))
    prices = {"Bitcoin": 40900.0}

    default_result = service.evaluar_riesgo(principal, prices)
    assert default_result["alertas"] == []
    assert default_result["advertencias"] == []
    assert service.obtener_tipo_estrategia_riesgo(principal.nombre) == "configurada"

    service.configurar_estrategia_riesgo_por_tipo(principal.nombre, "preventiva")
    preventive_result = service.evaluar_riesgo(principal, prices)
    assert service.obtener_tipo_estrategia_riesgo(principal.nombre) == "preventiva"
    assert preventive_result["alertas"] == []
    assert any("se aproxima" in warning for warning in preventive_result["advertencias"])

    cloned = service.clonar_cartera("Cartera de Prueba", 50.0)
    assert service.obtener_tipo_estrategia_riesgo(cloned.nombre) == "configurada"
    assert service.obtener_tipo_estrategia_riesgo(principal.nombre) == "preventiva"

    try:
        service.configurar_estrategia_riesgo_por_tipo(principal.nombre, "desconocida")
    except ValueError as exc:
        assert "Estrategia no válida" in str(exc)
    else:
        raise AssertionError("Una clave de estrategia desconocida debe rechazarse")


def test_template_method_integrates_purchase_and_sale_flows():
    from models.order import EstadoOrden
    from patterns.facade import TradingPlatformFacade

    ExchangeConnectionManager.reset_for_tests()
    facade = TradingPlatformFacade()
    cartera = facade.obtener_cartera("Cartera Principal")

    compra = facade.crear_y_ejecutar_orden(
        "MARKET", "COMPRA", "A", "Bitcoin", 0.01, cartera.nombre
    )
    posicion_despues_compra = cartera.buscar_posicion("Bitcoin")
    assert compra.estado == EstadoOrden.EJECUTADA
    assert posicion_despues_compra is not None
    cantidad_comprada = posicion_despues_compra.cantidad

    venta = facade.crear_y_ejecutar_orden(
        "MARKET", "VENTA", "A", "Bitcoin", 0.005, cartera.nombre
    )
    posicion_despues_venta = cartera.buscar_posicion("Bitcoin")
    assert venta.estado == EstadoOrden.EJECUTADA
    assert posicion_despues_venta is not None
    assert posicion_despues_venta.cantidad < cantidad_comprada
    assert facade.historial_ordenes()[0] is venta


def test_visitor_builds_type_specific_asset_sheets_through_market_service():
    from services.market_service import MarketService

    ExchangeConnectionManager.reset_for_tests()
    market = MarketService()

    crypto = market.obtener_ficha_activo("Bitcoin")
    nft = market.obtener_ficha_activo("CryptoArt #001")

    assert crypto["naturaleza"] == "Criptoactivo fungible"
    assert crypto["fraccionable"] is True
    assert nft["naturaleza"] == "Activo digital no fungible"
    assert nft["fraccionable"] is False
    assert nft["regla_cantidad"] == "Se negocia una unidad por operación."
