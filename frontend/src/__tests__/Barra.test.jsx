/** Boton Volver y selector de tema de la barra superior. */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, expect, test } from 'vitest'

import { BotonVolver, SelectorTema } from '../components/Barra.jsx'

afterEach(() => { localStorage.clear(); delete document.documentElement.dataset.tema })

test('Volver no aparece en el inicio', () => {
  render(<MemoryRouter initialEntries={['/']}><BotonVolver /></MemoryRouter>)
  expect(screen.queryByRole('button', { name: /Volver/ })).not.toBeInTheDocument()
})

test('Volver sin pantalla anterior lleva al inicio', async () => {
  render(
    <MemoryRouter initialEntries={['/clientes']}>
      <Routes>
        <Route path="/" element={<p>inicio</p>} />
        <Route path="/clientes" element={<BotonVolver />} />
      </Routes>
    </MemoryRouter>,
  )
  await userEvent.click(screen.getByRole('button', { name: /Volver/ }))
  expect(screen.getByText('inicio')).toBeInTheDocument()
})

test('el selector aplica y recuerda el tema', async () => {
  render(<SelectorTema />)
  expect(screen.getByRole('radio', { name: /automático/ })).toHaveAttribute('aria-checked', 'true')
  await userEvent.click(screen.getByRole('radio', { name: 'Tema oscuro' }))
  expect(document.documentElement.dataset.tema).toBe('oscuro')
  expect(localStorage.getItem('tema')).toBe('oscuro')
})
