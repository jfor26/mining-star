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
import { ProveedorCarrito } from './context/CarritoContext.jsx'
import { ProveedorSesion } from './context/SesionContext.jsx'
import './index.css'
import { aplicarTema, leerTema } from './utils/tema.js'

// El tema se aplica antes de pintar para que no parpadee al cargar.
aplicarTema(leerTema())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <ProveedorCarrito>
          <App />
        </ProveedorCarrito>
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
