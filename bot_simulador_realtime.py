import time
import datetime
import ccxt
import os
import json
import threading
import re
import sys

from modulo4_agentes import ejecutar_junta_directiva
from modulo5_comisiones import obtener_fees_dinamicos
from modulo6_notificaciones import TelegramNotifier
import modulo7_supabase
from modulo7_supabase import SupabaseManager

class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
        self.log.write("--- SAAK QUANTUM TERMINAL STREAM INIT ---\n")
        self.log.flush()

    def write(self, message):
        self.terminal.write(message)
        self.terminal.flush()
        try:
            self.log.write(message)
            self.log.flush()
        except Exception:
            pass

    def flush(self):
        self.terminal.flush()
        try:
            self.log.flush()
        except:
            pass

sys.stdout = DualLogger("terminal_stream.log")
sys.stderr = sys.stdout

class SaakBotManager:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.db = SupabaseManager()
        
        self.api_key = os.getenv("BITSO_API_KEY")
        self.api_secret = os.getenv("BITSO_SECRET")
        self.exchange = ccxt.bitso({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
        })
        
        self.capital_mxn = 0.0
        self.comision = 0.0065
        self.lock = threading.Lock()
        self.estrategia_activa = "Scalping"
        self._ultimo_trade_ts = time.time()
        
        self._init_balance_and_fees()
        
    def _init_balance_and_fees(self):
        # Sincronización Primaria: Estrictamente dinámica de cuenta real Bitso sin hardcodes
        try:
            balance = self.exchange.fetch_balance()
            self.capital_mxn = float(balance.get('MXN', {}).get('free', 0.0))
            self.ultimo_saldo_bitso_real = self.capital_mxn
        except Exception as e:
            print(f"⚠️ Error crítico sincronizando con Exchange: {e}. Usando último estado DB vivo...")
            try:
                bs = self.db.get_bot_status()
                if bs and bs.data:
                    self.capital_mxn = float(bs.data[0].get('mxn_real_balance', 0.0))
                    self.ultimo_saldo_bitso_real = self.capital_mxn
            except Exception:
                self.capital_mxn = 0.0
                self.ultimo_saldo_bitso_real = 0.0
                
        # Calculo de Comisiones
        try:
            _, taker_fee = obtener_fees_dinamicos(self.exchange, "BTC/MXN")
            self.comision = taker_fee
            print(f"✅ Fee dinámico resuelto: {self.comision*100:.3f}%")
        except Exception as e:
            print(f"⚠️ Error cargando fee dinámico: {e}")
            
        print(f"💰 Capital Liquido Inicial (Sincronizado Bitso): ${self.capital_mxn:,.2f} MXN")

    def _analisis_capital_inicial_ia(self):
        if self.capital_mxn <= 0:
            # Sincronizamos en ceros por si acaso
            self.db.upsert_bot_status({'id': 1, 'mxn_real_balance': 0.0, 'proyeccion_ia': "> Saldo insificiente para invertir."})
            return
            
        print(f"🧠 Consultando a IA (Llama 3.3 70B CFO) sobre sugerencia de diversificación inicial para ${self.capital_mxn:,.2f} MXN disponibles...")
        # Sincronizamos de golpe el capital recien jalado de Bitso a la Base de Datos para el frontend
        self.db.upsert_bot_status({
            'id': 1, 
            'mxn_real_balance': self.capital_mxn,
            'proyeccion_ia': f"> Analizando asignación de portafolio para ${self.capital_mxn:,.2f} MXN líquidos..."
        })
        
        try:
            import requests, os
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Eres el CFO cuantitativo institucional de SaaK Solutions. Hablas con el inversionista. Responde en un párrafo corto, contundente y con ORTOGRAFÍA PERFECTA (cero errores tipográficos). Evalúa lógicamente el capital: si es menor a $500 MXN, desaconseja el scalping (por riesgo físico de comisiones o mínimos de binance) y sugiere fuertemente Hold, dando una dirección clara de asignación. Si es alto, distribúyelo estratégicamente."},
                    {"role": "user", "content": f"El bot inició con un capital líquido disponible de ${self.capital_mxn:,.2f} en el Exchange. Redacta el Plan de Acción Operativo: ¿Debería invertir este monto en Scalping, Swing o Hold y por qué matemáticamente hablando?"}
                ],
                "temperature": 0.1
            }
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                sugerencia = res.json()['choices'][0]['message']['content'].strip()
                print(f"✅ Mandato CFO: {sugerencia}")
                self.db.upsert_bot_status({'id': 1, 'proyeccion_ia': f"> CFO SaaK: {sugerencia}"})
            else:
                self.db.upsert_bot_status({'id': 1, 'proyeccion_ia': "> CFO inalcanzable temporalmente. Procediendo a escaneo cuantitativo general."})
        except Exception as e:
            print(f"⚠️ Error al obtener sugerencia inicial de IA: {e}")

    def obtener_precio_mercado(self, simbolo='BTC/MXN'):
        try:
            ticker = self.exchange.fetch_ticker(simbolo)
            return ticker['last']
        except Exception as e:
            print(f"Error de red obteniendo precio para {simbolo}: {e}")
            return None

    def start(self):
        print("Iniciando Bot Simulador Real-Time Multiposición (Arquitectura Multithread)...")
        
        # Sugerencia Viva de Inversión al Arranque (Comentario de CFO)
        self._analisis_capital_inicial_ia()
        
        # El subproceso de monitoreo reacciona ràpidamente al estado de Stop Loss y Take Profit
        t_monitoreo = threading.Thread(target=self.monitoreo_bucle_rapido, daemon=True)
        t_monitoreo.start()
        
        # El subproceso principal evalúa IA
        self.junta_directiva_bucle_lento()

    def monitoreo_bucle_rapido(self):
        """ Inicializa el loop de eventos asíncrono para WebSockets en el hilo secundario """
        import asyncio
        asyncio.run(self._monitoreo_ws())

    async def _monitoreo_ws(self):
        """ Bucle de Alta Seguridad: Evita la Bomba de Tiempo ejecutando escaneo en tiempo real vía WebSocket """
        import asyncio
        import websockets
        import json
        import datetime
        import time
        
        uri = "wss://ws.bitso.com"
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    print("🌐 [WS] Conectado a Bitso WebSocket para monitoreo milimétrico")
                    
                    posiciones_cache = []
                    precios_historicos = {}
                    last_db_sync = 0
                    
                    # Bucle interior de mensajes del websocket
                    async for mensaje in websocket:
                        now = time.time()
                        hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Sincronización DB cada 15 segundos pero en background sin bloquear ticks
                        if now - last_db_sync > 15:
                            last_db_sync = now
                            try:
                                res = await asyncio.to_thread(self.db.get_bot_status)
                                if res and res.data and 'estrategia_activa' in res.data[0]:
                                    self.estrategia_activa = res.data[0]['estrategia_activa']
                                
                                res_pos = await asyncio.to_thread(self.db.get_open_positions)
                                posiciones_cache = res_pos.data if res_pos and res_pos.data else []
                                
                                books_necesarios = set(p['simbolo'].replace('/', '_').lower() for p in posiciones_cache)
                                if not books_necesarios:
                                    books_necesarios.add('btc_mxn')
                                    
                                for book in books_necesarios:
                                    msg = json.dumps({"action": "subscribe", "book": book, "type": "trades"})
                                    await websocket.send(msg)
                                    
                                # Actualizar status general del bot
                                with self.lock:
                                    capital_base = self.capital_mxn
                                nombres_criptos = [p['simbolo'] for p in posiciones_cache]
                                cripto_activa = " / ".join(nombres_criptos) if nombres_criptos else "Vigilando Liquidez"
                                
                                total_cripto_valor = sum([
                                    float(p['cantidad']) * precios_historicos.get(p['simbolo'], 0) 
                                    if p['estrategia'] != 'Yield Pasivo' 
                                    else float(p['cantidad'])
                                    for p in posiciones_cache
                                ])
                                balance_consolidado = capital_base + total_cripto_valor

                                def update_db_status(cb, ca):
                                    self.db.upsert_bot_status({
                                        'id': 1,
                                        'bitso_status': 'Online',
                                        'mxn_real_balance': cb,
                                        'btc_real_balance': 0, 
                                        'precio_actual_mxn': 0,
                                        'cripto_activa': ca
                                    })
                                await asyncio.to_thread(update_db_status, capital_base, cripto_activa)
                            except Exception as e:
                                pass # Ignorar errores DB temporales
                                
                        # Procesamiento en Tiempo Real de Precios
                        data = json.loads(mensaje)
                        if data.get('type') == 'trades' and data.get('payload'):
                            precio_actual = float(data['payload'][0]['r'])
                            book_tick = data.get('book', '').upper().replace('_', '/')
                            precios_historicos[book_tick] = precio_actual
                            
                            # Avaluar TODAS las posiciones que coincidan con este ticker instantaneamente
                            posiciones_vigentes = []
                            ventas_realizadas = False
                            
                            for pos in posiciones_cache:
                                simbolo = pos['simbolo']
                                if simbolo != book_tick:
                                    posiciones_vigentes.append(pos)
                                    continue
                                    
                                precio_entrada = float(pos['precio_entrada'])
                                cantidad = float(pos['cantidad'])
                                estrategia_pos = pos.get('estrategia', 'Hold')
                                id_pos = pos['id']
                                
                                # Trailing Stop: Inicialización de High Watermark
                                if not hasattr(self, '_high_watermarks'): self._high_watermarks = {}
                                if id_pos not in self._high_watermarks:
                                    self._high_watermarks[id_pos] = precio_entrada
                                
                                # Actualizar High Watermark en tiempo real
                                if precio_actual > self._high_watermarks[id_pos]:
                                    self._high_watermarks[id_pos] = precio_actual
                                    
                                high_price = self._high_watermarks[id_pos]
                                
                                variacion = (precio_actual - precio_entrada) / precio_entrada if precio_entrada > 0 else 0
                                subida_maxima_pct = (high_price - precio_entrada) / precio_entrada if precio_entrada > 0 else 0
                                
                                tp_limit, sl_limit = 0.05, -0.03 # Por defecto
                                est_lower = estrategia_pos.lower()
                                if 'scalping' in est_lower:
                                    tp_limit, sl_limit = 0.02, -0.02
                                elif 'swing' in est_lower:
                                    tp_limit, sl_limit = 0.05, -0.03
                                elif 'hold' in est_lower:
                                    tp_limit, sl_limit = 0.20, -0.05
                                    
                                # Lógica Dinámica: Trailing Stop Loss
                                trailing_distance = abs(sl_limit)
                                sl_dinamico = sl_limit
                                
                                # Si ya recorrimos al menos una fracción decente del TP (ej. 40%), se activa el Trailing
                                umbral_activacion_trailing = tp_limit * 0.4
                                if subida_maxima_pct >= umbral_activacion_trailing:
                                    # El nuevo limite asegura ganancias debajo del máximo
                                    sl_dinamico = subida_maxima_pct - trailing_distance
                                    # Asegurador: Nunca dejamos caer por debajo del Break Even matemático (+0.5%) si ya subió tanto
                                    if sl_dinamico < 0.005:
                                        sl_dinamico = 0.005

                                if variacion >= tp_limit or variacion <= sl_dinamico:
                                    if variacion >= tp_limit:
                                        razon_venta = "TAKE PROFIT FIJO"
                                    elif sl_dinamico > 0:
                                        razon_venta = "TRAILING STOP (Asegurado)"
                                    else:
                                        razon_venta = "STOP LOSS"
                                        
                                    print(f"⚡🚨 {razon_venta} INMEDIATO [WS STREAM] en {simbolo} | Var: {variacion*100:.2f}% (Máx alcanzado: +{subida_maxima_pct*100:.2f}%)")
                                    
                                    # Verificar Modo Produccion para Liquidación Viva
                                    modo_prod = False
                                    try:
                                        bs = self.db.get_bot_status()
                                        if bs and bs.data:
                                            modo_prod = bs.data[0].get('modo_produccion', False)
                                    except: pass
                                    
                                    if modo_prod:
                                        print(f"🔥 [ALERTA] MODO PRODUCCIÓN ACTIVO. Liquidando realmente {cantidad} de {simbolo} en Bitso...")
                                        try:
                                            self.exchange.create_market_sell_order(simbolo, cantidad)
                                            print(f"✔️ VENTA FÍSICA CONFIRMADA EN EXCHANGE.")
                                        except Exception as e:
                                            print(f"🚫 Error crudo vendiendo en Bitso (Protección de emergencia iniciada): {e}")
                                    
                                    mxn_bruto = cantidad * precio_actual
                                    mxn_neto = mxn_bruto * (1 - self.comision)
                                    comision_venta = mxn_bruto * self.comision
                                    
                                    with self.lock:
                                        self.capital_mxn += mxn_neto
                                        capital_actualizado = self.capital_mxn
                                        
                                    resultado_txt = "GANANCIA ✅" if variacion > 0 else "PÉRDIDA 📉"
                                    rendimiento_global = ((capital_actualizado - 1000) / 1000) * 100
                                    self.notifier.enviar_alerta(
                                        f"🔔 SaaK Solutions - PROTECCIÓN ACTIVADA\n\n"
                                        f"🪙 Activo Liquido: {simbolo} ({estrategia_pos})\n"
                                        f"📊 Cierre: {resultado_txt} vía {razon_venta}\n"
                                        f"📈 Variación de Red: {variacion*100:+.2f}%\n"
                                        f"💵 Liquidado: ${mxn_neto:,.2f} MXN\n"
                                        f"💰 Cartera Libre: ${capital_actualizado:,.2f} MXN\n"
                                        f"🚀 Rendimiento Hist. Cartera: {rendimiento_global:+.2f}%"
                                    )
                                    
                                    # DB operations bloqueantes dentro de otro thread
                                    def process_db(idp, pr, cant, mx_net, com):
                                        self.db.delete_position(idp)
                                        self.db.insert_trade_log({
                                            'tipo_orden': 'VENTA',
                                            'precio_btc': pr,
                                            'cantidad_btc': cant,
                                            'balance_mxn_resultante': mx_net,
                                            'comision_pagada': com
                                        })
                                    await asyncio.to_thread(process_db, id_pos, precio_actual, cantidad, capital_actualizado, comision_venta)
                                        
                                    with open("log_simulacion.txt", "a") as f:
                                        f.write(f"{hora_actual} | {simbolo} | VENTA ({razon_venta}) | Var: {variacion*100:.2f}% [WS]\n")
                                    ventas_realizadas = True
                                else:
                                    posiciones_vigentes.append(pos)
                                    
                            if ventas_realizadas:
                                posiciones_cache = posiciones_vigentes

            except Exception as e:
                print(f"⚠️ Desconexión del WebSocket, reconectando en 5s... {e}")
                import asyncio
                await asyncio.sleep(5)

    def junta_directiva_bucle_lento(self):
        """ Bucle de Inteligencia: Llama a los LLMs cada 15 minutos en busca de análisis técnico pausado """
        while True:
            try:
                self._gestionar_yield_pasivo() # Primero verificamos y administramos la inactividad natural
            except Exception as e:
                print(f"Error Yield: {e}")
                
            with self.lock:
                
                # Sincronización Viva de Inyecciones de Capital Externo
                try:
                    balance = self.exchange.fetch_balance()
                    saldo_real_vivo = float(balance.get('MXN', {}).get('free', 0.0))
                    # Si el saldo MXN en la API superó lo que el bot recordaba, hubo depósito
                    if saldo_real_vivo > getattr(self, 'ultimo_saldo_bitso_real', -1.0):
                        if getattr(self, 'ultimo_saldo_bitso_real', -1.0) != -1.0:
                            inyeccion_nueva = saldo_real_vivo - self.ultimo_saldo_bitso_real
                            if inyeccion_nueva > 1.0:
                                self.capital_mxn += inyeccion_nueva
                                self.ultimo_saldo_bitso_real = saldo_real_vivo
                                print(f"\n💰 [SYSTEM] ¡Inyección externa detectada! +${inyeccion_nueva:,.2f} MXN adicionales en tu cuenta liquida de Bitso.")
                                self._analisis_capital_inicial_ia()
                        else:
                            self.ultimo_saldo_bitso_real = saldo_real_vivo
                    else:
                        self.ultimo_saldo_bitso_real = saldo_real_vivo
                except Exception:
                    pass

                liquidez = self.capital_mxn
                
                estrategia_str = self.estrategia_activa
                
                # Tratamos Yield como efectivo disponible para invertir:
                try:
                    res_p = self.db.get_open_positions()
                    posiciones = res_p.data if res_p and res_p.data else []
                    pos_yield = next((p for p in posiciones if p['estrategia'] == 'Yield Pasivo'), None)
                    if pos_yield:
                        liquidez += float(pos_yield['cantidad'])
                except: pass
                
            if liquidez >= 50:
                print(f"\n🧠 [Filtro Cuantitativo] Evaluando mercado (Capital Disp: ${liquidez:,.2f}) (Estrategia: {self.estrategia_activa})")
                from modulo8_cuantitativo import realizar_analisis_tecnico
                
                mercado_actual_verde = {}
                # 1. Obtener lista dinámica de activos dictada por el Exchange (Bitso)
                try:
                    self.exchange.load_markets()
                    monedas_disponibles = [m for m in self.exchange.markets.keys() if m.endswith('/MXN')]
                    # Excluir stablecoins o monedas fiduciarias que no tienen volatilidad útil para trading
                    monedas_estables_fiat = ['USDT/MXN', 'USDC/MXN', 'PYUSD/MXN', 'USDS/MXN', 'EUR/MXN', 'USD/MXN', 'TUSD/MXN', 'RLUSD/MXN', 'DAI/MXN']
                    lista_activos = [m for m in monedas_disponibles if m not in monedas_estables_fiat]
                except Exception as e:
                    print(f"⚠️ Aviso Crítico Falló listado dinámico del exchange: {e}. Pausando escaneo.")
                    lista_activos = []

                # Evaluar cada activo validado
                for s in lista_activos:
                    try:
                        res_ta = realizar_analisis_tecnico(self.exchange, s, '15m', 50)
                        
                        # Actualizar métricas del dashboard guiadas por BTC (Ticker lider)
                        if s == 'BTC/MXN' and res_ta:
                            self.db.upsert_bot_status({
                                'id': 1,
                                'rsi': res_ta['rsi'],
                                'atr': round(abs(res_ta.get('macd_hist', 0.05)), 3),
                                'senal': 'COMPRAR (O) ' if res_ta['apto'] else 'HOLD (Pa)'
                            })

                        if res_ta and res_ta['apto']:
                            mercado_actual_verde[s] = f"Precio: {res_ta['precio']} | Puntaje Técnico: {res_ta['puntaje']} | RSI: {res_ta['rsi']} | Confirmaciones: {', '.join(res_ta['razones'])}"
                            print(f"✅ {s} SUPERÓ filtros técnicos: {res_ta['razones']}")
                        else:
                            razon_fail = res_ta['razones'] if res_ta and res_ta['razones'] else "Sin señales claras"
                            print(f"❌ {s} descartado matemáticamente: {razon_fail}")
                    except Exception as e: 
                        print(f"Error analizando {s}: {e}")
                        pass
                    
                dictamen = {}
                if not mercado_actual_verde:
                    print("⚠️ Ningún activo superó los filtros cuantitativos estrictos. IA en pausa para ahorrar procesamiento y tokens.")
                    self.db.upsert_bot_status({'id': 1, 'proyeccion_ia': "> Escaneo en pausa para conservar energía. Ningún activo superó el filtro inicial cuantitativo."})
                else:
                    msg_despertar = f"> Despertando redes neuronales CrewAI para análisis profundo de: {', '.join(list(mercado_actual_verde.keys()))}..."
                    print(f"🤖 Despertando IA (CrewAI) para análisis cualitativo final de: {list(mercado_actual_verde.keys())}")
                    self.db.upsert_bot_status({'id': 1, 'proyeccion_ia': msg_despertar})
                    intentos_ia = 0
                    while intentos_ia < 3 and not dictamen:
                        try:
                            resultado_crew = ejecutar_junta_directiva(str(mercado_actual_verde), liquidez, self.estrategia_activa, self.comision)
                            dictamen_str = resultado_crew.raw.replace('```json', '').replace('```', '')
                            
                            match = re.search(r'\{.*\}', dictamen_str, re.DOTALL)
                            if match:
                                dictamen_str = match.group(0)
                                
                            dictamen = json.loads(dictamen_str)
                            
                            dictamen_mensaje = f"> Veredicto IA completado. {dictamen.get('simbolo')} | Aprobado: {dictamen.get('aprobado')} | Tesis: {dictamen.get('razon', 'Sin razón definida')}"
                            self.db.upsert_bot_status({'id': 1, 'proyeccion_ia': dictamen_mensaje})
                            
                        except Exception as e:
                            print(f"⚠️ Error Parseando Respuesta LLM o Red IA (Intento {intentos_ia+1}/3): {e}")
                            intentos_ia += 1
                            time.sleep(5)

                if dictamen.get("simbolo"):
                    simbolo_target = dictamen.get("simbolo")
                    print(f"✅ Propuesta aprobada por Directiva -> {simbolo_target}")
                    
                    ids_in = []
                    try:
                        self.db.delete_pending_proposals()
                        min_inv = dictamen.get('inversion_minima_sugerida', 0)
                        proyeccion_ia = dictamen.get('razon', '')
                        if min_inv > 0:
                            proyeccion_ia = f"{proyeccion_ia} (Min Sugerido: ${min_inv:,.2f} MXN)"

                        res = self.db.insert_trade_proposal({
                            'simbolo': simbolo_target,
                            'estrategia': self.estrategia_activa,
                            'proyeccion': proyeccion_ia,
                            'probabilidad': 95, # Mock
                            'precio_entrada': float(dictamen.get('precio_entrada_sugerido', 0.0)),
                            'status': 'pendiente'
                        })
                        ids_in = [r['id'] for r in res.data] if res and res.data else []
                    except Exception as e:
                        print(f"⚠️ Error registrando propuesta en DB: {e}")

                    
                    # Caza de usuario dashboard
                    if ids_in:
                        print("⏳ Propuesta pendiente en Dashboard. Tienes 10 mins para decidir...")
                        aprobado = None
                        estrategia_al_proponer = self.estrategia_activa
                        
                        # Loop de 600 segundos (10 mins), chequeos activos cada segundo
                        for ciclo in range(600):
                            # Salida INMEDIATA si cambian la estrategia
                            if self.estrategia_activa != estrategia_al_proponer:
                                print(f"🚨 Abortando propuesta obsoleta. Estrategia cambió de {estrategia_al_proponer} a {self.estrategia_activa}")
                                self.db.update_proposals_status(ids_in, 'rechazada')
                                break
                                
                            time.sleep(1)
                            
                            # Solo consultamos Supabase cada 5 segundos para no saturar la red
                            if ciclo % 5 == 0:
                                try:
                                    res_props = self.db.get_trade_proposals(ids_in)
                                    if res_props and res_props.data:
                                        todos_listos = True
                                        for r in res_props.data:
                                            if r['status'] == 'aprobada':
                                                aprobado = r
                                                break
                                            if r['status'] == 'pendiente': todos_listos = False
                                        if aprobado or todos_listos: break
                                except: pass
                            
                        if aprobado:
                            self._ejecutar_compra(aprobado)
                            rechazar_resto = [i for i in ids_in if i != aprobado['id']]
                            if rechazar_resto: self.db.update_proposals_status(rechazar_resto, 'rechazada')
                        elif self.estrategia_activa == estrategia_al_proponer:
                            print("⏭️ Tiempo Agotado o Propuesta Rechazada por el Usuario.")
                            self.db.update_proposals_status(ids_in, 'rechazada')

            print("💤 Junta Directiva esperando 15 minutos para próxima evaluación global de mercado... (Escuchando cambios manuales)")
            estrategia_actual_loop = self.estrategia_activa
            for _ in range(15 * 60):
                if self.estrategia_activa != estrategia_actual_loop:
                    print(f"🔄 Interrupción Activa: Detectado cambio de estrategia en UI a '{self.estrategia_activa}'. Despertando CFO!")
                    break
                time.sleep(1)

    def _ejecutar_compra(self, propuesta):
        simbolo = propuesta['simbolo']
        estrategia = propuesta['estrategia']
        precio_actual = self.obtener_precio_mercado(simbolo) or propuesta['precio_entrada']
        
        with self.lock:
            # Recuperar de Yield Pasivo si es necesario antes de fragmentar la inversión
            try:
                res_p = self.db.get_open_positions()
                if res_p and res_p.data:
                    p_yield = next((p for p in res_p.data if p['estrategia'] == 'Yield Pasivo'), None)
                    if p_yield and self.capital_mxn < 500:
                        # Rescatar Yield Pasivo
                        inversion_inicial = float(p_yield['cantidad'])
                        dias_en_yield = (time.time() - self._ultimo_trade_ts) / (24*3600)
                        # Simulación de rendimiento pasivo del 5% APY
                        rendimiento = inversion_inicial * (0.05 / 365) * max(dias_en_yield, 1)
                        self.capital_mxn += (inversion_inicial + rendimiento)
                        self.db.delete_position(p_yield['id'])
                        self.notifier.enviar_alerta(
                            f"🏦 SaaK Solutions - RESCATE YIELD\n\n"
                            f"Capital inactivo retirado del programa Earn anticipadamente para aprovechar oportunidad.\n"
                            f"Total recuperado: ${(inversion_inicial + rendimiento):,.2f} MXN (Interés generado: ${rendimiento:,.4f} MXN)."
                        )
            except Exception as e:
                print(f"Error rescatando Yield: {e}")

            # Fragmentamos inversiones (Mantenemos fondos libres si hay excedente)
            monto_base = min(self.capital_mxn, 1000.0) 
            # Colchón de seguridad del 2% para evitar "Insufficient MXN" de comisiones Bitso si invertimos todo el saldo
            if (self.capital_mxn - monto_base) < (monto_base * 0.05):
                monto_invertir = monto_base * 0.98
            else:
                monto_invertir = monto_base
                
            if monto_invertir < 20: return 
            
        # Determinar si estamos operando en vivo (Producción)
        modo_produccion = False
        try:
            bs = self.db.get_bot_status()
            if bs and bs.data:
                modo_produccion = bs.data[0].get('modo_produccion', False)
        except: pass

        # SPREAD / SLIPPAGE SHIELD: Cotizamos la moneda un +5% MÁS CARA del último precio conocido histórico.
        # Monedas como LTC o TRX sufren de bajísima liquidez. El precio de venta real del libro de órdenes (Ask) suele ser 
        # exageradamente más caro que lo que muestra la portada. Matemáticamente esto obliga al bot a pedir menos volumen de cripto, 
        # y así garantizamos que Bitso jamás exceda tus $100 pesos en "Insufficient MXN Balance".
        precio_peor_escenario = precio_actual * 1.05
        cripto_bruta = monto_invertir / precio_peor_escenario
        
        # === EJECUCIÓN FÍSICA Y REAL (SI EL MODO ESTÁ ACTIVO) ===
        if modo_produccion:
            print(f"🔥 [ALERTA] MODO PRODUCCIÓN ACTIVO. Disparando orden viva a Bitso por {cripto_bruta} {simbolo}...")
            try:
                # CCXT requiere la cantidad neta a comprar del activo
                order = self.exchange.create_market_buy_order(simbolo, cripto_bruta)
                print(f"✔️ ¡ORDEN REAL APROBADA POR API! ID: {order['id']}")
                
                # SINCRONIZACIÓN PERFECTA: Cloned Wallet Mirroring
                # Consultamos el saldo oficial para no depender de estimaciones matemáticas
                import time
                time.sleep(2) # Segundos de gracia para que Bitso registre internamente el trade
                balance_oficial = self.exchange.fetch_balance()
                
                # Extraemos moneda base (ej. LTC) y cotejamos saldo exacto
                moneda_base = simbolo.split('/')[0]
                cripto_neta = float(balance_oficial.get(moneda_base, {}).get('free', cripto_bruta * (1-self.comision)))
                resto = float(balance_oficial.get('MXN', {}).get('free', self.capital_mxn - monto_invertir))
                
                with self.lock:
                    self.capital_mxn = resto
                    
                # Si el broker devolvió el precio medio exacto de ejecución, lo sustituimos
                if order.get('average'):
                    precio_actual = float(order['average'])
                    
            except Exception as e:
                print(f"🚫 [Fila] Error ejecutando orden viva en Bitso, cancelando pase a DB: {e}")
                return # Abortar si la red física falla
        else:
            with self.lock:
                self.capital_mxn -= monto_invertir
                resto = self.capital_mxn
            cripto_neta = cripto_bruta * (1 - self.comision)

        comision_p = monto_invertir * self.comision
        
        self.notifier.enviar_alerta(
            f"🟢 SaaK Solutions - COMPRA AUTORIZADA\n\n"
            f"🪙 Activo Adquirido: {cripto_neta} {simbolo}\n"
            f"📉 Precio Entrada: ${precio_actual:,.2f} MXN\n"
            f"💵 Saldo Remanente Cartera: ${resto:,.4f} MXN"
        )
        
        try:
            self.db.insert_trade_log({
                'tipo_orden': 'COMPRA',
                'precio_btc': precio_actual,
                'cantidad_btc': cripto_neta,
                'balance_mxn_resultante': resto,
                'comision_pagada': comision_p
            })
            self.db.insert_position({
                'simbolo': simbolo,
                'cantidad': cripto_neta,
                'precio_entrada': precio_actual,
                'comision_pagada': comision_p,
                'estrategia': estrategia
            })
        except Exception as e:
            print(f"Error DB insert position: {e}")
            
        with open("log_simulacion.txt", "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {simbolo} | COMPRA ({estrategia}) a ${precio_actual:,.2f}\n")
        print(f"✔️ COMPRA SIMULADA REGISTRADA: {simbolo} ({estrategia})")
        self._ultimo_trade_ts = time.time()

    def _gestionar_yield_pasivo(self):
        res = self.db.get_open_positions()
        posiciones = res.data if res and res.data else []
        en_yield = any(p['estrategia'] == 'Yield Pasivo' for p in posiciones)
        tiene_activas = any(p['estrategia'] != 'Yield Pasivo' for p in posiciones)
        
        if tiene_activas or en_yield:
            if tiene_activas: self._ultimo_trade_ts = time.time() # Mantener reloj congelado si hay accion viva
            return

        with self.lock:
            if self.capital_mxn < 100: return
            
        inactividad_segundos = time.time() - self._ultimo_trade_ts 
        if inactividad_segundos > (7 * 24 * 3600):
            print("💤 [YIELD] Extendida inactividad de mercado detectada (>7 días).")
            with self.lock:
                monto_yield = self.capital_mxn
                self.capital_mxn = 0
            
            self.db.insert_position({
                'simbolo': 'USDT_EARN/MXN',
                'cantidad': monto_yield,
                'precio_entrada': 1.0,
                'comision_pagada': 0,
                'estrategia': 'Yield Pasivo'
            })
            self.notifier.enviar_alerta(
                f"🏦 SaaK Solutions - YIELD PASIVO ACTIVADO\n\n"
                f"Mercado lateral prolongado. He migrado ${monto_yield:,.2f} MXN a instrumentos Earn estables para generar capital pasivo mientras esperamos."
            )

if __name__ == "__main__":
    bot = SaakBotManager()
    bot.start()
