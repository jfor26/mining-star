/** Campana de notificaciones. */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import Campana from '../components/Campana.jsx'

const AVISOS = {
  sin_leer: 2,
  resultados: [
    { clave: 'norma:1', tipo: 'normativa', titulo: 'Requisito vencido', texto: 'Regalías venció hace 3 días.', ruta: '/normativa', leida: false },
    { clave: 'stock:1:2', tipo: 'inventario', titulo: 'Stock mínimo', texto: 'Recebo: quedan 2.', ruta: '/inventario', leida: false },
  ],
}
const respuesta = (c, s = 200) => new Response(s === 204 ? null : JSON.stringify(c), { status: s, headers: { 'Content-Type': 'application/json' } })

afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear() })

function pintar() {
  sessionStorage.setItem('access', 'x')
  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<Campana />} />
        <Route path="/normativa" element={<p>pantalla normativa</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

test('muestra el contador y la lista de avisos', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta(AVISOS))
  pintar()
  const boton = await screen.findByRole('button', { name: 'Notificaciones: 2 sin leer' })
  await userEvent.click(boton)
  expect(screen.getByRole('dialog', { name: 'Notificaciones' })).toHaveTextContent('Regalías venció hace 3 días.')
  await userEvent.click(screen.getByRole('button', { name: 'Inventario' }))
  expect(screen.queryByText('Regalías venció hace 3 días.')).not.toBeInTheDocument()
})

test('al abrir un aviso lo marca como leído y lleva a su módulo', async () => {
  const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async (_u, o) => (o?.method === 'POST' ? respuesta(null, 204) : respuesta(AVISOS)))
  pintar()
  await userEvent.click(await screen.findByRole('button', { name: /2 sin leer/ }))
  await userEvent.click(screen.getByRole('button', { name: /Requisito vencido/ }))
  expect(await screen.findByText('pantalla normativa')).toBeInTheDocument()
  await waitFor(() => expect(espia.mock.calls.some(([, o]) => o?.method === 'POST' && o.body.includes('norma:1'))).toBe(true))
})
