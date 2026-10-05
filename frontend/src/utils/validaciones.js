/**
 * Validaciones de formulario en el navegador.
 *
 * Replican las reglas del servidor para avisar al usuario antes de enviar,
 * pero NO las sustituyen: la API vuelve a validar todo, porque cualquier
 * programa puede llamarla sin pasar por esta interfaz.
 * Cada funcion devuelve el mensaje de error, o null si el valor es valido.
 */
import { hoyISO } from './formato.js'

export const requerido = (valor) =>
  String(valor ?? '').trim() === '' ? 'Este campo es obligatorio.' : null

export const longitudMaxima = (maximo) => (valor) =>
  String(valor ?? '').length > maximo ? `Máximo ${maximo} caracteres.` : null

export const soloDigitos = (valor) =>
  /^\d+$/.test(String(valor ?? '').trim()) ? null : 'Solo se admiten dígitos, sin puntos ni espacios.'

export const correo = (valor) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(valor ?? '').trim()) ? null : 'Correo electrónico no válido.'

export const telefono = (valor) =>
  /^\d{7,15}$/.test(String(valor ?? '').trim()) ? null : 'El teléfono debe tener entre 7 y 15 dígitos.'

export const enteroEntre = (minimo, maximo) => (valor) => {
  const n = Number(valor)
  if (!Number.isInteger(n)) return 'Debe ser un número entero.'
  if (n < minimo) return `El mínimo es ${minimo}.`
  if (n > maximo) return `Solo hay ${maximo} unidades disponibles.`
  return null
}

export const decimalEntre = (minimo, maximo, decimales = 2) => (valor) => {
  const texto = String(valor ?? '').trim()
  if (!new RegExp(`^\\d+(\\.\\d{1,${decimales}})?$`).test(texto)) {
    return `Número con máximo ${decimales} decimales, usando punto.`
  }
  const n = Number(texto)
  if (n < minimo) return `El mínimo es ${minimo}.`
  if (n > maximo) return `El máximo es ${maximo}.`
  return null
}

export const fechaNoFutura = (valor) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(valor ?? ''))) return 'Fecha no válida.'
  return valor > hoyISO() ? 'La fecha no puede ser posterior a hoy.' : null
}

/**
 * Aplica un conjunto de reglas a un objeto de datos.
 * @param {object} datos   valores del formulario
 * @param {object} reglas  { campo: [regla1, regla2, ...] }
 * @returns {object} errores por campo; vacio si todo es valido
 */
export function validar(datos, reglas) {
  const errores = {}
  for (const [campo, lista] of Object.entries(reglas)) {
    for (const regla of lista) {
      const mensaje = regla(datos[campo])
      if (mensaje) { errores[campo] = mensaje; break }
    }
  }
  return errores
}
