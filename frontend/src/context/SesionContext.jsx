/**
 * Estado de la sesion compartido por toda la aplicacion.
 *
 * Un contexto evita pasar el usuario por props de componente en componente:
 * cualquier pantalla lo obtiene con useSesion().
 *
 * puede(modulo, operacion) consulta la matriz de permisos del cargo que
 * envia el servidor al iniciar sesion. Sirve para OCULTAR menus y botones;
 * la proteccion real esta en la API, que responde 403 de todas formas.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { cuandoExpireLaSesion, sesion } from '../api/cliente.js'

const SesionContext = createContext(null)

export function ProveedorSesion({ children }) {
  const [usuario, setUsuario] = useState(() => sesion.usuarioGuardado())

  const iniciarSesion = useCallback(async (nombre, clave) => {
    const datos = await sesion.iniciar(nombre, clave)
    setUsuario(datos.usuario)
    return datos
  }, [])

  const cerrarSesion = useCallback(async () => {
    await sesion.cerrar()
    setUsuario(null)
  }, [])

  const puede = useCallback(
    (modulo, operacion = 'ver') => Boolean(usuario?.permisos?.[modulo]?.includes(operacion)),
    [usuario],
  )

  // Si el token de refresco tambien vencio, el cliente HTTP avisa y aqui se
  // cierra la sesion; la ruta protegida redirige entonces al inicio de sesion.
  useEffect(() => { cuandoExpireLaSesion(() => setUsuario(null)) }, [])

  const valor = useMemo(
    () => ({ usuario, iniciarSesion, cerrarSesion, puede }),
    [usuario, iniciarSesion, cerrarSesion, puede],
  )
  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
}

// oxlint-disable-next-line react/only-export-components
export function useSesion() {
  const contexto = useContext(SesionContext)
  if (!contexto) throw new Error('useSesion debe usarse dentro de <ProveedorSesion>')
  return contexto
}
