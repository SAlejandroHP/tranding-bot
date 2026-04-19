import React from 'react';

const NavIsland = ({ isOnline, onLogout }) => {
  return (
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

      <button type="button" className="nav-btn" onClick={onLogout}>
        <span className="icon" style={{fontSize: '1.2rem'}}>⎋</span> Logout
      </button>
    </div>
  );
};

export default NavIsland;
