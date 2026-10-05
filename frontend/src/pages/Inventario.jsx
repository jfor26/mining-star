/**
 * Consulta de stock de productos terminados (historia de usuario HU-002).
 *
 * Criterios de aceptacion que cubre:
 *  - lista con nombre, codigo y cantidad disponible;
 *  - campo de busqueda por nombre;
 *  - las cantidades se actualizan solas: se vuelven a pedir cada 30 segundos,
 *    de modo que una venta registrada en otro equipo se refleja sin recargar.
 */
import { useCallback, useEffect, useState } from 'react'

import { peticion } from '../api/cliente.js'
import { Aviso, Cargando, Encabezado, Tabla } from '../components/Comunes.jsx'
import { moneda } from '../utils/formato.js'

const INTERVALO_MS = 30_000

export default function Inventario() {
  const [busqueda, setBusqueda] = useState('')
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')
  const [actualizado, setActualizado] = useState(null)

  const cargar = useCallback(async (texto) => {
    try {
      const ruta = `/productos/?ordering=nombre${texto ? `&search=${encodeURIComponent(texto)}` : ''}`
      setDatos(await peticion(ruta))
      setActualizado(new Date())
      setError('')
    } catch {
      setError('No fue posible consultar el inventario.')
    }
  }, [])

  // Espera 300 ms despues de la ultima tecla para no consultar la API
  // con cada letra que se escribe.
  useEffect(() => {
    const espera = setTimeout(() => cargar(busqueda.trim()), 300)
    return () => clearTimeout(espera)
  }, [busqueda, cargar])

  useEffect(() => {
    const reloj = setInterval(() => cargar(busqueda.trim()), INTERVALO_MS)
    return () => clearInterval(reloj)
  }, [busqueda, cargar])

  const columnas = [
    { clave: 'codigo', titulo: 'Código' },
    { clave: 'nombre', titulo: 'Producto' },
    { clave: 'categoria', titulo: 'Categoría' },
    { clave: 'proveedor_nombre', titulo: 'Proveedor' },
    { clave: 'precio_venta', titulo: 'Precio de venta', celda: (p) => moneda(p.precio_venta) },
    {
      clave: 'stock', titulo: 'Disponible',
      celda: (p) => (
        <span className={`etiqueta ${p.stock_bajo ? 'alerta' : 'normal'}`}>
          {p.stock} {p.stock_bajo ? '· stock mínimo' : ''}
        </span>
      ),
    },
  ]

  return (
    <>
      <Encabezado titulo="Inventario" descripcion="Stock disponible de productos terminados en tiempo real." />
      <section className="tarjeta">
        <div className="barra-filtros">
          <input
            type="search"
            placeholder="Buscar por nombre, código o categoría…"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar productos"
            maxLength={100}
          />
          {actualizado && (
            <small>Actualizado a las {actualizado.toLocaleTimeString('es-CO')}</small>
          )}
        </div>
        <Aviso tipo="error">{error}</Aviso>
        {datos ? (
          <>
            <Tabla columnas={columnas} filas={datos.results} vacio="Ningún producto coincide con la búsqueda." />
            <p className="pie-tabla">{datos.count} producto{datos.count === 1 ? '' : 's'}</p>
          </>
        ) : <Cargando />}
      </section>
    </>
  )
}
