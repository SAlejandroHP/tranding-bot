import React, { useState, useEffect } from 'react';
import { supabase } from '../services/supabaseClient';

const countryCodes = [
  { code: '+54', name: 'Argentina' },
  { code: '+591', name: 'Bolivia' },
  { code: '+55', name: 'Brasil' },
  { code: '+56', name: 'Chile' },
  { code: '+57', name: 'Colombia' },
  { code: '+506', name: 'Costa Rica' },
  { code: '+53', name: 'Cuba' },
  { code: '+593', name: 'Ecuador' },
  { code: '+503', name: 'El Salvador' },
  { code: '+34', name: 'España' },
  { code: '+1', name: 'Estados Unidos/Canadá' },
  { code: '+502', name: 'Guatemala' },
  { code: '+504', name: 'Honduras' },
  { code: '+52', name: 'México' },
  { code: '+505', name: 'Nicaragua' },
  { code: '+507', name: 'Panamá' },
  { code: '+595', name: 'Paraguay' },
  { code: '+51', name: 'Perú' },
  { code: '+1787', name: 'Puerto Rico' },
  { code: '+1809', name: 'Rep. Dominicana' },
  { code: '+598', name: 'Uruguay' },
  { code: '+58', name: 'Venezuela' }
];

const UserProfileModal = ({ onClose, onProfileUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  
  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    avatarUrl: ''
  });

  const [selectedLada, setSelectedLada] = useState('+52');
  const [phoneRaw, setPhoneRaw] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchLada, setSearchLada] = useState('');
  
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    if (!supabase) return;
    
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      setErrorMsg(`Fallo al leer sesión (API): ${error.message}`);
      return;
    }
    
    const user = session?.user;
    
    if (user) {
      setUser(user);

      let parsedLada = '+52';
      let parsedPhone = '';

      const userPhone = user.user_metadata?.phone || user.phone;

      if (userPhone) {
        // Find matching LADA (longest match first just in case)
        const match = [...countryCodes].sort((a,b) => b.code.length - a.code.length).find(c => userPhone.startsWith(c.code));
        if (match) {
           parsedLada = match.code;
           parsedPhone = userPhone.substring(match.code.length);
        } else {
           parsedPhone = userPhone; // Fallback
        }
      }
      setSelectedLada(parsedLada);
      setPhoneRaw(parsedPhone);

      setFormData({
        email: user.email || '',
        fullName: user.user_metadata?.full_name || '',
        avatarUrl: user.user_metadata?.avatar_url || ''
      });
    } else {
      setErrorMsg('No se detectó un usuario activo en el servidor.');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = async (e) => {
    try {
      setLoading(true);
      if (!e.target.files || e.target.files.length === 0) {
        throw new Error('Debes seleccionar una imagen.');
      }

      const file = e.target.files[0];
      const fileExt = file.name.split('.').pop();
      const fileName = `${Math.random()}.${fileExt}`;
      const filePath = `${fileName}`;

      if (supabase) {
        let { error: uploadError } = await supabase.storage.from('avatars').upload(filePath, file);

        if (uploadError) {
          throw uploadError;
        }

        const { data } = supabase.storage.from('avatars').getPublicUrl(filePath);
        if (data && data.publicUrl) {
           setFormData({ ...formData, avatarUrl: data.publicUrl });
           setMessage('Imagen subida correctamente.');
        }
      }
    } catch (error) {
       const file = e.target.files[0];
       const reader = new FileReader();
       reader.onloadend = () => {
         setFormData({ ...formData, avatarUrl: reader.result });
         setMessage('Imagen precargada localmente.');
       };
       reader.readAsDataURL(file);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!supabase) return;
    if (!user) {
      setErrorMsg('Error Crítico: Tu sesión caducó. Por favor recarga la página.');
      return;
    }
    
    setLoading(true);
    setMessage('');
    setErrorMsg('');

    try {
      let finalPhone = phoneRaw.trim() ? `${selectedLada}${phoneRaw.trim()}` : "";
      const userPhone = user.user_metadata?.phone || user.phone;

      const updates = {
        data: {
          full_name: formData.fullName,
          avatar_url: formData.avatarUrl,
        }
      };

      if (formData.email && formData.email !== user.email) {
        updates.email = formData.email;
      }
      
      // Guardar en metadata para NO triggerear el SMS provider de Supabase Auth
      if (finalPhone !== userPhone) {
        updates.data.phone = finalPhone;
      }

      const { data, error } = await supabase.auth.updateUser(updates);

      if (error) throw error;
      
      setMessage('¡Perfil actualizado con éxito en Supabase!');
      if (onProfileUpdate) onProfileUpdate(updates.data.avatar_url);
      
    } catch (error) {
      setErrorMsg(`Error de Supabase: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{position: 'fixed', top:0, left:0, right:0, bottom:0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', zIndex: 9999, display: 'flex', justifyContent: 'center', alignItems: 'flex-start', overflowY: 'auto', padding: '4rem 1rem'}} onClick={onClose}>
      <div className="modal-content" style={{background: '#0d0d0d', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '16px', padding: '2rem', maxWidth: '400px', width: '100%', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', margin: 'auto'}} onClick={(e) => e.stopPropagation()}>
        
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
           <h2 style={{color: '#fff', fontSize: '1.25rem', fontWeight: 'bold', margin: 0}}>Configurar Perfil</h2>
           <button onClick={onClose} style={{background: 'transparent', border:'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.5rem'}}>&times;</button>
        </div>

        {errorMsg && <div style={{background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem', border: '1px solid rgba(239, 68, 68, 0.3)'}}>{errorMsg}</div>}
        {message && <div style={{background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem', border: '1px solid rgba(16, 185, 129, 0.3)'}}>{message}</div>}

        <form onSubmit={handleUpdate} style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
               {formData.avatarUrl ? (
                 <img src={formData.avatarUrl} alt="Avatar" style={{width: '100%', height: '100%', objectFit: 'cover'}} />
               ) : (
                 <span style={{fontSize: '2rem', color: 'var(--text-muted)'}}>👤</span>
               )}
            </div>
            <label style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', cursor: 'pointer', textDecoration: 'underline' }}>
              Cambiar Foto
              <input type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} disabled={loading} />
            </label>
          </div>

          <div style={{display: 'flex', flexDirection: 'column', gap: '0.3rem'}}>
             <label style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Nombre Completo</label>
             <input type="text" name="fullName" value={formData.fullName} onChange={handleChange} style={{background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem', borderRadius: '8px', color: '#fff'}} placeholder="Tu Nombre"/>
          </div>

          <div style={{display: 'flex', flexDirection: 'column', gap: '0.3rem'}}>
             <label style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Correo Electrónico</label>
             <input type="email" name="email" value={formData.email} onChange={handleChange} style={{background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem', borderRadius: '8px', color: '#fff'}} placeholder="usuario@correo.com"/>
          </div>

          <div style={{display: 'flex', flexDirection: 'column', gap: '0.3rem'}}>
             <label style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Teléfono</label>
             <div style={{ display: 'flex', gap: '0.5rem', position: 'relative' }}>
                <div 
                   style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem', borderRadius: '8px', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', width: '90px', justifyContent: 'space-between', userSelect: 'none' }}
                   onClick={() => setShowDropdown(!showDropdown)}
                >
                  <span style={{ fontWeight: 'bold' }}>{selectedLada}</span> 
                  <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>▼</span>
                </div>
                
                {showDropdown && (
                  <div style={{ position: 'absolute', top: '100%', left: 0, marginTop: '4px', background: '#111', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '8px', width: '250px', maxHeight: '200px', overflowY: 'auto', zIndex: 10, boxShadow: '0 10px 30px rgba(0,0,0,0.8)' }}>
                     <div style={{ padding: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', position: 'sticky', top: 0, background: '#111' }}>
                       <input 
                         type="text" 
                         value={searchLada} 
                         onChange={e => setSearchLada(e.target.value)} 
                         placeholder="Buscar país o clave..."
                         style={{ width: '100%', background: 'transparent', border: 'none', color: '#fff', outline: 'none', fontSize: '0.85rem' }} 
                         autoFocus
                       />
                     </div>
                     {countryCodes.filter(c => c.name.toLowerCase().includes(searchLada.toLowerCase()) || c.code.includes(searchLada)).map(c => (
                       <div 
                         key={c.name} 
                         style={{ padding: '0.5rem 1rem', cursor: 'pointer', color: '#ccc', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between' }}
                         onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; e.currentTarget.style.color = '#fff'; }}
                         onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#ccc'; }}
                         onClick={() => { setSelectedLada(c.code); setShowDropdown(false); setSearchLada(''); }}
                       >
                         <span>{c.name}</span> <span style={{color:'var(--text-muted)'}}>{c.code}</span>
                       </div>
                     ))}
                     {countryCodes.filter(c => c.name.toLowerCase().includes(searchLada.toLowerCase()) || c.code.includes(searchLada)).length === 0 && (
                       <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                         No se encontraron países.
                       </div>
                     )}
                  </div>
                )}

                <input 
                  type="tel" 
                  value={phoneRaw} 
                  onChange={e => setPhoneRaw(e.target.value.replace(/\D/g, ''))} 
                  style={{flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem', borderRadius: '8px', color: '#fff'}} 
                  placeholder="Ej. 5512345678"
                />
             </div>
          </div>

          <button 
             type="submit" 
             disabled={loading}
             style={{marginTop: '0.5rem', padding: '0.75rem', background: '#10b981', color: '#ffffff', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.2s', filter: loading ? 'brightness(0.7)' : 'none' }}>
             {loading ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UserProfileModal;
