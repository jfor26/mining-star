/**
 * Carrito de compras.
 *
 * Vive en el navegador (sessionStorage) hasta que el usuario confirma el
 * pedido: solo entonces viaja al servidor, que vuelve a validar precios y
 * existencias. Nunca se confia en el precio que diga el navegador.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const CarritoContext = createContext(null)
const CLAVE = 'carrito'

function leer() {
  try { return JSON.parse(sessionStorage.getItem(CLAVE)) ?? [] } catch { return [] }
}

export function ProveedorCarrito({ children }) {
  const [lineas, setLineas] = useState(leer)

  useEffect(() => {
    try { sessionStorage.setItem(CLAVE, JSON.stringify(lineas)) } catch { /* modo privado */ }
  }, [lineas])

  const agregar = useCallback((producto, cantidad = 1) => {
    setLineas((actual) => {
      const existente = actual.find((l) => l.producto.id === producto.id)
      const tope = producto.stock
      if (existente) {
        return actual.map((l) => (l.producto.id === producto.id
          ? { ...l, cantidad: Math.min(l.cantidad + cantidad, tope) } : l))
      }
      return [...actual, { producto, cantidad: Math.min(cantidad, tope) }]
    })
  }, [])

  const cambiarCantidad = useCallback((id, cantidad) => {
    setLineas((actual) => actual
      .map((l) => (l.producto.id === id ? { ...l, cantidad: Math.max(0, Math.min(cantidad, l.producto.stock)) } : l))
      .filter((l) => l.cantidad > 0))
  }, [])

  const quitar = useCallback((id) => setLineas((a) => a.filter((l) => l.producto.id !== id)), [])
  const vaciar = useCallback(() => setLineas([]), [])

  const valor = useMemo(() => ({
    lineas,
    unidades: lineas.reduce((s, l) => s + l.cantidad, 0),
    total: lineas.reduce((s, l) => s + l.cantidad * Number(l.producto.precio_venta), 0),
    agregar, cambiarCantidad, quitar, vaciar,
  }), [lineas, agregar, cambiarCantidad, quitar, vaciar])

  return <CarritoContext.Provider value={valor}>{children}</CarritoContext.Provider>
}

// oxlint-disable-next-line react/only-export-components
export function useCarrito() {
  const contexto = useContext(CarritoContext)
  if (!contexto) throw new Error('useCarrito debe usarse dentro de <ProveedorCarrito>')
  return contexto
}
