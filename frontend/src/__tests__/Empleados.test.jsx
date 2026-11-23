/** Pruebas del modulo Empleados y cargos. */
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ProveedorSesion } from '../context/SesionContext.jsx'
import Empleados, { tiempoLaborado } from '../pages/Empleados.jsx'

const EMPLEADOS = [
  { id: 1, documento: '1001', nombres: 'Ana', apellidos: 'Ruiz', nombre_completo: 'Ana Ruiz', correo: 'ana@x.co',
    telefono: '3200000000', cargo: 'Auxiliar', area: 'Operaciones', estado: 'Activo', fecha_ingreso: '2020-01-15' },
  { id: 2, documento: '1002', nombres: 'Luis', apellidos: 'Guzmán', nombre_completo: 'Luis Guzmán', correo: 'luis@x.co',
    telefono: '3200000001', cargo: 'Operario', area: 'Operaciones', estado: 'Vacaciones', fecha_ingreso: '2025-06-01' },
]

function entrarComo(permisos) {
  sessionStorage.setItem('access', 'token-de-prueba')
  sessionStorage.setItem('usuario', JSON.stringify({ username: 'prueba', rol: 'Administrador', permisos }))
}

const respuesta = (cuerpo, status = 200) => new Response(
  status === 204 ? null : JSON.stringify(cuerpo), { status, headers: { 'Content-Type': 'application/json' } },
)

const pintar = () => render(<MemoryRouter><ProveedorSesion><Empleados /></ProveedorSesion></MemoryRouter>)

afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear() })

describe('tiempoLaborado', () => {
  const ref = new Date(2026, 10, 23) // 23 de noviembre de 2026
  it('expresa años y meses', () => expect(tiempoLaborado('2020-01-15', ref)).toBe('6 años y 10 meses'))
  it('usa singular', () => expect(tiempoLaborado('2025-10-01', ref)).toBe('1 año y 1 mes'))
  it('menos de un mes', () => expect(tiempoLaborado('2026-11-10', ref)).toBe('Menos de un mes'))
})

describe('Empleados', () => {
  it('lista los empleados y pide el orden y el filtro de cargo a la API', async () => {
    entrarComo({ empleados: ['ver'] })
    const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta({ results: EMPLEADOS, next: null }))
    pintar()
    expect(await screen.findByText('Ana Ruiz')).toBeInTheDocument()
    // Solo lectura: sin formulario ni botones de acciones.
    expect(screen.queryByRole('heading', { name: 'Registrar empleado' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Eliminar/ })).not.toBeInTheDocument()

    await userEvent.selectOptions(screen.getByLabelText('Ordenar empleados'), 'fecha_ingreso')
    await userEvent.click(within(screen.getByRole('group', { name: 'Filtrar por cargo' })).getByRole('button', { name: /^Auxiliar/ }))
    await waitFor(() => {
      const url = String(espia.mock.calls.at(-1)[0])
      expect(url).toContain('ordering=fecha_ingreso')
      expect(url).toContain('cargo=Auxiliar')
    })
  })

  it('valida el formulario antes de enviar', async () => {
    entrarComo({ empleados: ['ver', 'crear', 'editar', 'eliminar'] })
    const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => respuesta({ results: [], next: null }))
    pintar()
    await userEvent.click(await screen.findByRole('button', { name: 'Guardar empleado' }))
    expect(screen.getAllByText('Este campo es obligatorio.').length).toBeGreaterThan(0)
    expect(espia.mock.calls.every(([, opciones]) => (opciones?.method ?? 'GET') === 'GET')).toBe(true)
  })

  it('pide confirmación antes de eliminar y luego envía DELETE', async () => {
    entrarComo({ empleados: ['ver', 'crear', 'editar', 'eliminar'] })
    const espia = vi.spyOn(globalThis, 'fetch').mockImplementation(async (_url, opciones) => (
      opciones?.method === 'DELETE' ? respuesta(null, 204) : respuesta({ results: EMPLEADOS, next: null })
    ))
    pintar()
    await userEvent.click(await screen.findByRole('button', { name: 'Eliminar a Luis Guzmán' }))
    expect(screen.getByRole('alertdialog')).toHaveTextContent('¿Eliminar a Luis Guzmán?')
    expect(espia.mock.calls.some(([, o]) => o?.method === 'DELETE')).toBe(false)
    await userEvent.click(screen.getByRole('button', { name: 'Sí, eliminar' }))
    await waitFor(() => expect(espia.mock.calls.some(([u, o]) => o?.method === 'DELETE' && String(u).includes('/empleados/2/'))).toBe(true))
    expect(await screen.findByText('Empleado Luis Guzmán eliminado.')).toBeInTheDocument()
  })
})

it('si el empleado tiene producción asociada, explica por qué no se elimina', async () => {
  entrarComo({ empleados: ['ver', 'eliminar'] })
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (_url, opciones) => (
    opciones?.method === 'DELETE'
      ? respuesta({ mensaje: 'No se puede eliminar Luis Guzmán: tiene registros asociados en registros de producción.' }, 409)
      : respuesta({ results: EMPLEADOS, next: null })
  ))
  pintar()
  await userEvent.click(await screen.findByRole('button', { name: 'Eliminar a Luis Guzmán' }))
  await userEvent.click(screen.getByRole('button', { name: 'Sí, eliminar' }))
  expect(await screen.findByText(/tiene registros asociados.*Inactivo/)).toBeInTheDocument()
})
