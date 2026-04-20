import React from 'react';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  const { 
    isLogged, step, requestLoginCode, verifyLoginCode, logout, loading, error, isInitializing
  } = useAuth();
  
  if (isInitializing) {
    return <div className="app-wrapper" style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}><div className="orb orb-emerald"></div></div>;
  }

  return (
    <div className="app-wrapper">
      {!isLogged ? (
        <Login 
          step={step}
          requestLoginCode={requestLoginCode}
          verifyLoginCode={verifyLoginCode}
          loading={loading} 
          error={error} 
        />
      ) : (
        <Dashboard onLogout={logout} />
      )}
    </div>
  );
}

export default App;
