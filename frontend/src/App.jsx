/**
 * Rutas de la aplicacion.
 *
 * /login es publica; el resto cuelga del marco <Diseno /> y esta protegida:
 * sin sesion iniciada, RutaProtegida redirige al inicio de sesion.
 */
import { Route, Routes } from 'react-router-dom'

import Diseno from './components/Diseno.jsx'
import RutaProtegida from './components/RutaProtegida.jsx'
import Clientes from './pages/Clientes.jsx'
import Inventario from './pages/Inventario.jsx'
import Login from './pages/Login.jsx'
import NoEncontrada from './pages/NoEncontrada.jsx'
import Panel from './pages/Panel.jsx'
import Produccion from './pages/Produccion.jsx'
import Ventas from './pages/Ventas.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RutaProtegida><Diseno /></RutaProtegida>}>
        <Route index element={<Panel />} />
        <Route path="inventario" element={<Inventario />} />
        <Route path="clientes" element={<Clientes />} />
        <Route path="ventas" element={<Ventas />} />
        <Route path="produccion" element={<Produccion />} />
        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  )
}
