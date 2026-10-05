/** Pruebas del componente generico de tabla. */
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Tabla } from '../components/Comunes.jsx'

describe('Tabla', () => {
  const columnas = [{ clave: 'nombre', titulo: 'Nombre' }, { clave: 'stock', titulo: 'Stock', celda: (f) => `${f.stock} u` }]

  it('pinta encabezados y filas, aplicando las celdas personalizadas', () => {
    render(<Tabla columnas={columnas} filas={[{ id: 1, nombre: 'Mármol blanco', stock: 7 }]} />)
    expect(screen.getByRole('columnheader', { name: 'Nombre' })).toBeInTheDocument()
    expect(screen.getByText('Mármol blanco')).toBeInTheDocument()
    expect(screen.getByText('7 u')).toBeInTheDocument()
  })

  it('muestra el mensaje de vacío cuando no hay filas', () => {
    render(<Tabla columnas={columnas} filas={[]} vacio="Sin productos." />)
    expect(screen.getByText('Sin productos.')).toBeInTheDocument()
  })
})
