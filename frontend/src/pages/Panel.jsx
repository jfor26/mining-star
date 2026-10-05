/**
 * Panel principal: indicadores del negocio y alertas de inventario.
 * Consume GET /resumen/ y GET /productos/stock-bajo/.
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { peticion } from '../api/cliente.js'
import { Aviso, Cargando, Encabezado, Indicador } from '../components/Comunes.jsx'
import { cantidad, moneda } from '../utils/formato.js'

export default function Panel() {
  const [resumen, setResumen] = useState(null)
  const [alertas, setAlertas] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([peticion('/resumen/'), peticion('/productos/stock-bajo/')])
      .then(([datos, bajos]) => { setResumen(datos); setAlertas(bajos) })
      .catch(() => setError('No fue posible cargar los indicadores.'))
  }, [])

  if (error) return <Aviso tipo="error">{error}</Aviso>
  if (!resumen) return <Cargando />

  return (
    <>
      <Encabezado titulo="Panel" descripcion="Estado general de Ortega Espinosa y Compañía S.A.S." />
      <section className="rejilla-indicadores">
        <Indicador titulo="Total vendido" valor={moneda(resumen.total_vendido)} detalle={`${resumen.ventas} ventas vigentes`} tono="verde" />
        <Indicador titulo="Productos" valor={resumen.productos} detalle={`${resumen.productos_stock_bajo} en stock mínimo`} tono="naranja" />
        <Indicador titulo="Clientes" valor={resumen.clientes} />
        <Indicador titulo="Empleados" valor={resumen.empleados} tono="morado" />
      </section>

      <section className="tarjeta">
        <h2>Alertas de inventario</h2>
        {alertas.length === 0 ? (
          <p>Ningún producto está en su stock mínimo.</p>
        ) : (
          <ul className="lista-alertas">
            {alertas.map((p) => (
              <li key={p.id}>
                <strong>{p.nombre}</strong> ({p.codigo}): quedan {cantidad(p.stock)} unidades,
                mínimo {p.stock_minimo}.
              </li>
            ))}
          </ul>
        )}
        <Link to="/inventario" className="boton">Ver inventario</Link>
      </section>
    </>
  )
}
