# SaaK Quantum Trading Bot

SaaK Quantum es un avanzado motor de trading institucional y dashboard de operaciones optimizado para criptomonedas. Construido con una arquitectura de sistema distribuido, combina la ejecución de alta frecuencia, modelos matemáticos cuantitativos de volatilidad y un panel directivo multi-agente impulsado por IA de vanguardia.

## 🔥 Características Principales

* **Motor Real-Time Multithread**: Utiliza conexiones WebSocket (Bitso) ultrarrápidas y en hilos independientes para monitorear milimétricamente el movimiento del mercado y liquidar en Stop-Loss o Take-Profit instantáneo sin cuellos de botella bloqueantes.
* **Junta Directiva Artificial (CrewAI)**: Agentes de IA impulsados por Llama-3.3-70B que funcionan como un comité de inversión completo (CFO), tomando decisiones estratégicas basadas en el análisis técnico generado por algoritmos matemáticos (RSI, MACD, ATR).
* **Consola de Operaciones en Vivo**: Un lujoso dashboard moderno construido con React (Web Dashboard) con estética Bento-Box, proyecciones reales, y una **terminal viva** renderizada en interfaz gráfica que lee directamente la memoria de streaming del bot en tiempo real.
* **Protección Ante Riesgos Dinámica**: Cálculos automatizados de liquidez basados en slippage, volumen en libro de órdenes, trailing stop-losses paramétricos y simulación rigurosa.
* **Notificaciones por Telegram**: Eventos de inversión críticos con trazabilidad instantánea a tu dispositivo móvil.
* **Estado en la Nube (Supabase)**: Streaming vivo de datos entre la arquitectura base de Python y el Frontend por medio de Websockets con PostgreSQL.

## 🛠️ Tecnologías Empleadas

- **Backend**: `Python 3.11+`, `ccxt` (Conexiones a Exchange), `CrewAI`, `Groq Cloud (LLM)`, `pandas` / `ta` (Análisis Técnico Avanzado), `websockets`.
- **Frontend**: `React.js`, `Vite`, `CSS Moderno (Glassmorphism)`, `@supabase/supabase-js`.
- **Infraestructura**: `Supabase` (Base de Datos Realtime en la Nube).

## 🚀 Arquitectura del Proyecto

- `bot_simulador_realtime.py`: El orquestador principal. Arranca los hilos de red, intercepta salidas de terminal estándar, evalúa liquidez e inicia el streaming en vivo.
- `modulo0_backtest` a `modulo8_cuantitativo`: Conjunto de herramientas dedicadas a la conectividad del API, operaciones con comisiones dinámicas, notificaciones asíncronas y modelos estadísticos financieros de mercado.
- `/saak-dashboard/`: Aplicación frontend que escucha las suscripciones a Supabase e interactúa con el orquestador backend con su plugin Vite de terminal.

## 💻 Instalación y Uso

### 1. Clonar y configurar Backend (Orquestador)

```bash
git clone https://github.com/SAlejandroHP/tranding-bot.git
cd tranding-bot
python -m venv venv
source venv/bin/activate
pip install -r reqs_clean.txt
```

Crea tu archivo `.env` en la raíz del proyecto para alojar las claves:
```env
BITSO_API_KEY=tu_clave
BITSO_SECRET=tu_secreto
GROQ_API_KEY=tu_clave_de_groq
TELEGRAM_TOKEN=tu_token_telegram
TELEGRAM_CHAT_ID=tu_chat_id
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_secret_role
```

### 2. Arrancar la CLI y Motor Backend

```bash
python bot_simulador_realtime.py
```

### 3. Configurar y arrancar Dashboard Visual

En otra nueva ventana de terminal:
```bash
cd saak-dashboard
npm install
npm run dev
```

> Tu `.env` o las variables de entorno de Vite requerirán estar expuestos en tu cliente de desarrollo (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_GROQ_API_KEY`).

## ⚠️ Nota Legal
Este sistema incluye soporte y capacidades funcionales para *Trading Real* mediante switches de Producción. La ejecución es algorítmica y sujeta a inestabilidades del mercado y riesgo de hardware financiero. Úsalo bajo tu propio alcance y responsabilidad.
