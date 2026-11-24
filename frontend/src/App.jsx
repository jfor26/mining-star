/**
 * Rutas de la aplicacion.
 *
 * /login es publica; el resto cuelga del marco <Diseno /> y esta protegida:
 * sin sesion iniciada, RutaProtegida redirige al inicio de sesion, y
 * RequierePermiso muestra "acceso restringido" si el cargo no ve el modulo.
 */
import { Route, Routes } from 'react-router-dom'

import Diseno from './components/Diseno.jsx'
import RequierePermiso from './components/RequierePermiso.jsx'
import RutaProtegida from './components/RutaProtegida.jsx'
import Clientes from './pages/Clientes.jsx'
import Crm from './pages/Crm.jsx'
import Empleados from './pages/Empleados.jsx'
import Empresa from './pages/Empresa.jsx'
import Inventario from './pages/Inventario.jsx'
import Login from './pages/Login.jsx'
import Mejora from './pages/Mejora.jsx'
import NoEncontrada from './pages/NoEncontrada.jsx'
import Normativa from './pages/Normativa.jsx'
import Panel from './pages/Panel.jsx'
import Portal from './pages/Portal.jsx'
import Produccion from './pages/Produccion.jsx'
import Seguridad from './pages/Seguridad.jsx'
import Carrito from './pages/tienda/Carrito.jsx'
import ResultadoPago from './pages/tienda/ResultadoPago.jsx'
import Tienda from './pages/tienda/Tienda.jsx'
import Ventas from './pages/Ventas.jsx'

const conPermiso = (modulo, pagina) => <RequierePermiso modulo={modulo}>{pagina}</RequierePermiso>

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/portal" element={<RutaProtegida paraClientes><Portal /></RutaProtegida>} />
      <Route element={<RutaProtegida><Diseno /></RutaProtegida>}>
        <Route index element={conPermiso('panel', <Panel />)} />
        <Route path="empresa" element={<Empresa />} />
        <Route path="inventario" element={conPermiso('productos', <Inventario />)} />
        <Route path="clientes" element={conPermiso('clientes', <Clientes />)} />
        <Route path="crm" element={conPermiso('crm', <Crm />)} />
        <Route path="ventas" element={conPermiso('ventas', <Ventas />)} />
        <Route path="tienda" element={conPermiso('pedidos', <Tienda />)} />
        <Route path="tienda/carrito" element={conPermiso('pedidos', <Carrito />)} />
        <Route path="tienda/resultado" element={conPermiso('pedidos', <ResultadoPago />)} />
        <Route path="empleados" element={conPermiso('empleados', <Empleados />)} />
        <Route path="produccion" element={conPermiso('produccion', <Produccion />)} />
        <Route path="normativa" element={conPermiso('normativa', <Normativa />)} />
        <Route path="mejora" element={conPermiso('mejora', <Mejora />)} />
        <Route path="seguridad" element={conPermiso('seguridad', <Seguridad />)} />
        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  )
}
