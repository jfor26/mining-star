/** Funciones de presentacion con el formato colombiano (es-CO). */

const pesos = new Intl.NumberFormat('es-CO', {
  style: 'currency', currency: 'COP', maximumFractionDigits: 0,
})
const numero = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 2 })

export const moneda = (valor) => pesos.format(Number(valor ?? 0))
export const cantidad = (valor) => numero.format(Number(valor ?? 0))
export const fecha = (iso) => (iso ? new Date(iso).toLocaleDateString('es-CO') : '—')

/** Fecha de hoy en formato AAAA-MM-DD segun la hora local, no la UTC. */
export function hoyISO() {
  const d = new Date()
  const dos = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`
}
