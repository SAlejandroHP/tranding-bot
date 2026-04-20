import React, { useState, useEffect, useRef } from 'react';
import { supabase } from '../services/supabaseClient';
import { GROQ_URL, GROQ_MODEL, GROQ_API_KEY } from '../config/env';

import MainLayout from '../layouts/MainLayout';
import ProposalCard from '../components/ProposalCard';
import TypewriterText from '../components/TypewriterText';

// --- Efectos de Sonido (Web Audio API) ---
const playPing = () => {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    oscillator.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.1); // A6
    
    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
    
    oscillator.start(audioCtx.currentTime);
    oscillator.stop(audioCtx.currentTime + 0.5);
  } catch (e) {
    console.error('Error al reproducir audio:', e);
  }
};

const Dashboard = ({ onLogout }) => {
  const [trades, setTrades] = useState([]);
  const [botStatus, setBotStatus] = useState(null);
  const [propuestas, setPropuestas] = useState([]);
  const [openPositions, setOpenPositions] = useState([]);
  const [analisisIA, setAnalisisIA] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastTradeId, setLastTradeId] = useState(null);
  const [loadingConfig, setLoadingConfig] = useState(false);
  const [showProdModal, setShowProdModal] = useState(false);
  
  const [terminalLogs, setTerminalLogs] = useState([]);
  const terminalRef = useRef(null);

  const loadInitialData = async () => {
    if (!supabase) return;
    try {
      const { data: posData } = await supabase.from('open_positions').select('*').order('created_at', { ascending: false });
      if (posData) setOpenPositions(posData);

      const { data: statusData } = await supabase.from('bot_status').select('*').eq('id', 1).single();
      if (statusData) setBotStatus(statusData);

      const { data: tradesData } = await supabase.from('trades_log').select('*').order('created_at', { ascending: false }).limit(10);
      if (tradesData) setTrades(tradesData);

      const { data: propuestasData } = await supabase.from('trade_proposals').select('*').eq('status', 'pendiente').order('probabilidad', { ascending: false });
      if (propuestasData) setPropuestas(propuestasData);

    } catch (err) {
      console.error('Error fetch inicial:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!supabase) {
      setAnalisisIA('Aviso: Configura las credenciales de Supabase');
      setLoading(false);
      return;
    }

    loadInitialData();
    
    const openPositionsChannel = supabase.channel('public:open_positions')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'open_positions' }, async () => {
          const { data } = await supabase.from('open_positions').select('*').order('created_at', { ascending: false });
          if (data) setOpenPositions(data);
        })
      .subscribe();

    const botStatusChannel = supabase.channel('public:bot_status')
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'bot_status', filter: 'id=eq.1' }, (payload) => {
          setBotStatus(prev => ({ ...prev, ...payload.new }));
        })
      .subscribe();

    const tradesChannel = supabase.channel('public:trades_log')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'trades_log' }, (payload) => {
          playPing();
          setTrades(prevTrades => [payload.new, ...prevTrades].slice(0, 10));
        })
      .subscribe();

    const proposalsChannel = supabase.channel('public:trade_proposals')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'trade_proposals' }, async () => {
           const { data } = await supabase.from('trade_proposals').select('*').eq('status', 'pendiente').order('probabilidad', { ascending: false });
           if (data) setPropuestas(data);
        })
      .subscribe();

    return () => {
      supabase.removeChannel(openPositionsChannel);
      supabase.removeChannel(botStatusChannel);
      supabase.removeChannel(tradesChannel);
      supabase.removeChannel(proposalsChannel);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch('/api/terminal-logs');
        if (res.ok) {
          const data = await res.json();
          setTerminalLogs(data.logs || []);
        }
      } catch (err) {}
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 1500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  useEffect(() => {
    if (trades.length > 0) {
      const latestTrade = trades[0].id || trades[0].created_at;
      if (latestTrade !== lastTradeId) {
        setLastTradeId(latestTrade);
        generarAnalisis(trades);
      }
    }
  }, [trades, lastTradeId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function generarAnalisis(datosTrades) {
    try {
      setAnalisisIA('');
      const prompt = `Eres el analista financiero de SaaK Solutions. Analiza estos últimos movimientos y manda una línea de terminal resumiendo estatus (max 15 palabras): ${JSON.stringify(datosTrades, null, 2)}`;
      
      const response = await fetch(GROQ_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${GROQ_API_KEY}` },
        body: JSON.stringify({ model: GROQ_MODEL, messages: [{ role: 'user', content: prompt }], temperature: 0.2 })
      });
      const result = await response.json();
      setAnalisisIA(result.choices[0].message.content);
    } catch {
      setAnalisisIA('Sistema fuera de línea o error en red cuántica...');
    }
  }

  const formatCurrency = (val) => val != null ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val).replace('$', '$ ') : '-';
  const formatCrypto = (val) => val != null ? `${Number(val).toFixed(6)}` : '-';
  const formatDate = (d) => {
    if (!d) return '-';
    return new Date(d).toLocaleString('es-MX', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };
  
  const isOnline = botStatus?.bitso_status === 'Online';
  
  const actualizarEstrategia = async (nuevaEstrategia) => {
    if (!supabase) return;
    setBotStatus(prev => ({ ...prev, estrategia_activa: nuevaEstrategia }));
    try {
      await supabase.from('bot_status').update({ estrategia_activa: nuevaEstrategia }).eq('id', 1);
    } catch (err) { console.error(err); }
  };

  const actualizarReinvertir = async (nuevoEstado) => {
    if (!supabase) return;
    setLoadingConfig(true);
    setBotStatus(prev => ({ ...prev, reinvertir_ganancias: nuevoEstado }));
    try {
      await supabase.from('bot_status').update({ reinvertir_ganancias: nuevoEstado }).eq('id', 1);
    } catch (err) { console.error(err); } finally { setLoadingConfig(false); }
  };

  const aprobarPropuesta = async (id_aprobada) => {
    if (!supabase) return;
    setLoadingConfig(true);
    try {
      await supabase.from('trade_proposals').update({ status: 'aprobada' }).eq('id', id_aprobada);
      await supabase.from('trade_proposals').update({ status: 'rechazada' }).eq('status', 'pendiente').neq('id', id_aprobada);
      playPing();
      setPropuestas([]);
    } catch (err) { console.error(err); } finally { setLoadingConfig(false); }
  };

  const [holdForm, setHoldForm] = useState({coin: 'BTC', amount: ''});
  const [presupuestoLocal, setPresupuestoLocal] = useState('');

  // Efecto para sincronizar el presupuesto local si ya viene configurado
  useEffect(() => {
     if (botStatus && botStatus.decision_usuario) {
         try {
             const dec = JSON.parse(botStatus.decision_usuario);
             const est = botStatus.estrategia_activa || 'Swing';
             const p = dec.presupuestos?.[est.toUpperCase()];
             if (p) setPresupuestoLocal(p.toString());
         } catch(e) {}
     }
  }, [botStatus?.estrategia_activa, botStatus?.decision_usuario]);

  const actualizarPresupuesto = async (nuevoMonto) => {
      setPresupuestoLocal(nuevoMonto);
      if (!nuevoMonto || isNaN(nuevoMonto)) return;
      const amount = parseFloat(nuevoMonto);
      const est = (botStatus?.estrategia_activa || 'Swing').toUpperCase();
      
      let dec = {};
      try { if (botStatus?.decision_usuario) dec = JSON.parse(botStatus.decision_usuario); } catch(e) {}
      
      dec.presupuestos = dec.presupuestos || {};
      dec.presupuestos[est] = amount;
      
      await supabase.from('bot_status').update({ decision_usuario: JSON.stringify(dec) }).eq('id', 1);
  };

  const ejecutarHoldManual = async () => {
     const amt = parseFloat(holdForm.amount);
     if (isNaN(amt) || amt <= 0) return;
     try {
         await supabase.from('trade_proposals').insert({
             simbolo: `${holdForm.coin}/MXN`,
             estrategia: 'Hold',
             status: 'orden_manual',
             proyeccion: `Inversión Manual HOLD - Monto Asignado: ${amt}`,
             probabilidad: 100,
             precio_entrada: 0.0
         });
         setHoldForm({...holdForm, amount: ''});
         playPing();
     } catch (e) {
         console.error("Error order manual Hold", e);
     }
  };

  return (
    <MainLayout isOnline={isOnline} onLogout={onLogout}>
      {showProdModal && (
        <div className="modal-overlay" style={{position: 'fixed', top:0, left:0, right:0, bottom:0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', zIndex: 9999, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
          <div className="modal-content" style={{background: '#0d0d0d', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '16px', padding: '2rem', maxWidth: '400px', width: '90%', boxShadow: '0 25px 50px -12px rgba(239, 68, 68, 0.25)'}}>
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
              <div style={{width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.3)'}}>
                <span style={{fontSize: '2rem'}}>⚠️</span>
              </div>
              <h2 style={{color: 'var(--accent-red)', fontSize: '1.25rem', marginBottom: '1rem', fontWeight: 'bold', letterSpacing: '0.05em'}}>ADVERTENCIA INSTITUCIONAL</h2>
              <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6', marginBottom: '2rem'}}>
                Estás a punto de encender el <strong style={{color: '#fff'}}>MODO PRODUCCIÓN</strong>.<br/><br/>
                El Agente IA tomará el control y comenzará a ejecutar órdenes de compra y venta <strong style={{color: '#fff'}}>REALES</strong> inyectando liquidez viva.<br/><br/>
                ¿Asumes el control y liberas al orquestador automátizado?
              </p>
              <div style={{display: 'flex', gap: '1rem', width: '100%'}}>
                <button 
                  onClick={() => setShowProdModal(false)}
                  style={{flex: 1, padding: '0.75rem', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s', letterSpacing: '0.05em'}}
                  onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                  onMouseOut={(e) => e.target.style.background = 'transparent'}
                >
                  CANCELAR
                </button>
                <button 
                  onClick={async () => {
                    await supabase.from('bot_status').update({ modo_produccion: true }).eq('id', 1);
                    setShowProdModal(false);
                    playPing();
                  }}
                  style={{flex: 1, padding: '0.75rem', background: 'var(--accent-red)', border: 'none', color: '#fff', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', transition: 'all 0.2s', letterSpacing: '0.05em', boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)'}}
                  onMouseOver={(e) => e.target.style.filter = 'brightness(1.2)'}
                  onMouseOut={(e) => e.target.style.filter = 'brightness(1)'}
                >
                  SÍ, INYECTAR
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-container">
        
        {/* Minimal Header */}
        <header className="dashboard-header">
          <div className="header-title">
            <h1>SaaK Quantum</h1>
            <span className="dev-badge">v2.0 PRE-RELEASE</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
             <span className={`status-dot ${isOnline ? 'status-online' : 'status-offline'}`}></span>
             <span className="mono-value" style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
          </div>
        </header>

        {/* BENTO GRID */}
        <main className="bento-grid">

          {/* COL 1: Portfolio */}
          <div className="bento-card col-span-4">
            <div className="card-header">
              <span><span className="icon">◈</span> Patrimonio Total AUM</span>
            </div>
            <div className="huge-value mono-value">
              {botStatus?.mxn_real_balance != null ? formatCurrency(botStatus.mxn_real_balance + openPositions.reduce((acc, pos) => acc + (pos.cantidad * pos.precio_entrada), 0)) : '---'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem', marginBottom: '1rem', fontStyle: 'italic' }}>
              Valuación estimada basada en el último precio de mercado (Actualización cada 15 min)
            </div>
            <div className="metrics-row" style={{borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem'}}>
              <div className="metric-col">
                <span className="metric-label">Liquidez MXN</span>
                <span className="large-value mono-value text-green">{formatCurrency(botStatus?.mxn_real_balance)}</span>
              </div>
              {openPositions.length > 0 ? (
                <div className="metric-col" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {openPositions.map((pos, idx) => {
                    const moneda = pos.simbolo ? pos.simbolo.split('/')[0] : 'CRIPTO';
                    return (
                      <div key={idx} style={{ display: 'flex', flexDirection: 'column' }}>
                        <span className="metric-label">Balance {moneda}</span>
                        <span className="large-value mono-value text-gold">{formatCrypto(pos.cantidad)}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="metric-col">
                  <span className="metric-label">Balance Cripto</span>
                  <span className="large-value mono-value text-gold">0.000000</span>
                </div>
              )}
            </div>
          </div>

          {/* COL 2: Command Center */}
          <div className="bento-card col-span-4">
            <div className="card-header">
              <span><span className="icon">⎈</span> Panel de Control</span>
            </div>
            <div className="command-controls">
              <div className="strategy-segmented">
                {['Hold', 'Swing', 'Scalping'].map(est => (
                  <button 
                    key={est}
                    className={`segment-btn ${botStatus?.estrategia_activa?.toUpperCase() === est.toUpperCase() ? 'active' : ''}`}
                    onClick={() => actualizarEstrategia(est)}
                  >
                    {est}
                  </button>
                ))}
              </div>
              
              {botStatus?.mxn_real_balance > 0 && (
                <div className="strategy-projections" style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                   <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Proyección Operativa (Sobre {formatCurrency(botStatus.mxn_real_balance)})
                   </div>
                   {(() => {
                      const est = botStatus?.estrategia_activa?.toUpperCase() || 'SWING';
                      const liq = botStatus.mxn_real_balance;
                      let tp = 0; let sl = 0;
                      if (est === 'SCALPING') { tp = 0.02; sl = 0.02; }
                      else if (est === 'SWING') { tp = 0.05; sl = 0.03; }
                      else { tp = 0.20; sl = 0.05; }
                      
                      return (
                         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="metric-col" style={{ alignItems: 'flex-start' }}>
                               <span className="metric-label" style={{ color: 'var(--accent-green)' }}>Meta Objetivo (+{tp*100}%)</span>
                               <span className="mono-value" style={{ color: 'var(--accent-green)', fontSize: '0.9rem' }}>+{formatCurrency(liq * tp)}</span>
                            </div>
                            <div className="metric-col" style={{ alignItems: 'flex-end' }}>
                               <span className="metric-label" style={{ color: 'var(--accent-red)' }}>Riesgo Máx (-{sl*100}%)</span>
                               <span className="mono-value" style={{ color: 'var(--accent-red)', fontSize: '0.9rem' }}>-{formatCurrency(liq * sl)}</span>
                            </div>
                         </div>
                      );
                   })()}
                </div>
              )}

              {botStatus?.estrategia_activa?.toUpperCase() === 'HOLD' ? (
                <div className="hold-manual-form" style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Inversión Directa (Hold)</div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <select value={holdForm.coin} onChange={(e) => setHoldForm({...holdForm, coin: e.target.value})} style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: '1px solid var(--border-color)' }}>
                       <option value="BTC">BTC</option>
                       <option value="ETH">ETH</option>
                       <option value="XRP">XRP</option>
                       <option value="SOL">SOL</option>
                       <option value="DOGE">DOGE</option>
                    </select>
                    <input type="number" placeholder="Monto MXN" value={holdForm.amount} onChange={(e) => setHoldForm({...holdForm, amount: e.target.value})} style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: '1px solid var(--border-color)' }} />
                  </div>
                  <button onClick={ejecutarHoldManual} style={{ width: '100%', padding: '0.5rem', background: 'var(--accent-blue)', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Comprar / Ejecutar Hold</button>
                </div>
              ) : (
                <div className="budget-form" style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Presupuesto Asignado por Trade</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{color: 'var(--text-muted)'}}>$</span>
                    <input type="number" value={presupuestoLocal} onChange={(e) => setPresupuestoLocal(e.target.value)} onBlur={(e) => actualizarPresupuesto(e.target.value)} style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: '1px solid var(--border-color)', fontSize: '1rem', fontFamily: '"JetBrains Mono", monospace' }} placeholder="Monto exacto..." />
                    <span style={{color: 'var(--text-muted)'}}>MXN</span>
                  </div>
                </div>
              )}
              
              <div className="switch-wrapper" style={{ marginTop: '0.75rem' }}>
                <div className="metric-col" style={{marginBottom: 0}}>
                  <span className="metric-label" style={{color: '#fff'}}>Modo Interés Compuesto</span>
                  <span style={{fontSize: '0.65rem', color: 'var(--text-muted)'}}>Reinvertir liquidez ganada en el siguiente cálculo</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={botStatus?.reinvertir_ganancias || false} 
                    onChange={(e) => actualizarReinvertir(e.target.checked)} 
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="switch-wrapper" style={{ marginTop: '0.75rem', borderColor: botStatus?.modo_produccion ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255,255,255,0.05)', background: botStatus?.modo_produccion ? 'rgba(239, 68, 68, 0.05)' : 'transparent' }}>
                <div className="metric-col" style={{marginBottom: 0}}>
                  <span className="metric-label" style={{color: botStatus?.modo_produccion ? 'var(--accent-red)' : '#fff', fontWeight: botStatus?.modo_produccion ? '600' : 'normal', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                    {botStatus?.modo_produccion && <span className="t-dot t-red" style={{animation: 'pulse 2s infinite'}}></span>}
                    Modo Producción (Real)
                  </span>
                  <span style={{fontSize: '0.65rem', color: 'var(--text-muted)'}}>
                    {botStatus?.modo_produccion ? '¡PELIGRO! Transacciones reales' : 'Simulación aislada (Paper Trading)'}
                  </span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={botStatus?.modo_produccion || false} 
                    onChange={async (e) => {
                      const nuevoEstado = e.target.checked;
                      if (nuevoEstado) {
                        setShowProdModal(true);
                      } else {
                        await supabase.from('bot_status').update({ modo_produccion: false }).eq('id', 1);
                      }
                    }} 
                  />
                  <span className="slider" style={botStatus?.modo_produccion ? {backgroundColor: 'var(--accent-red)'} : {}}></span>
                </label>
              </div>
            </div>
          </div>

          {/* COL 3: Radar & Signal */}
          <div className="bento-card col-span-4" style={{justifyContent: 'space-between'}}>
             <div className="card-header">
              <span><span className="icon">⌖</span> Radar de Señales</span>
            </div>
            
            <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.05)', marginBottom: '1rem', textAlign: 'center' }}>
               <span className="metric-label">Mecanismo Activo</span>
               <div className={`large-value mono-value ${botStatus?.senal?.includes('COMPRAR') ? 'text-green' : botStatus?.senal?.includes('VENDER') ? 'text-red' : 'text-gold'}`} style={{marginTop: '0.2rem'}}>
                 {botStatus?.senal || 'MONITOREANDO'}
               </div>
            </div>
            
            <div className="metrics-row" style={{marginTop: 0, justifyContent: 'space-around'}}>
               <div className="metric-col" style={{alignItems: 'center'}}>
                 <span className="metric-label">RSI 14</span>
                 <span className={`large-value mono-value ${botStatus?.rsi < 30 ? 'text-green' : botStatus?.rsi > 70 ? 'text-red' : ''}`}>
                    {botStatus?.rsi != null ? Number(botStatus.rsi).toFixed(1) : '-'}
                 </span>
               </div>
               <div className="metric-col" style={{alignItems: 'center'}}>
                 <span className="metric-label">Volatilidad ATR</span>
                 <span className="large-value mono-value">
                    {botStatus?.atr != null ? (Number(botStatus.atr)*100).toFixed(1) + '%' : '-'}
                 </span>
               </div>
            </div>
          </div>

          {/* ROW 2: Proposals & Terminal */}
          <div className="bento-card col-span-6" style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
            <div className="card-header" style={{ flexShrink: 0 }}>
              <span><span className="icon">⟁</span> Propuestas IA</span>
              <span className="dev-badge">{propuestas.length} ACTIVAS</span>
            </div>
            
            {propuestas.length > 0 ? (
              <div className="proposals-container" style={{ flex: 1, overflowY: 'auto' }}>
                {propuestas.map(p => (
                  <ProposalCard 
                    key={p.id} proposal={p} estrategiaActiva={botStatus?.estrategia_activa}
                    onApprove={aprobarPropuesta} disabled={loadingConfig}
                  />
                ))}
              </div>
            ) : (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontStyle: 'italic', fontFamily: '"JetBrains Mono", monospace' }}>
                &gt; Red pasiva. Buscando ineficiencias en el mercado...
              </div>
            )}
          </div>

          <div className="bento-card col-span-6" style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
             <div className="card-header" style={{ flexShrink: 0 }}>
              <span><span className="icon">_</span> Consola de Operaciones</span>
            </div>
            <div className="terminal-window" style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, overflow: 'hidden' }}>
               <div className="terminal-top-bar" style={{ flexShrink: 0 }}>
                 <div className="t-dot t-red"></div>
                 <div className="t-dot t-yel"></div>
                 <div className="t-dot t-grn"></div>
               </div>
               
               <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.75rem', lineHeight: '1.5' }} ref={terminalRef}>
                 {terminalLogs.map((log, idx) => {
                    const isError = log.toLowerCase().includes('error') || log.toLowerCase().includes('fatal');
                    const isWarn = log.toLowerCase().includes('alerta') || log.includes('⚠️');
                    const isSuccess = log.includes('✅') || log.includes('✔️');
                    const isCommand = log.startsWith('$') || log.startsWith('---');
                    
                    let color = '#a1a1aa';
                    if (isError) color = 'var(--accent-red)';
                    else if (isWarn) color = 'var(--accent-gold)';
                    else if (isSuccess) color = 'var(--accent-green)';
                    else if (isCommand) color = '#fff';
                    
                    return (
                      <div key={idx} style={{ color, wordBreak: 'break-all', marginBottom: '4px' }}>
                        {log}
                      </div>
                    );
                 })}
                 {terminalLogs.length === 0 && (
                   <div style={{ color: '#a1a1aa' }}>Iniciando streams...</div>
                 )}
               </div>
               
               <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)', color: 'var(--accent-green)', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.75rem', flexShrink: 0 }}>
                  <TypewriterText text={botStatus?.proyeccion_ia || '...secuencia de arranque finalizada. monitoreando.'} />
               </div>
            </div>
          </div>

          {/* ROW 3: Active Positions & Recent Trades */}
          <div className="bento-card col-span-6">
            <div className="card-header">
              <span><span className="icon">▣</span> Exposición Activa (Cartera)</span>
            </div>
            <div className="bento-table-wrapper">
              <table className="bento-table">
                <thead>
                  <tr>
                    <th>Activo Corriente</th>
                    <th>Estrategia</th>
                    <th>Precio Entrada</th>
                    <th>Volumen</th>
                  </tr>
                </thead>
                <tbody>
                  {openPositions.length > 0 ? (
                    openPositions.map(pos => (
                      <tr key={pos.id} className="animated-row">
                        <td className="mono-value" style={{fontWeight: 600}}>{pos.simbolo}</td>
                        <td><span className="dev-badge" style={{background: 'transparent'}}>{pos.estrategia}</span></td>
                        <td className="mono-value text-gold">{formatCurrency(pos.precio_entrada)}</td>
                        <td className="mono-value">{Number(pos.cantidad).toFixed(4)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="4" style={{textAlign: 'center', color: 'var(--text-muted)'}}>Ninguna posición del mercado expuesta</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bento-card col-span-6">
            <div className="card-header">
              <span><span className="icon">≡</span> Bitácora de Ejecución</span>
            </div>
            <div className="bento-table-wrapper">
              <table className="bento-table">
                <thead>
                  <tr>
                    <th>Fecha Operación</th>
                    <th>Acción</th>
                    <th>Px Operativo</th>
                    <th>Liq. Restante</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.length > 0 ? (
                    trades.map((t, i) => (
                      <tr key={t.id || i} className="animated-row">
                        <td style={{color: 'var(--text-muted)', fontSize: '0.75rem'}}>{formatDate(t.created_at)}</td>
                        <td className={t.tipo_orden?.includes('COMPRA') ? 'type-buy' : 'type-sell'}>{t.tipo_orden}</td>
                        <td className="mono-value">{formatCurrency(t.precio_btc || t.precio)}</td>
                        <td className="mono-value text-green">{formatCurrency(t.balance_mxn_resultante || t.balance_mxn)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="4" style={{textAlign: 'center', color: 'var(--text-muted)'}}>La bitácora de órdenes está vacía</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </main>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
