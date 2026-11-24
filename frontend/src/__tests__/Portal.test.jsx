/** Portal de clientes: compras propias y solicitud de cotizacion. */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import { ProveedorSesion } from '../context/SesionContext.jsx'
import Portal from '../pages/Portal.jsx'

const RESUMEN = {
  cliente: { nombre: 'Vías del Centro', documento: '900500001', empresa: 'Obra civil', correo: 'c@v.co' },
  compras: [{ id: 67, numero: 'V-0067', fecha: '2026-11-16', total: '264000.00', estado: 'Completada', productos: ['Rajón × 11'] }],
  solicitudes: [],
}
const CATALOGO = [{ id: 5, codigo: 'REC-001', nombre: 'Recebo para vías', categoria: 'Agregados', precio: '30000.00', disponible: true }]
const respuesta = (c, s = 200) => new Response(JSON.stringify(c), { status: s, headers: { 'Content-Type': 'application/json' } })

afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear() })

function pintar() {
  sessionStorage.setItem('access', 'x')
  sessionStorage.setItem('usuario', JSON.stringify({ username: '900500001', rol: 'Cliente', permisos: {} }))
  render(<MemoryRouter><ProveedorSesion><Portal /></ProveedorSesion></MemoryRouter>)
}

function simularAPI(alCotizar) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (url, o) => {
    const u = String(url)
    if (u.includes('/portal/cotizaciones/')) return alCotizar(JSON.parse(o.body))
    if (u.includes('/portal/catalogo/')) return respuesta(CATALOGO)
    return respuesta(RESUMEN)
  })
}

test('muestra las compras del cliente y el catálogo', async () => {
  simularAPI(() => respuesta({}, 201))
  pintar()
  expect(await screen.findByText('V-0067')).toBeInTheDocument()
  expect(screen.getByText('$ 264.000')).toBeInTheDocument()
  expect(await screen.findByRole('button', { name: 'Cotizar Recebo para vías' })).toBeInTheDocument()
})

test('no envía una cotización sin productos', async () => {
  const espia = simularAPI(() => respuesta({}, 201))
  pintar()
  await userEvent.click(await screen.findByRole('button', { name: 'Enviar solicitud' }))
  expect(screen.getByRole('alert')).toHaveTextContent('Elija al menos un producto.')
  expect(espia.mock.calls.some(([u]) => String(u).includes('/cotizaciones/'))).toBe(false)
})

test('envía la cotización con el producto elegido desde el catálogo', async () => {
  let enviado = null
  simularAPI((cuerpo) => { enviado = cuerpo; return respuesta({ id: 1, estado: 'Recibida' }, 201) })
  pintar()
  await userEvent.click(await screen.findByRole('button', { name: 'Cotizar Recebo para vías' }))
  const cantidad = screen.getByLabelText('Cantidad')
  await userEvent.clear(cantidad)
  await userEvent.type(cantidad, '15')
  expect(screen.getByText('$ 450.000')).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Enviar solicitud' }))
  await waitFor(() => expect(enviado).toEqual({ items: [{ producto: 5, cantidad: 15 }], fecha_entrega: null, observaciones: '' }))
  expect(await screen.findByText(/Solicitud enviada/)).toBeInTheDocument()
})
