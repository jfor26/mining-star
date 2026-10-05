/** Pruebas de las reglas de validacion del lado del navegador. */
import { describe, expect, it } from 'vitest'

import {
  correo, decimalEntre, enteroEntre, fechaNoFutura, longitudMaxima, requerido, soloDigitos, telefono, validar,
} from '../utils/validaciones.js'

describe('reglas de validación', () => {
  it('requerido rechaza vacío y solo espacios', () => {
    expect(requerido('')).not.toBeNull()
    expect(requerido('   ')).not.toBeNull()
    expect(requerido('Mármol')).toBeNull()
  })

  it('soloDigitos rechaza letras, puntos y caracteres especiales', () => {
    for (const valor of ['10A5', '1.085.123', '108-5', '<script>']) expect(soloDigitos(valor)).not.toBeNull()
    expect(soloDigitos('1085123456')).toBeNull()
  })

  it('correo exige formato válido', () => {
    expect(correo('no-es-correo')).not.toBeNull()
    expect(correo('a@b')).not.toBeNull()
    expect(correo('compras@andina.co')).toBeNull()
  })

  it('telefono exige entre 7 y 15 dígitos', () => {
    expect(telefono('123')).not.toBeNull()
    expect(telefono('3001234567')).toBeNull()
  })

  it('longitudMaxima respeta el límite', () => {
    expect(longitudMaxima(5)('123456')).not.toBeNull()
    expect(longitudMaxima(5)('12345')).toBeNull()
  })

  it('enteroEntre no permite vender más que el stock', () => {
    const regla = enteroEntre(1, 7)
    expect(regla('0')).not.toBeNull()
    expect(regla('8')).toMatch(/Solo hay 7/)
    expect(regla('2.5')).not.toBeNull()
    expect(regla('7')).toBeNull()
  })

  it('decimalEntre limita rango y decimales', () => {
    const regla = decimalEntre(0.01, 5000)
    expect(regla('0')).not.toBeNull()
    expect(regla('5000.01')).not.toBeNull()
    expect(regla('10.555')).not.toBeNull()
    expect(regla('treinta')).not.toBeNull()
    expect(regla('35.50')).toBeNull()
  })

  it('fechaNoFutura rechaza fechas posteriores a hoy y formatos inválidos', () => {
    expect(fechaNoFutura('2999-01-01')).not.toBeNull()
    expect(fechaNoFutura('31/12/2025')).not.toBeNull()
    expect(fechaNoFutura('2025-01-15')).toBeNull()
  })

  it('validar devuelve el primer error de cada campo', () => {
    const errores = validar({ a: '', b: 'x' }, { a: [requerido], b: [requerido] })
    expect(Object.keys(errores)).toEqual(['a'])
  })
})
