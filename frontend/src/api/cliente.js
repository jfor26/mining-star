/**
 * Cliente HTTP de la API REST de Mining Star.
 *
 * Centraliza tres responsabilidades para que ningun componente tenga que
 * repetirlas: agregar el token JWT a cada peticion, renovarlo cuando vence
 * y convertir las respuestas de error en una excepcion con los mensajes de
 * validacion del servidor.
 */

const BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

// Se usa sessionStorage y no localStorage: el token se borra al cerrar la
// pestana, lo que reduce el riesgo si alguien usa el mismo equipo despues.
const almacen = {
  leer: (clave) => sessionStorage.getItem(clave),
  guardar: (clave, valor) => sessionStorage.setItem(clave, valor),
  borrar: () => {
    sessionStorage.removeItem('access')
    sessionStorage.removeItem('refresh')
    sessionStorage.removeItem('usuario')
  },
}

/** Error de la API con el codigo HTTP y el cuerpo de la respuesta. */
export class ErrorAPI extends Error {
  constructor(estado, datos) {
    super(datos?.mensaje ?? datos?.detail ?? `Error ${estado}`)
    this.estado = estado
    this.datos = datos ?? {}
  }

  /** Errores por campo, tanto si vienen en "errores" como en la raiz. */
  get errores() {
    return this.datos.errores ?? this.datos
  }
}

// Quien quiera enterarse de que la sesion expiro se suscribe aqui.
let alExpirar = () => {}
export const cuandoExpireLaSesion = (funcion) => { alExpirar = funcion }

async function renovarToken() {
  const refresh = almacen.leer('refresh')
  if (!refresh) return false
  const respuesta = await fetch(`${BASE}/auth/refrescar/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!respuesta.ok) return false
  // El servidor rota el token de refresco: cada renovacion entrega uno
  // nuevo y el anterior queda invalidado en la lista negra.
  const { access, refresh: nuevoRefresh } = await respuesta.json()
  almacen.guardar('access', access)
  if (nuevoRefresh) almacen.guardar('refresh', nuevoRefresh)
  return true
}

/**
 * Hace una peticion a la API.
 * @param {string} ruta   ruta relativa, por ejemplo "/clientes/"
 * @param {object} opciones metodo, datos (cuerpo JSON) y si lleva token
 */
export async function peticion(ruta, { metodo = 'GET', datos, conToken = true, reintento = true } = {}) {
  const cabeceras = { 'Content-Type': 'application/json' }
  const token = almacen.leer('access')
  if (conToken && token) cabeceras.Authorization = `Bearer ${token}`

  const respuesta = await fetch(`${BASE}${ruta}`, {
    method: metodo,
    headers: cabeceras,
    body: datos === undefined ? undefined : JSON.stringify(datos),
  })

  // El token de acceso dura dos horas. Si vencio, se renueva una vez con el
  // de refresco y se repite la peticion sin que el usuario lo note.
  if (respuesta.status === 401 && conToken && reintento) {
    if (await renovarToken()) {
      return peticion(ruta, { metodo, datos, conToken, reintento: false })
    }
    almacen.borrar()
    alExpirar()
  }

  if (respuesta.status === 204) return null
  const cuerpo = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) throw new ErrorAPI(respuesta.status, cuerpo)
  return cuerpo
}

/** Recorre todas las paginas de un listado paginado y devuelve los resultados. */
export async function obtenerTodos(ruta) {
  const resultados = []
  let pagina = 1
  for (;;) {
    const separador = ruta.includes('?') ? '&' : '?'
    const datos = await peticion(`${ruta}${separador}page=${pagina}`)
    resultados.push(...datos.results)
    if (!datos.next) return resultados
    pagina += 1
  }
}

export const sesion = {
  async iniciar(username, password) {
    const datos = await peticion('/auth/login/', {
      metodo: 'POST', datos: { username, password }, conToken: false,
    })
    almacen.guardar('access', datos.access)
    almacen.guardar('refresh', datos.refresh)
    almacen.guardar('usuario', JSON.stringify(datos.usuario))
    return datos
  },
  /** Avisa al servidor para que invalide el token de refresco y borra todo. */
  async cerrar() {
    const refresh = almacen.leer('refresh')
    try {
      if (refresh) await peticion('/auth/logout/', { metodo: 'POST', datos: { refresh }, reintento: false })
    } catch { /* aunque falle la red, la sesion local se cierra igual */ }
    almacen.borrar()
  },
  /** Momento en que vence el token de acceso actual (lo lleva dentro, en "exp"). */
  venceElToken() {
    const token = almacen.leer('access')
    if (!token) return null
    try {
      const carga = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
      return new Date(carga.exp * 1000)
    } catch { return null }
  },
  usuarioGuardado() {
    const texto = almacen.leer('usuario')
    return texto && almacen.leer('access') ? JSON.parse(texto) : null
  },
}
