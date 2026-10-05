/**
 * Punto de entrada del front-end de Mining Star.
 *
 * StrictMode ejecuta dos veces algunos ciclos en desarrollo para detectar
 * efectos secundarios mal escritos; no afecta la version de produccion.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import App from './App.jsx'
import { ProveedorSesion } from './context/SesionContext.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
