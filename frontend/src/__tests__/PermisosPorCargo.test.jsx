/**
 * El menu y las pantallas se adaptan al cargo del usuario.
 * (La proteccion real esta en la API; esto prueba que la interfaz no
 * ofrezca opciones que el cargo no puede usar.)
 */
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import Diseno from '../components/Diseno.jsx'
import RequierePermiso from '../components/RequierePermiso.jsx'
import { ProveedorCarrito } from '../context/CarritoContext.jsx'
import { ProveedorSesion } from '../context/SesionContext.jsx'

function entrarComo(rol, permisos) {
  sessionStorage.setItem('access', 'token-de-prueba')
  sessionStorage.setItem('usuario', JSON.stringify({ username: 'prueba', rol, permisos }))
}

function montar(ruta = '/') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <ProveedorSesion>
        <ProveedorCarrito>
          <Routes>
            <Route element={<Diseno />}>
              <Route index element={<p>inicio</p>} />
              <Route path="clientes" element={<RequierePermiso modulo="clientes"><p>listado de clientes</p></RequierePermiso>} />
            </Route>
          </Routes>
        </ProveedorCarrito>
      </ProveedorSesion>
    </MemoryRouter>,
  )
}

afterEach(() => sessionStorage.clear())

test('el operario solo ve en el menu los modulos de su cargo', () => {
  entrarComo('Operario', { panel: ['ver'], produccion: ['crear', 'ver'], mejora: ['crear', 'ver'] })
  montar()
  expect(screen.getByRole('link', { name: /Producción/ })).toBeInTheDocument()
  expect(screen.queryByRole('link', { name: /Clientes/ })).not.toBeInTheDocument()
  expect(screen.queryByRole('link', { name: /Seguridad/ })).not.toBeInTheDocument()
  expect(screen.getByText('Operario')).toBeInTheDocument()
})

test('una ruta sin permiso muestra acceso restringido en lugar del contenido', () => {
  entrarComo('Operario', { panel: ['ver'] })
  montar('/clientes')
  expect(screen.getByRole('alert')).toHaveTextContent('Acceso restringido')
  expect(screen.queryByText('listado de clientes')).not.toBeInTheDocument()
})

test('el comercial ve el carrito y los clientes', () => {
  entrarComo('Comercial', { panel: ['ver'], clientes: ['ver', 'crear'], pedidos: ['ver', 'crear'] })
  montar('/clientes')
  expect(screen.getByText('listado de clientes')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /Carrito/ })).toBeInTheDocument()
})
