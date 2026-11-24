/** Sitio publico: calculadora, radicacion y consulta de PQRS, contacto. */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'

import Sitio, { metrosCubicos } from '../pages/sitio/Sitio.jsx'

const respuesta = (c, s = 200) => new Response(JSON.stringify(c), { status: s, headers: { 'Content-Type': 'application/json' } })
afterEach(() => vi.restoreAllMocks())
const pintar = () => render(<MemoryRouter><Sitio /></MemoryRouter>)

test('calculadora de recebo', () => {
  expect(metrosCubicos(100, 6, 20)).toBe(120)
  expect(metrosCubicos(10, 3, 15)).toBe(4.5)
  expect(metrosCubicos(0, 3, 15)).toBe(0)
})

test('la calculadora cambia con los botones', async () => {
  pintar()
  expect(screen.getByText('≈ 120 m³')).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Más espesor' }))
  expect(screen.getByText('≈ 150 m³')).toBeInTheDocument()
})

test('radica una PQRS sin token y muestra el radicado', async () => {
  const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta({ radicado: 'PQRS-2026-0007', estado: 'Recibida' }, 201))
  pintar()
  await userEvent.click(screen.getByRole('radio', { name: 'Queja' }))
  await userEvent.type(screen.getByLabelText('Nombre completo'), 'Ana Ruiz')
  await userEvent.type(screen.getByLabelText('Documento o NIT'), '1085123456')
  await userEvent.type(screen.getByLabelText('Correo para la respuesta'), 'ana@x.co')
  await userEvent.type(screen.getByLabelText('Describa su queja'), 'El despacho llegó tarde.')
  await userEvent.click(screen.getByRole('checkbox'))
  await userEvent.click(screen.getByRole('button', { name: 'Radicar' }))
  expect(await screen.findByText('PQRS-2026-0007')).toBeInTheDocument()
  const [url, opciones] = espia.mock.calls[0]
  expect(String(url)).toContain('/publico/pqrs/')
  expect(opciones.headers.Authorization).toBeUndefined()
  expect(JSON.parse(opciones.body)).toMatchObject({ tipo: 'Queja', documento: '1085123456', autoriza_datos: true })
})

test('muestra los errores que devuelve la API', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta({ autoriza_datos: ['Debe autorizar el tratamiento de sus datos.'] }, 400))
  pintar()
  await userEvent.click(screen.getByRole('button', { name: 'Radicar' }))
  expect(await screen.findByText('Debe autorizar el tratamiento de sus datos.')).toBeInTheDocument()
})

test('consulta un radicado inexistente', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta({ detail: 'No encontrado.' }, 404))
  pintar()
  await userEvent.type(screen.getByLabelText('Radicado'), 'PQRS-2026-9999')
  await userEvent.type(screen.getByLabelText('Documento o NIT con que la radicó'), '1')
  await userEvent.click(screen.getByRole('button', { name: 'Consultar' }))
  await waitFor(() => expect(screen.getByText(/No encontramos una PQRS/)).toBeInTheDocument())
})
