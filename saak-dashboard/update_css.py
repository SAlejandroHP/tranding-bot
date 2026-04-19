import sys

css_code = """
/* Login Screen */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  z-index: 10;
  width: 100%;
}

.login-outer-shape {
  width: 420px;
  position: relative;
  filter: drop-shadow(0 25px 40px rgba(0, 0, 0, 0.4));
  margin-top: 2rem;
}

.login-box {
  background: var(--panel-bg);
  /* A nice highly-rounded squircle form that mimics the custom hexagon feel but natively renders beautifully */
  border-radius: 40px; 
  border: 1px solid var(--panel-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 4rem 2.5rem 3rem 2.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.login-avatar-wrapper {
  position: absolute;
  top: -45px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 11;
  /* Use a hexagon clip-path for the avatar as requested by the image! */
  filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.3));
}

.login-avatar-hexagon {
  width: 90px;
  height: 90px;
  background: rgba(16, 185, 129, 0.2);
  border: 2px solid var(--accent-green);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-avatar-hexagon svg {
  width: 40px;
  height: 40px;
  color: var(--accent-green);
  fill: var(--accent-green);
  opacity: 0.8;
}

.login-title {
  text-align: center;
  font-size: 1.8rem;
  font-weight: 300;
  letter-spacing: 0.05em;
  color: var(--text-main);
  margin-bottom: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-input-wrapper {
  /* Creating the sharp pointed input from the picture using clip-path */
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
}

.login-input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  clip-path: polygon(15px 0%, calc(100% - 15px) 0%, 100% 50%, calc(100% - 15px) 100%, 15px 100%, 0% 50%);
  padding: 0.25rem 1.25rem;
  transition: all 0.3s ease;
}

.login-input-group:focus-within {
  background: #ffffff;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
}

.login-icon {
  padding: 0.5rem 0.5rem 0.5rem 0;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-icon svg, .login-icon-right svg {
  width: 20px;
  height: 20px;
}

.login-input-group input {
  flex: 1;
  background: transparent;
  border: none;
  font-family: 'Outfit', sans-serif;
  color: #333;
  font-size: 1rem;
  padding: 0.85rem 0;
  outline: none;
  width: 100%;
}

.login-input-group input::placeholder {
  color: #aaa;
}

.login-icon-right {
  padding: 0.5rem 0 0.5rem 0.5rem;
  color: var(--accent-green);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s;
  opacity: 0.7;
}

.login-icon-right:hover {
  opacity: 1;
}

.login-btn {
  margin-top: 0.5rem;
  background: var(--accent-green);
  border: none;
  color: #000;
  font-weight: 700;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 1.2rem;
  /* Use clip path for button to mimic the pointed style! */
  clip-path: polygon(20px 0%, calc(100% - 20px) 0%, 100% 50%, calc(100% - 20px) 100%, 20px 100%, 0% 50%);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
}

.login-btn:hover {
  background: #0ea5e9; /* Switch to blue gradient on hover like the image */
  transform: translateY(-2px);
  box-shadow: 0 15px 25px rgba(14, 165, 233, 0.4);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.remember-me input {
  accent-color: var(--text-muted);
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.forgot-password {
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: var(--text-main);
}
"""

with open('src/App.css', 'a') as f:
    f.write("\n" + css_code)
