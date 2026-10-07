/**
 * Tienda y brochure de productos.
 *
 * La misma pantalla sirve de catalogo para el carrito y de brochure
 * imprimible: el boton "Imprimir brochure" usa la hoja de estilos de
 * impresion (index.css, @media print), que oculta menus y botones.
 */
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { obtenerTodos, peticion } from '../../api/cliente.js'
import { Aviso, Cargando, Encabezado, Estado, Pestanas, Tabla } from '../../components/Comunes.jsx'
import { useCarrito } from '../../context/CarritoContext.jsx'
import { useSesion } from '../../context/SesionContext.jsx'
import { fecha, moneda } from '../../utils/formato.js'

// Usos de cada linea de producto, tomados del analisis de mercado del proyecto.
const USOS = {
  'Material de cantera': 'Base y sub-base de vías, rellenos y obras civiles.',
  'Caliza industrial': 'Materia prima para clínker y cemento. Caliza calcítica de bajo magnesio.',
  'Cal agrícola': 'Corrección de suelos ácidos en arroz y frutales del Tolima.',
  Marmolina: 'Pisos, pegantes, estucos y acabados.',
  Agregados: 'Concretos, prefabricados y mantenimiento vial.',
  'Mármol ornamental': 'Enchapes y acabados arquitectónicos.',
}

const TONO_PEDIDO = { Pagado: 'bien', Pendiente: 'aviso', Cancelado: 'neutro', Fallido: 'critico' }

function Catalogo() {
  const { puede } = useSesion()
  const { agregar } = useCarrito()
  const [productos, setProductos] = useState(null)
  const [categoria, setCategoria] = useState('')
  const [aviso, setAviso] = useState('')

  useEffect(() => { obtenerTodos('/productos/?ordering=categoria').then(setProductos).catch(() => setProductos([])) }, [])

  const categorias = useMemo(() => [...new Set((productos ?? []).map((p) => p.categoria))], [productos])
  const visibles = (productos ?? []).filter((p) => !categoria || p.categoria === categoria)
  if (!productos) return <Cargando />

  return (
    <>
      <div className="barra-filtros no-imprimir">
        <div className="chips" role="group" aria-label="Filtrar por categoría">
          <button type="button" className={`chip${categoria === '' ? ' activo' : ''}`} onClick={() => setCategoria('')}>Todas</button>
          {categorias.map((c) => (
            <button key={c} type="button" className={`chip${categoria === c ? ' activo' : ''}`} onClick={() => setCategoria(c)}>{c}</button>
          ))}
        </div>
        <button type="button" className="boton secundario" onClick={() => window.print()}>⎙ Imprimir brochure</button>
      </div>
      <Aviso tipo="exito" alCerrar={() => setAviso('')}>{aviso}</Aviso>

      <div className="solo-imprimir portada-brochure">
        <img src="/logo.png" alt="" width="180" />
        <h1>Portafolio de productos</h1>
        <p>Mining Star Services and Products · Ortega Espinosa y Cía. S.A.S.<br />
          Mármol, caliza y derivados desde Payandé, San Luis (Tolima). Fuente legal y trazable, cerca del punto de consumo.</p>
      </div>

      <div className="rejilla-productos">
        {visibles.map((p) => (
          <article key={p.id} className="producto">
            <div className={`franja cat-${categorias.indexOf(p.categoria) % 6}`} aria-hidden="true">
              <span>{p.codigo}</span>
            </div>
            <div className="cuerpo-producto">
              <small className="categoria">{p.categoria}</small>
              <h3>{p.nombre}</h3>
              <p>{USOS[p.categoria] ?? 'Producto minero de Mining Star.'}</p>
              <div className="pie-producto">
                <strong className="precio">{moneda(p.precio_venta)}</strong>
                {p.stock === 0
                  ? <Estado tono="critico">Agotado</Estado>
                  : p.stock_bajo ? <Estado tono="aviso">Pocas unidades</Estado> : <Estado tono="bien">Disponible</Estado>}
              </div>
              {puede('pedidos', 'crear') && (
                <button type="button" className="boton primario no-imprimir" disabled={p.stock === 0}
                  onClick={() => { agregar(p, 1); setAviso(`${p.nombre} agregado al carrito.`) }}>
                  Agregar al carrito
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
      <p className="solo-imprimir pie-brochure">Precios en pesos colombianos, sujetos a disponibilidad. Proyecto formativo SENA – ADSO.</p>
    </>
  )
}

function Pedidos() {
  const [pedidos, setPedidos] = useState(null)
  useEffect(() => { peticion('/pedidos/?ordering=-creado').then((d) => setPedidos(d.results)).catch(() => setPedidos([])) }, [])
  if (!pedidos) return <Cargando />
  return (
    <section className="tarjeta">
      <Tabla filas={pedidos} vacio="Aún no hay pedidos." columnas={[
        { clave: 'id', titulo: 'Pedido', celda: (p) => `P-${String(p.id).padStart(4, '0')}` },
        { clave: 'creado', titulo: 'Fecha', celda: (p) => fecha(p.creado) },
        { clave: 'cliente_nombre', titulo: 'Cliente' },
        { clave: 'items', titulo: 'Productos', celda: (p) => p.items.map((i) => `${i.producto_nombre} × ${i.cantidad}`).join(', ') },
        { clave: 'total', titulo: 'Total', celda: (p) => moneda(p.total) },
        { clave: 'metodo_pago', titulo: 'Pago', celda: (p) => p.metodo_pago || '—' },
        { clave: 'estado', titulo: 'Estado', celda: (p) => <Estado tono={TONO_PEDIDO[p.estado]}>{p.estado_nombre}</Estado> },
      ]} />
    </section>
  )
}

export default function Tienda() {
  const { unidades } = useCarrito()
  const { puede } = useSesion()
  const [pestana, setPestana] = useState('catalogo')
  return (
    <>
      <Encabezado titulo="Tienda y brochure" descripcion="Catálogo de productos, carrito de compras y pagos en línea.">
        {puede('pedidos', 'crear') && <Link to="/tienda/carrito" className="boton primario">🛒 Ver carrito ({unidades})</Link>}
      </Encabezado>
      <div className="no-imprimir">
        <Pestanas activa={pestana} alCambiar={setPestana}
          pestanas={[['catalogo', 'Catálogo / brochure'], ['pedidos', 'Pedidos y pagos']]} />
      </div>
      {pestana === 'catalogo' ? <Catalogo /> : <Pedidos />}
    </>
  )
}
