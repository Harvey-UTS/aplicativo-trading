import random #Precios Randoms
import threading #Manejo de Hilos del Sistema (Procesos en Segundo Plano)
import time #Evita Retrasos Temporales

class ExchangeConnectionManager:
    _instance = None
    _lock = threading.Lock() #No se Creen Multiples Instancias

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init_sim() #Inicializa el Objeto o la Instancia
            return cls._instance

    def _init_sim(self):
        self.prices = {"BTC/USDT": 64500.50, "ETH/USDT": 3450.75, "SOL/USDT": 145.20}
        self.running = True
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _update_loop(self):
        while self.running:
            time.sleep(1.0)
            for pair in self.prices:
                self.prices[pair] = round(self.prices[pair] * (1 + random.uniform(-0.003, 0.003)), 2)

    def get_price(self, pair):
        return self.prices.get(pair)

    def stop(self):
        self.running = False
        print("\n🛑 Conexión con APIs finalizada.")


if __name__ == "__main__":
    api = ExchangeConnectionManager()
    
    # Escuchador en segundo plano para la tecla 'q'
    def listen_stop():
        if input().lower() == 'q':
            api.stop()
            
    threading.Thread(target=listen_stop, daemon=True).start()

    print("🟢 Simulación activa. Presiona 'Ctrl + C' o ingresa 'q' + Enter para salir.\n")
    try:
        count = 1
        while api.running:
            print(f"[{count:04d}] BTC: ${api.get_price('BTC/USDT')} USDT | ETH: ${api.get_price('ETH/USDT')} USDT")
            count += 1
            time.sleep(1.5)
    except KeyboardInterrupt:
        api.stop()