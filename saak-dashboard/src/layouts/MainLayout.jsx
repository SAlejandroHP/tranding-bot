import React from 'react';
import NavIsland from '../components/NavIsland';
import SaakTutor from '../components/SaakTutor';

const MainLayout = ({ children, isOnline, onLogout }) => {
  return (
    <div className="main-layout" style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative' }}>
      
      {/* Background Orbs */}
      <div className="orb orb-emerald"></div>
      <div className="orb orb-gold"></div>
      <div className="orb orb-blue"></div>

      {/* Floating Header */}
      <div style={{ zIndex: 100, position: 'relative' }}>
        <NavIsland isOnline={isOnline} onLogout={onLogout} />
      </div>

      {/* Scrollable Main Content Area */}
      {/* Añadimos paddingTop para dar espacio al NavIsland fijo */}
      <div className="layout-content-area" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', position: 'relative', zIndex: 1, paddingTop: '80px', paddingBottom: '40px' }}>
        {children}
      </div>

      {/* Floating Chat/Tutor */}
      <div style={{ zIndex: 100, position: 'relative' }}>
        <SaakTutor />
      </div>
      
    </div>
  );
};

export default MainLayout;
