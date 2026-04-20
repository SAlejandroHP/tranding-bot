import React, { useState } from 'react';

const Login = ({ step, requestLoginCode, verifyLoginCode, loading, error }) => {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (step === 1) {
      requestLoginCode(email);
    } else {
      verifyLoginCode(email, code);
    }
  };

  return (
    <div className="login-container">
      <div className="login-outer-wrapper">
        <div className="login-avatar-wrapper">
          <div className="login-avatar-hexagon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
        
        <div className="login-box-shape">
          <h2 className="login-title">Iniciar Sesión</h2>
          
          <form className="login-form" onSubmit={handleSubmit}>
            {error && (
              <div style={{ color: 'var(--accent-red)', marginBottom: '1rem', fontSize: '0.85rem', textAlign: 'center' }}>
                {error}
              </div>
            )}
            
            {step === 1 ? (
              <div className="login-input-group">
                <span className="login-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
                  </svg>
                </span>
                <input 
                  type="email" 
                  placeholder="Email de usuario" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                />
              </div>
            ) : (
              <div className="login-input-group">
                <span className="login-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </span>
                <input 
                  type="text" 
                  placeholder="Código de seguridad" 
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  required 
                  autoComplete="one-time-code"
                  style={{ letterSpacing: '4px', textAlign: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}
                />
              </div>
            )}
            
            <button type="submit" className="login-btn" disabled={loading}>
              {loading ? 'CARGANDO...' : (step === 1 ? 'ENVIAR CÓDIGO' : 'VERIFICAR')}
            </button>
            
            {step === 2 && (
              <div className="login-options" style={{justifyContent: 'center', marginTop: '1rem'}}>
                 <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Revisa tu buzón de correo para ingresar el código</span>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
