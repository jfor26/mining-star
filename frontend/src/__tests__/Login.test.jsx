/** Pruebas de la pantalla de inicio de sesion. */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ProveedorSesion } from '../context/SesionContext.jsx'
import Login from '../pages/Login.jsx'

const pintar = () => render(
  <MemoryRouter><ProveedorSesion><Login /></ProveedorSesion></MemoryRouter>,
)

afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear() })

describe('Login', () => {
  it('no envía la petición si faltan datos', async () => {
    const espia = vi.spyOn(globalThis, 'fetch')
    pintar()
    await userEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }))
    expect(screen.getAllByText('Este campo es obligatorio.')).toHaveLength(2)
    expect(espia).not.toHaveBeenCalled()
  })

  it('muestra el mensaje de error de autenticación que devuelve la API', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(
      JSON.stringify({ autenticado: false, mensaje: 'Error en la autenticacion: usuario o contrasena incorrectos.' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } },
    ))
    pintar()
    await userEvent.type(screen.getByLabelText('Usuario'), 'juan.ortega')
    await userEvent.type(screen.getByLabelText('Contraseña'), 'equivocada')
    await userEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }))
    expect(await screen.findByRole('alert')).toHaveTextContent('usuario o contrasena incorrectos')
  })
})
