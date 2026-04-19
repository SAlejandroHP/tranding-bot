import React, { useState, useEffect } from 'react';
import { GROQ_URL, GROQ_MODEL, GROQ_API_KEY } from '../config/env';

const proposalTooltipsCache = new Map();

const calcularEscenariosDinámicos = (precio, estrategia) => {
  const isScalping = (estrategia?.toUpperCase() || 'HOLD') === 'SCALPING';
  return [
    { pct: isScalping ? 0.02 : 0.05 },
    { pct: isScalping ? 0.008 : 0.02 },
    { pct: isScalping ? -0.01 : -0.03 }
  ];
};

const ProposalCard = ({ proposal, estrategiaActiva, onApprove, disabled }) => {
  const [tip, setTip] = useState(proposalTooltipsCache.get(proposal.id) || '');
  const [loadingTip, setLoadingTip] = useState(false);

  // Fetching del consejo al instante y cacheado
  useEffect(() => {
    if (!tip && !loadingTip && proposal.simbolo) {
      setLoadingTip(true);
      const fetchTip = async () => {
        try {
          const prompt = `Dame un consejo muy corto (max 10 palabras) sobre invertir en ${proposal.simbolo} con prob de ${proposal.probabilidad}%. Escribe como experto financiero cuantitativo.`;
          const response = await fetch(GROQ_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${GROQ_API_KEY}` },
            body: JSON.stringify({ model: GROQ_MODEL, messages: [{ role: 'user', content: prompt }], temperature: 0.5 })
          });
          const result = await response.json();
          const newTip = result.choices[0].message.content.trim();
          setTip(newTip);
          proposalTooltipsCache.set(proposal.id, newTip);
        } catch { setTip('Red neuronal sin conexión.'); } finally { setLoadingTip(false); }
      };
      fetchTip();
    }
  }, [tip, loadingTip, proposal.simbolo, proposal.probabilidad, proposal.id]);

  const probability = proposal.probabilidad || 0;
  let probColor = 'var(--accent-red)'; 
  if (probability > 50) probColor = 'var(--accent-gold)'; 
  if (probability >= 70) probColor = 'var(--accent-green)';
  
  const entryPrice = proposal.precio_entrada || 0;
  const formatCalcCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val).replace('$', '$ ');
  const escenarios = calcularEscenariosDinámicos(entryPrice, estrategiaActiva);

  return (
    <div className="proposal-item">
      <div className="prop-header">
        <div className="prop-asset">{proposal.simbolo}</div>
        <div className="prop-prob-circle" style={{ borderColor: probColor, color: probColor }}>{probability}%</div>
      </div>
      
      <div className="prop-proj">{proposal.proyeccion}</div>
      
      {entryPrice > 0 && (() => {
        const pOpt = escenarios[0].pct; const pRisk = Math.abs(escenarios[2].pct);
        const total = pOpt + pRisk;
        
        let baseInversion = 1000;
        const match = proposal.proyeccion?.match(/Min Sugerido: \$([\d,]+(\.\d+)?)/);
        if (match) baseInversion = parseFloat(match[1].replace(/,/g, ''));
        
        return (
          <div className="price-action-wrapper" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div className="pa-labels mono-value">
                <span className="text-red">Lim. Riesgo: {formatCalcCurrency(entryPrice * (1 - pRisk))}</span>
                <span className="text-green">Ganancia: {formatCalcCurrency(entryPrice * (1 + pOpt))}</span>
              </div>
              <div className="pa-track">
                <div className="pa-risk" style={{ width: `${(pRisk/total)*100}%` }}></div>
                <div className="pa-entry"></div>
                <div className="pa-target" style={{ width: `${(pOpt/total)*100}%` }}></div>
              </div>
              <div className="pa-midpoint mono-value">Entrada: {formatCalcCurrency(entryPrice)}</div>
            </div>

            <div className="bento-table-wrapper" style={{ marginTop: '0.5rem', background: 'rgba(0,0,0,0.4)', borderRadius: '6px' }}>
              <table className="bento-table" style={{ fontSize: '0.75rem', marginBottom: 0 }}>
                <thead>
                  <tr>
                    <th>Escenario</th>
                    <th>Var %</th>
                    <th>Px Cierre</th>
                    <th>P&L (Sobre {formatCalcCurrency(baseInversion)})</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span className="text-green" style={{fontWeight: 600}}>Optimista (TP)</span></td>
                    <td className="mono-value text-green">+{Math.round(pOpt*100)}%</td>
                    <td className="mono-value">{formatCalcCurrency(entryPrice * (1 + pOpt))}</td>
                    <td className="mono-value text-green" style={{fontWeight: 'bold'}}>+{formatCalcCurrency(baseInversion * pOpt)}</td>
                  </tr>
                  <tr>
                    <td><span className="text-red" style={{fontWeight: 600}}>Pesimista (SL)</span></td>
                    <td className="mono-value text-red">-{Math.round(pRisk*100)}%</td>
                    <td className="mono-value">{formatCalcCurrency(entryPrice * (1 - pRisk))}</td>
                    <td className="mono-value text-red" style={{fontWeight: 'bold'}}>-{formatCalcCurrency(baseInversion * pRisk)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        );
      })()}

      <button className="btn-approve" onClick={() => onApprove(proposal.id)} disabled={disabled}>
        [ EJECUTAR MANDATO ]
      </button>

      <div className="terminal-tip">
        <div className="tip-header">&gt; CONSEJO_IA</div>
        <div className="tip-text mono-value">{loadingTip ? 'procesando...' : tip}</div>
      </div>
    </div>
  );
};

export default ProposalCard;
