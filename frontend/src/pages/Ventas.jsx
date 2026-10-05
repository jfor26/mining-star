/**
 * Registro de ventas (historia de usuario HU-003) e historial.
 *
 * Criterios de aceptacion que cubre:
 *  - seleccionar un cliente existente y un producto del catalogo;
 *  - validar que la cantidad no supere el stock disponible;
 *  - confirmar precio y total antes de guardar;
 *  - al guardar, la API genera el numero de venta y descuenta el inventario.
 * La venta se envia a POST /ventas/registrar/, nunca a POST /ventas/.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { fecha, moneda } from '../utils/formato.js'
import { enteroEntre, requerido, validar } from '../utils/validaciones.js'

const VACIO = { cliente: '', producto: '', cantidad: '1' }

/** Pide a la API todo lo que la pantalla necesita. No toca el estado. */
async function obtenerDatos() {
  const [clientes, productos, ventas] = await Promise.all([
    obtenerTodos('/clientes/?ordering=nombre'),
    obtenerTodos('/productos/?ordering=nombre'),
    peticion('/ventas/?ordering=-fecha'),
  ])
  return { clientes, productos, ventas: ventas.results }
}

export default function Ventas() {
  const [clientes, setClientes] = useState([])
  const [productos, setProductos] = useState([])
  const [ventas, setVentas] = useState(null)
  const [datos, setDatos] = useState(VACIO)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const aplicar = useCallback((d) => {
    setClientes(d.clientes); setProductos(d.productos); setVentas(d.ventas)
  }, [])
  const cargar = useCallback(async () => aplicar(await obtenerDatos()), [aplicar])

  useEffect(() => {
    // "vigente" evita actualizar el estado si el usuario ya salio de la
    // pantalla antes de que llegara la respuesta.
    let vigente = true
    obtenerDatos()
      .then((d) => { if (vigente) aplicar(d) })
      .catch(() => { if (vigente) setAviso({ tipo: 'error', texto: 'No fue posible cargar los datos.' }) })
    return () => { vigente = false }
  }, [aplicar])

  const producto = useMemo(
    () => productos.find((p) => String(p.id) === datos.producto),
    [productos, datos.producto],
  )
  const total = producto ? Number(producto.precio_venta) * Number(datos.cantidad || 0) : 0

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value })

  async function registrar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, {
      cliente: [requerido],
      producto: [requerido],
      cantidad: [requerido, enteroEntre(1, producto?.stock ?? 0)],
    })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return

    try {
      const { venta } = await peticion('/ventas/registrar/', {
        metodo: 'POST',
        datos: { cliente: Number(datos.cliente), producto: Number(datos.producto), cantidad: Number(datos.cantidad) },
      })
      setAviso({ tipo: 'exito', texto: `Venta V-${String(venta.id).padStart(4, '0')} registrada por ${moneda(venta.total)}.` })
      setDatos(VACIO)
      cargar()
    } catch (error) {
      setErrores(erroresDeLaAPI(error))
      setAviso({ tipo: 'error', texto: error.message })
    }
  }

  async function anular(id) {
    if (!window.confirm('¿Anular la venta y devolver las unidades al inventario?')) return
    try {
      await peticion(`/ventas/${id}/anular/`, { metodo: 'POST' })
      setAviso({ tipo: 'exito', texto: 'Venta anulada y stock devuelto.' })
      cargar()
    } catch (error) {
      setAviso({ tipo: 'error', texto: error.message })
    }
  }

  const columnas = [
    { clave: 'id', titulo: 'N.º', celda: (v) => `V-${String(v.id).padStart(4, '0')}` },
    { clave: 'fecha', titulo: 'Fecha', celda: (v) => fecha(v.fecha) },
    { clave: 'cliente_nombre', titulo: 'Cliente' },
    { clave: 'detalle', titulo: 'Producto', celda: (v) => v.detalles.map((d) => `${d.producto_nombre} × ${d.cantidad}`).join(', ') },
    { clave: 'total', titulo: 'Total', celda: (v) => moneda(v.total) },
    { clave: 'estado', titulo: 'Estado', celda: (v) => <span className={`etiqueta ${v.estado === 'Anulada' ? 'alerta' : 'normal'}`}>{v.estado}</span> },
    {
      clave: 'acciones', titulo: '',
      celda: (v) => v.estado !== 'Anulada' && (
        <button type="button" className="boton pequeno" onClick={() => anular(v.id)}>Anular</button>
      ),
    },
  ]

  return (
    <>
      <Encabezado titulo="Ventas" descripcion="Registre ventas descontando el inventario y consulte el historial." />
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      <div className="dos-columnas">
        <section className="tarjeta">
          <h2>Nueva venta</h2>
          <form onSubmit={registrar} noValidate>
            <Campo como="select" etiqueta="Cliente" nombre="cliente" value={datos.cliente} onChange={cambiar} error={errores.cliente}>
              <option value="">Seleccione un cliente</option>
              {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre} — {c.empresa}</option>)}
            </Campo>
            <Campo como="select" etiqueta="Producto" nombre="producto" value={datos.producto} onChange={cambiar} error={errores.producto}>
              <option value="">Seleccione un producto</option>
              {productos.map((p) => (
                <option key={p.id} value={p.id} disabled={p.stock === 0}>
                  {p.nombre} ({p.stock} disponibles)
                </option>
              ))}
            </Campo>
            <Campo etiqueta="Cantidad" nombre="cantidad" type="number" min="1" max={producto?.stock}
              value={datos.cantidad} onChange={cambiar} error={errores.cantidad} />
            <dl className="resumen-venta">
              <dt>Precio unitario</dt><dd>{moneda(producto?.precio_venta)}</dd>
              <dt>Total</dt><dd><strong>{moneda(total)}</strong></dd>
            </dl>
            <button type="submit" className="boton primario">Registrar venta</button>
          </form>
        </section>
        <section className="tarjeta">
          <h2>Historial</h2>
          {ventas ? <Tabla columnas={columnas} filas={ventas} vacio="Aún no hay ventas." /> : <Cargando />}
        </section>
      </div>
    </>
  )
}
