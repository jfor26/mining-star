/** Asistente Mining Star (chatbot por reglas). */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'

import Asistente from '../components/Asistente.jsx'
import { ProveedorSesion } from '../context/SesionContext.jsx'

afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear() })

test('envía la pregunta y muestra la respuesta con su fuente', async () => {
  sessionStorage.setItem('access', 'x')
  sessionStorage.setItem('usuario', JSON.stringify({ username: 'gerente', first_name: 'Laura', rol: 'Gerente', permisos: {} }))
  const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response(
    JSON.stringify({ respuesta: 'Hay 1.092 t de caliza.', fuente: 'Producción e Inventario', sugerencias: ['¿Qué requisitos vencen pronto?'] }),
    { status: 200, headers: { 'Content-Type': 'application/json' } },
  ))
  render(<ProveedorSesion><Asistente /></ProveedorSesion>)
  await userEvent.click(screen.getByRole('button', { name: /Asistente/ }))
  expect(screen.getByText(/Hola, Laura/)).toBeInTheDocument()
  await userEvent.type(screen.getByLabelText('Escriba su pregunta'), '¿cuánta caliza hay?{enter}')
  expect(await screen.findByText('Hay 1.092 t de caliza.')).toBeInTheDocument()
  expect(screen.getByText('Fuente: Producción e Inventario')).toBeInTheDocument()
  expect(JSON.parse(espia.mock.calls[0][1].body)).toEqual({ pregunta: '¿cuánta caliza hay?' })
})
