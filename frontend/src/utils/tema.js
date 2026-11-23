/**
 * Tema de la interfaz: claro, oscuro o automatico (sigue al sistema operativo).
 * Se guarda en localStorage para recordarlo entre visitas; si el navegador no
 * lo permite, se usa "auto" sin romper la aplicacion.
 */
export const TEMAS = [
  ['claro', '☀', 'Tema claro'],
  ['oscuro', '☾', 'Tema oscuro'],
  ['auto', '◐', 'Tema automático (según el dispositivo)'],
]

export function leerTema() {
  try {
    const guardado = localStorage.getItem('tema')
    return TEMAS.some(([clave]) => clave === guardado) ? guardado : 'auto'
  } catch {
    return 'auto'
  }
}

export function aplicarTema(tema) {
  document.documentElement.dataset.tema = tema
  try { localStorage.setItem('tema', tema) } catch { /* sin almacenamiento: solo esta visita */ }
}
