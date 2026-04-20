import React, { useState, useEffect } from 'react';
import UserProfileModal from './UserProfileModal';
import { supabase } from '../services/supabaseClient';

const NavIsland = ({ isOnline, onLogout }) => {
  const [showProfile, setShowProfile] = useState(false);
  const [userAvatar, setUserAvatar] = useState(null);

  useEffect(() => {
    fetchUserAvatar();
  }, []);

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
