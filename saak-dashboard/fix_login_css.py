import sys

with open('src/App.css', 'r') as f:
    css = f.read()

# Replace .login-box
old_login_box = """
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
"""

new_login_box = """
.login-box {
  background: var(--panel-bg);
  width: 380px;
  height: 440px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 3.5rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  /* PERFECT ROUNDED HEXAGON */
  clip-path: path('M 115 0 L 265 0 Q 285 0 295 22 L 370 198 Q 380 220 370 242 L 295 418 Q 285 440 265 440 L 115 440 Q 95 440 85 418 L 10 242 Q 0 220 10 198 L 85 22 Q 95 0 115 0 Z');
}
"""
css = css.replace(old_login_box.strip(), new_login_box.strip())

# Replace .login-outer-shape
old_outer_shape = """
.login-outer-shape {
  width: 420px;
  position: relative;
  filter: drop-shadow(0 25px 40px rgba(0, 0, 0, 0.4));
  margin-top: 2rem;
}
"""
new_outer_shape = """
.login-outer-shape {
  width: 380px;
  height: 440px;
  position: relative;
  /* Drop shadow acts as our borders and deep shadow since clip-path cuts traditional borders! */
  filter: drop-shadow(0 0 1px rgba(16, 185, 129, 0.5)) drop-shadow(0 25px 40px rgba(0, 0, 0, 0.4));
  margin-top: 2rem;
}
"""
css = css.replace(old_outer_shape.strip(), new_outer_shape.strip())

# Update inputs and buttons height
old_input_group = """
.login-input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  clip-path: polygon(15px 0%, calc(100% - 15px) 0%, 100% 50%, calc(100% - 15px) 100%, 15px 100%, 0% 50%);
  padding: 0.25rem 1.25rem;
  transition: all 0.3s ease;
}
"""
new_input_group = """
.login-input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  clip-path: polygon(10px 0%, calc(100% - 10px) 0%, 100% 50%, calc(100% - 10px) 100%, 10px 100%, 0% 50%);
  padding: 0rem 1rem;
  transition: all 0.3s ease;
}
"""
css = css.replace(old_input_group.strip(), new_input_group.strip())

old_input_inner = """
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
"""
new_input_inner = """
.login-input-group input {
  flex: 1;
  background: transparent;
  border: none;
  font-family: 'Outfit', sans-serif;
  color: #333;
  font-size: 0.9rem;
  padding: 0.55rem 0;
  outline: none;
  width: 100%;
}
"""
css = css.replace(old_input_inner.strip(), new_input_inner.strip())

old_btn = """
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
"""
new_btn = """
.login-btn {
  margin-top: 0.5rem;
  background: var(--accent-green);
  border: none;
  color: #000;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.75rem 1.5rem;
  /* Use clip path for button to mimic the pointed style! */
  clip-path: polygon(15px 0%, calc(100% - 15px) 0%, 100% 50%, calc(100% - 15px) 100%, 15px 100%, 0% 50%);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
}
"""
css = css.replace(old_btn.strip(), new_btn.strip())


# Save
with open('src/App.css', 'w') as f:
    f.write(css)

print("CSS updated successfully!")
