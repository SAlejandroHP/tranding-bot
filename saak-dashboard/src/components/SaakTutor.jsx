import React, { useState } from 'react';
import { GROQ_URL, GROQ_MODEL, GROQ_API_KEY } from '../config/env';

const SaakTutor = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true); setAnswer('');
    try {
      const prompt = `System Prompt: Eres un tutor experto en trading cuantitativo para la plataforma SaaK Solutions. Responde a la duda del usuario en máximo 2 o 3 líneas, con un lenguaje muy sencillo y apto para principiantes. Duda: ${question}`;
      const response = await fetch(GROQ_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${GROQ_API_KEY}` },
        body: JSON.stringify({ model: GROQ_MODEL, messages: [{ role: 'user', content: prompt }], temperature: 0.2 })
      });
      const result = await response.json();
      setAnswer(result.choices[0].message.content);
    } catch (error) { setAnswer('Error de conexión a la red neuronal.'); } finally { setLoading(false); }
  };

  return (
    <div className={`saak-tutor-island ${isOpen ? 'open' : ''}`} onClick={() => !isOpen && setIsOpen(true)}>
      {!isOpen ? (
        <div className="saak-tutor-collapsed">
          <span style={{fontSize: '1.2rem'}}>🧠</span>
          <span>Tutor IA SaaK</span>
        </div>
      ) : (
        <div className="saak-tutor-expanded" onClick={e => e.stopPropagation()}>
          <div style={{display: 'flex', gap: '0.5rem', fontWeight: 700, color: 'var(--accent-green)'}}>🧠 Interfaz Consultiva</div>
          <form onSubmit={handleSubmit} className="tutor-form">
            <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Pregunta sobre la estrategia o el mercado..." className="tutor-input" autoFocus />
            <button type="submit" className="tutor-submit" disabled={loading || !question.trim()}>{loading ? '...' : 'CONSULTAR'}</button>
          </form>
          {answer && <div className="tutor-answer">{answer}</div>}
          <button className="tutor-close" onClick={(e) => { e.stopPropagation(); setIsOpen(false); setQuestion(''); setAnswer(''); }}>CERRAR PUNTUAL</button>
        </div>
      )}
    </div>
  );
};

export default SaakTutor;
