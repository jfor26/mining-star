/**
 * Pantalla a la que vuelve el cliente despues de pagar.
 * Consulta el estado real del pedido en el servidor: nunca se da por pagado
 * solo porque el navegador llego a esta URL.
 */
import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { peticion } from '../../api/cliente.js'
import { Cargando, Encabezado, Estado } from '../../components/Comunes.jsx'
import { moneda } from '../../utils/formato.js'

export default function ResultadoPago() {
  const [parametros] = useSearchParams()
  const [pedido, setPedido] = useState(null)
  const [error, setError] = useState('')
  const id = parametros.get('pedido')

  useEffect(() => {
    peticion(`/pedidos/${id}/verificar/`).then(setPedido).catch(() => setError('No se encontró el pedido.'))
  }, [id])

  if (error) return <p>{error}</p>
  if (!pedido) return <Cargando texto="Verificando el pago con la pasarela…" />
  const pagado = pedido.estado === 'Pagado'
  return (
    <>
      <Encabezado titulo={pagado ? 'Pago aprobado' : 'Pago en verificación'} />
      <section className="tarjeta resultado-pago">
        <Estado tono={pagado ? 'bien' : pedido.estado === 'Fallido' ? 'critico' : 'aviso'}>{pedido.estado_nombre}</Estado>
        <h2>Pedido P-{String(pedido.id).padStart(4, '0')} · {moneda(pedido.total)}</h2>
        <p>
          {pagado
            ? `Se registró la venta V-${String(pedido.venta).padStart(4, '0')} y se descontó el inventario.`
            : 'Si ya pagó, la confirmación de Stripe puede tardar unos segundos. Recargue la página.'}
        </p>
        <div className="acciones">
          <Link to="/tienda" className="boton primario">Volver a la tienda</Link>
          <Link to="/ventas" className="boton secundario">Ver ventas</Link>
        </div>
      </section>
    </>
  )
}
