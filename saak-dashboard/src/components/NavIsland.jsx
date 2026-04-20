import React, { useState, useEffect } from 'react';
import UserProfileModal from './UserProfileModal';
import { supabase } from '../services/supabaseClient';

const NavIsland = ({ isOnline, onLogout }) => {
  const [showProfile, setShowProfile] = useState(false);
  const [userAvatar, setUserAvatar] = useState(null);

  useEffect(() => {
    fetchUserAvatar();
  }, []);
  const [showSimulate, setShowSimulate] = useState(false);
  const [simAmount, setSimAmount] = useState('');

  const fetchUserAvatar = async () => {
    if (!supabase) return;
    const { data: { session } } = await supabase.auth.getSession();
    const user = session?.user;
    if (user && user.user_metadata?.avatar_url) {
      setUserAvatar(user.user_metadata.avatar_url);
    }
  };

  const handleProfileUpdated = (newAvatarUrl) => {
    if (newAvatarUrl) setUserAvatar(newAvatarUrl);
  };

  const handleSimulateInjection = async (e) => {
    e.preventDefault();
    if (!supabase) {
        alert("Sin conexión a la base de datos.");
        return;
    }
    const amount = parseFloat(simAmount);
    if (isNaN(amount) || amount <= 0) return;

    try {
      const { data, error: selectErr } = await supabase.from('bot_status').select('mxn_real_balance').eq('id', 1).single();
      if (selectErr) console.error("Error obteniendo balance:", selectErr);
      
      const currentBal = data?.mxn_real_balance || 0;
      const newBal = currentBal + amount;
      
      const { error: updateErr } = await supabase.from('bot_status').update({
         mxn_real_balance: newBal,
         proyeccion_ia: `> Nueva inyección simulada registrada: +$${amount} MXN. Despertando Junta Directiva...`
      }).eq('id', 1);
      
      if (updateErr) console.error("Error al inyectar:", updateErr);

    } catch (err) {
      console.error('Excepción inyectando capital:', err);
    } finally {
      setShowSimulate(false);
      setSimAmount('');
    }
  };

  return (
    <>
      <div className="nav-island">
        <div className="nav-item">
          <span className="icon" style={{color: '#fff'}}>◈</span> <span style={{color: '#fff', fontWeight: 800}}>SaaK OS</span>
        </div>
        
        <div className="nav-divider"></div>
        
        <div className="sync-status">
          <span className={`status-dot ${isOnline ? 'status-online' : 'status-offline'}`}></span>
          <span style={{color: isOnline ? 'var(--accent-green)' : 'var(--text-muted)'}}>
            {isOnline ? 'Bitso Sincronizado' : 'Sin Conexión Bitso'}
          </span>
        </div>

        <div className="nav-divider"></div>

        <button type="button" className="nav-btn" onClick={() => setShowSimulate(true)} style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>
          <span className="icon" style={{fontSize: '1.2rem'}}>🚀</span> Simular Inyección
        </button>

        <div className="nav-divider"></div>

        <button type="button" className="nav-btn" onClick={() => setShowProfile(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {userAvatar ? (
             <img src={userAvatar} alt="Profile" style={{ width: '20px', height: '20px', borderRadius: '50%', objectFit: 'cover' }} />
          ) : (
             <span className="icon" style={{fontSize: '1.2rem'}}>👤</span>
          )}
          Perfil
        </button>

        <div className="nav-divider"></div>

        <button type="button" className="nav-btn" onClick={onLogout}>
          <span className="icon" style={{fontSize: '1.2rem'}}>⎋</span> Logout
        </button>
      </div>

      {showSimulate && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, backdropFilter: 'blur(5px)' }}>
          <div className="modal-content" style={{ backgroundColor: 'var(--bg-bento)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '2rem', width: '90%', maxWidth: '400px', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
            <h3 style={{ color: '#fff', marginBottom: '1.5rem', textAlign: 'center' }}>Inyectar Capital (Simulación)</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', textAlign: 'center' }}>
              Agrega fondos virtuales para que la Inteligencia Artificial analice cómo distribuirlos según tu estrategia actual.
            </p>
            <form onSubmit={handleSimulateInjection}>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ color: '#fff', fontSize: '0.85rem', marginBottom: '0.5rem', display: 'block' }}>Monto a Inyectar (MXN)</label>
                <div style={{ position: 'relative' }}>
                  <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>$</span>
                  <input 
                    type="number" 
                    value={simAmount}
                    onChange={(e) => setSimAmount(e.target.value)}
                    placeholder="Ej. 5000"
                    style={{ width: '100%', padding: '0.75rem 1rem 0.75rem 2rem', borderRadius: '8px', backgroundColor: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', color: '#fff' }}
                    autoFocus
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="button" onClick={() => setShowSimulate(false)} style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', backgroundColor: 'transparent', border: '1px solid var(--border-color)', color: '#fff', cursor: 'pointer' }}>
                  Cancelar
                </button>
                <button type="submit" style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', backgroundColor: '#3b82f6', border: 'none', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
                  Inyectar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showProfile && (
        <UserProfileModal 
          onClose={() => setShowProfile(false)} 
          onProfileUpdate={handleProfileUpdated} 
        />
      )}
    </>
  );
};

export default NavIsland;
