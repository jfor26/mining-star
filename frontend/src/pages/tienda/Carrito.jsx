/**
 * Carrito de compras y pago.
 *
 * 1. El usuario elige el cliente y revisa las cantidades.
 * 2. "Confirmar pedido" crea el pedido en el servidor (POST /pedidos/).
 * 3. "Pagar" pide la sesion de pago (POST /pedidos/{id}/pagar/):
 *    - con Stripe configurado, redirige a la pagina segura de Stripe;
 *    - en modo simulado, muestra una ventana de aprobacion de demostracion.
 */
import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { obtenerTodos, peticion } from '../../api/cliente.js'
import { Aviso, Campo, Encabezado, Estado } from '../../components/Comunes.jsx'
import { useCarrito } from '../../context/CarritoContext.jsx'
import { moneda } from '../../utils/formato.js'

export default function Carrito() {
  const { lineas, total, cambiarCantidad, quitar, vaciar } = useCarrito()
  const [clientes, setClientes] = useState([])
  const [cliente, setCliente] = useState('')
  const [modo, setModo] = useState(null)
  const [pedido, setPedido] = useState(null)
  const [parametros] = useSearchParams()
  const [aviso, setAviso] = useState(() => (parametros.get('cancelado')
    ? { tipo: 'error', texto: 'El pago fue cancelado. El pedido sigue pendiente.' } : { tipo: '', texto: '' }))
  const [ocupado, setOcupado] = useState(false)
  const navegar = useNavigate()

  useEffect(() => {
    obtenerTodos('/clientes/?ordering=nombre').then(setClientes).catch(() => {})
    peticion('/pagos/config/').then(setModo).catch(() => {})
  }, [])

  async function confirmarPedido() {
    if (!cliente) { setAviso({ tipo: 'error', texto: 'Seleccione el cliente del pedido.' }); return }
    setOcupado(true)
    try {
      const creado = await peticion('/pedidos/', {
        metodo: 'POST',
        datos: { cliente: Number(cliente), items: lineas.map((l) => ({ producto: l.producto.id, cantidad: l.cantidad })) },
      })
      setPedido(creado)
      vaciar()
      setAviso({ tipo: 'exito', texto: `Pedido P-${String(creado.id).padStart(4, '0')} creado por ${moneda(creado.total)}. Proceda al pago.` })
    } catch (error) {
      setAviso({ tipo: 'error', texto: error.message })
    } finally { setOcupado(false) }
  }

  async function pagar() {
    setOcupado(true)
    try {
      const respuesta = await peticion(`/pedidos/${pedido.id}/pagar/`, { metodo: 'POST' })
      if (respuesta.modo === 'stripe' && respuesta.url) {
        window.location.assign(respuesta.url) // pagina segura de Stripe Checkout
        return
      }
      setPedido({ ...pedido, simulando: true })
    } catch (error) {
      setAviso({ tipo: 'error', texto: error.message })
    } finally { setOcupado(false) }
  }

  async function aprobarSimulado() {
    setOcupado(true)
    try {
      await peticion(`/pedidos/${pedido.id}/confirmar-simulado/`, { metodo: 'POST' })
      navegar(`/tienda/resultado?pedido=${pedido.id}`)
    } catch (error) {
      setAviso({ tipo: 'error', texto: error.message })
      setOcupado(false)
    }
  }

  return (
    <>
      <Encabezado titulo="Carrito de compras" descripcion="Revise el pedido, elija el cliente y pague en línea.">
        <Link to="/tienda" className="boton secundario">← Seguir comprando</Link>
      </Encabezado>
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      {modo && (
        <p className="nota-pago">
          {modo.modo === 'stripe'
            ? <Estado tono="bien">Stripe activo (modo prueba)</Estado>
            : <Estado tono="aviso">Pasarela en modo simulado</Estado>}{' '}
          {modo.modo === 'stripe'
            ? 'El pago se hace en la página segura de Stripe; use la tarjeta de prueba 4242 4242 4242 4242.'
            : 'No hay llaves de Stripe en el .env: el pago se aprueba aquí mismo para la demostración.'}
        </p>
      )}

      {pedido ? (
        <section className="tarjeta resumen-pedido">
          <h2>Pedido P-{String(pedido.id).padStart(4, '0')} · {pedido.cliente_nombre}</h2>
          <ul>{pedido.items.map((i) => <li key={i.id}>{i.producto_nombre} × {i.cantidad} — {moneda(i.subtotal)}</li>)}</ul>
          <p className="total-grande">Total a pagar: {moneda(pedido.total)}</p>
          {!pedido.simulando ? (
            <button type="button" className="boton primario grande" onClick={pagar} disabled={ocupado}>
              {ocupado ? 'Conectando con la pasarela…' : modo?.modo === 'stripe' ? 'Pagar con Stripe' : 'Pagar'}
            </button>
          ) : (
            <div className="pasarela-simulada" role="dialog" aria-label="Pago simulado">
              <strong>Pasarela de demostración</strong>
              <p>Así se vería la aprobación del banco. Al aprobar, el pedido se convierte en venta y se descuenta el inventario.</p>
              <div className="acciones">
                <button type="button" className="boton exito" onClick={aprobarSimulado} disabled={ocupado}>Aprobar pago</button>
                <button type="button" className="boton secundario" onClick={() => setPedido({ ...pedido, simulando: false })}>Volver</button>
              </div>
            </div>
          )}
        </section>
      ) : lineas.length === 0 ? (
        <section className="tarjeta vacio-carrito">
          <p>El carrito está vacío.</p>
          <Link to="/tienda" className="boton primario">Ir al catálogo</Link>
        </section>
      ) : (
        <div className="dos-columnas invertido">
          <section className="tarjeta">
            <h2>Productos</h2>
            <ul className="lineas-carrito">
              {lineas.map(({ producto, cantidad }) => (
                <li key={producto.id}>
                  <div>
                    <strong>{producto.nombre}</strong>
                    <small>{moneda(producto.precio_venta)} c/u · {producto.stock} disponibles</small>
                  </div>
                  <div className="control-cantidad">
                    <button type="button" className="boton icono-solo" aria-label="Quitar una unidad"
                      onClick={() => cambiarCantidad(producto.id, cantidad - 1)}>−</button>
                    <input type="number" min="1" max={producto.stock} value={cantidad} aria-label={`Cantidad de ${producto.nombre}`}
                      onChange={(e) => cambiarCantidad(producto.id, Number(e.target.value) || 1)} />
                    <button type="button" className="boton icono-solo" aria-label="Agregar una unidad"
                      onClick={() => cambiarCantidad(producto.id, cantidad + 1)}>+</button>
                  </div>
                  <strong className="subtotal">{moneda(cantidad * Number(producto.precio_venta))}</strong>
                  <button type="button" className="boton peligro pequeno" onClick={() => quitar(producto.id)}>Quitar</button>
                </li>
              ))}
            </ul>
          </section>
          <section className="tarjeta">
            <h2>Resumen</h2>
            <Campo como="select" etiqueta="Cliente" nombre="cliente" value={cliente} onChange={(e) => setCliente(e.target.value)}>
              <option value="">Seleccione el cliente</option>
              {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </Campo>
            <dl className="resumen-venta">
              <dt>Total</dt><dd><strong>{moneda(total)}</strong></dd>
            </dl>
            <button type="button" className="boton primario grande" onClick={confirmarPedido} disabled={ocupado}>
              {ocupado ? 'Creando pedido…' : 'Confirmar pedido'}
            </button>
            <button type="button" className="boton fantasma" onClick={vaciar}>Vaciar carrito</button>
          </section>
        </div>
      )}
    </>
  )
}
