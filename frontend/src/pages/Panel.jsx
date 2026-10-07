/**
 * Dashboard: indicadores y graficas del negocio.
 * Consume GET /dashboard/ (series agregadas) y GET /productos/stock-bajo/.
 *
 * El servidor solo envia los bloques que el cargo puede ver, asi que cada
 * grafica se pinta unicamente si su serie llego en la respuesta.
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'

import { peticion } from '../api/cliente.js'
import { Aviso, Cargando, Encabezado, Estado, Indicador } from '../components/Comunes.jsx'
import { Globo, TarjetaGrafica } from '../components/Graficas.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { cantidad, fecha, moneda } from '../utils/formato.js'
import { EJE, ESTADOS, SERIES } from '../utils/paleta.js'

const millones = (v) => `$${(v / 1_000_000).toLocaleString('es-CO', { maximumFractionDigits: 1 })} M`
const TONO_NORMATIVA = { Cumplido: 'bien', EnTramite: 'aviso', Pendiente: 'serio', Vencido: 'critico' }
const COLOR_TONO = { bien: ESTADOS.bien, aviso: ESTADOS.aviso, serio: ESTADOS.serio, critico: ESTADOS.critico }

export default function Panel() {
  const { usuario, puede } = useSesion()
  const [datos, setDatos] = useState(null)
  const [alertas, setAlertas] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    peticion('/dashboard/').then(setDatos).catch(() => setError('No fue posible cargar el dashboard.'))
    if (puede('productos')) peticion('/productos/stock-bajo/').then(setAlertas).catch(() => {})
  }, [puede])

  if (error) return <Aviso tipo="error">{error}</Aviso>
  if (!datos) return <Cargando />
  const ind = datos.indicadores

  return (
    <>
      <Encabezado
        titulo={`Hola, ${usuario?.first_name || usuario?.username}`}
        descripcion={`Dashboard de Mining Star · vista del cargo ${usuario?.rol}. Solo ve la información de los módulos que su cargo tiene asignados.`}
      />

      <section className="rejilla-indicadores">
        {ind.total_vendido !== undefined && (
          <Indicador titulo="Total vendido" valor={moneda(ind.total_vendido)} detalle={`${ind.ventas} ventas vigentes`} tono="verde" />
        )}
        {ind.toneladas_mes !== undefined && (
          <Indicador titulo="Producción del mes" valor={`${cantidad(ind.toneladas_mes)} t`} detalle="Toneladas extraídas" />
        )}
        {ind.valor_embudo !== undefined && (
          <Indicador titulo="Embudo comercial" valor={millones(ind.valor_embudo)} detalle={`${ind.oportunidades_abiertas} oportunidades abiertas`} tono="morado" />
        )}
        {ind.cumplimiento_normativo !== undefined && (
          <Indicador titulo="Cumplimiento normativo" valor={`${ind.cumplimiento_normativo} %`} detalle="Requisitos cumplidos" tono="naranja" />
        )}
        {ind.productos !== undefined && (
          <Indicador titulo="Productos" valor={ind.productos} detalle={`${ind.stock_bajo} en stock mínimo`} tono="naranja" />
        )}
        {ind.clientes !== undefined && <Indicador titulo="Clientes" valor={ind.clientes} />}
        {ind.empleados !== undefined && <Indicador titulo="Empleados activos" valor={ind.empleados} tono="morado" />}
      </section>

      <div className="rejilla-graficas">
        {datos.ventas_por_mes && (
          <TarjetaGrafica ancho={2} titulo="Ventas por mes" descripcion="Valor vendido en los últimos seis meses, sin ventas anuladas. El mes actual va corrido."
            filas={datos.ventas_por_mes} columnas={[['mes', 'Mes'], ['ventas', 'N.º ventas'], ['total', 'Total', moneda]]}>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={datos.ventas_por_mes} margin={{ top: 10, right: 16, left: 8, bottom: 0 }}>
                <defs>
                  <linearGradient id="relleno-ventas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={SERIES[0]} stopOpacity={0.25} />
                    <stop offset="100%" stopColor={SERIES[0]} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="mes" {...EJE} />
                <YAxis tickFormatter={millones} {...EJE} width={70} />
                <Tooltip content={<Globo formato={moneda} />} />
                <Area type="linear" dataKey="total" name="Ventas" stroke={SERIES[0]} strokeWidth={2}
                  fill="url(#relleno-ventas)" activeDot={{ r: 5 }} />
              </AreaChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.top_productos && (
          <TarjetaGrafica titulo="Productos más vendidos" descripcion="Ingresos por producto."
            filas={datos.top_productos} columnas={[['producto', 'Producto'], ['unidades', 'Unidades'], ['ingresos', 'Ingresos', moneda]]}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={datos.top_productos} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" tickFormatter={millones} {...EJE} />
                <YAxis type="category" dataKey="producto" width={150} {...EJE}
                  tickFormatter={(t) => (t.length > 22 ? `${t.slice(0, 21)}…` : t)} />
                <Tooltip content={<Globo formato={moneda} />} cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="ingresos" name="Ingresos" fill={SERIES[0]} radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.produccion_diaria && (
          <TarjetaGrafica ancho={2} titulo="Producción diaria por material" descripcion="Toneladas extraídas en los últimos 14 días (HU-001)."
            filas={datos.produccion_diaria} columnas={[['dia', 'Día'], ['Caliza', 'Caliza (t)'], ['Marmol', 'Mármol (t)'], ['Recebo', 'Recebo (t)']]}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={datos.produccion_diaria} margin={{ top: 10, right: 16, left: 0 }}>
                <CartesianGrid vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="dia" {...EJE} />
                <YAxis {...EJE} unit=" t" width={56} />
                <Tooltip content={<Globo formato={(v) => `${cantidad(v)} t`} />} cursor={{ fill: '#f1f5f9' }} />
                <Legend iconType="circle" />
                <Bar dataKey="Caliza" stackId="p" fill={SERIES[0]} stroke="#fff" strokeWidth={2} />
                <Bar dataKey="Marmol" name="Mármol" stackId="p" fill={SERIES[1]} stroke="#fff" strokeWidth={2} />
                <Bar dataKey="Recebo" stackId="p" fill={SERIES[2]} stroke="#fff" strokeWidth={2} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.embudo_crm && (
          <TarjetaGrafica titulo="Embudo comercial (CRM)" descripcion="Oportunidades por etapa."
            filas={datos.embudo_crm} columnas={[['etapa', 'Etapa'], ['cantidad', 'Cantidad'], ['valor', 'Valor', moneda]]}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={datos.embudo_crm} layout="vertical" margin={{ left: 8, right: 24 }}>
                <XAxis type="number" allowDecimals={false} {...EJE} />
                <YAxis type="category" dataKey="etapa" width={130} {...EJE} />
                <Tooltip content={<Globo />} cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="cantidad" name="Oportunidades" fill={SERIES[0]} radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.inventario_por_categoria && (
          <TarjetaGrafica titulo="Inventario valorizado por categoría" descripcion="Existencias × precio de venta."
            filas={datos.inventario_por_categoria} columnas={[['categoria', 'Categoría'], ['unidades', 'Unidades'], ['valor', 'Valor', moneda]]}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={datos.inventario_por_categoria} layout="vertical" margin={{ left: 8, right: 16 }}>
                <XAxis type="number" tickFormatter={millones} {...EJE} />
                <YAxis type="category" dataKey="categoria" width={130} {...EJE} />
                <Tooltip content={<Globo formato={moneda} />} cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="valor" name="Valor" fill={SERIES[0]} radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.normativa_por_estado && (
          <TarjetaGrafica titulo="Requisitos legales por estado" descripcion="Autoridad minera, ambiental y demás entidades."
            filas={datos.normativa_por_estado} columnas={[['nombre', 'Estado'], ['cantidad', 'Requisitos']]}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={datos.normativa_por_estado} margin={{ top: 10, right: 16 }}>
                <XAxis dataKey="nombre" {...EJE} />
                <YAxis allowDecimals={false} {...EJE} width={30} />
                <Tooltip content={<Globo />} cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="cantidad" name="Requisitos" radius={[4, 4, 0, 0]} barSize={36}
                  label={{ position: 'top', fill: '#334155', fontSize: 12 }}>
                  {datos.normativa_por_estado.map((f) => <Cell key={f.clave} fill={COLOR_TONO[TONO_NORMATIVA[f.clave]]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {datos.proximos_vencimientos?.length > 0 && (
              <ul className="lista-vencimientos">
                {datos.proximos_vencimientos.map((r) => (
                  <li key={r.id}>
                    <Estado tono={r.alerta === 'vencido' ? 'critico' : r.alerta === 'proximo' ? 'aviso' : 'neutro'}>
                      {r.dias < 0 ? `Vencido hace ${-r.dias} d` : `${r.dias} d`}
                    </Estado>
                    <span>{r.nombre} <small>({r.autoridad} · {fecha(r.fecha_vencimiento)})</small></span>
                  </li>
                ))}
              </ul>
            )}
            <Link to="/normativa" className="boton fantasma pequeno">Ir al repositorio normativo</Link>
          </TarjetaGrafica>
        )}

        {datos.mejora_por_fase && (
          <TarjetaGrafica titulo="Mejora continua (PHVA)" descripcion="Acciones por fase del ciclo."
            filas={datos.mejora_por_fase} columnas={[['nombre', 'Fase'], ['cantidad', 'Acciones']]}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={datos.mejora_por_fase} margin={{ top: 10, right: 16 }}>
                <XAxis dataKey="nombre" {...EJE} />
                <YAxis allowDecimals={false} {...EJE} width={30} />
                <Tooltip content={<Globo />} cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="cantidad" name="Acciones" fill={SERIES[0]} radius={[4, 4, 0, 0]} barSize={36} />
              </BarChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {datos.accesos_recientes && (
          <TarjetaGrafica titulo="Ingresos al sistema" descripcion="Últimos 7 días: ingresos exitosos y fallidos."
            filas={datos.accesos_recientes} columnas={[['dia', 'Día'], ['ingresos', 'Exitosos'], ['fallidos', 'Fallidos o bloqueados']]}>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={datos.accesos_recientes} margin={{ top: 10, right: 16 }}>
                <CartesianGrid vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="dia" {...EJE} />
                <YAxis allowDecimals={false} {...EJE} width={30} />
                <Tooltip content={<Globo />} />
                <Legend iconType="circle" />
                <Line dataKey="ingresos" name="Exitosos" stroke={SERIES[0]} strokeWidth={2} dot={{ r: 4 }} />
                <Line dataKey="fallidos" name="Fallidos" stroke={SERIES[1]} strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </TarjetaGrafica>
        )}

        {alertas.length > 0 && (
          <section className="tarjeta">
            <h2>Alertas de inventario</h2>
            <ul className="lista-alertas">
              {alertas.map((p) => (
                <li key={p.id}>
                  <Estado tono="serio">Stock mínimo</Estado> <strong>{p.nombre}</strong>: quedan {cantidad(p.stock)}, mínimo {p.stock_minimo}.
                </li>
              ))}
            </ul>
            <Link to="/inventario" className="boton fantasma pequeno">Ver inventario</Link>
          </section>
        )}
      </div>
    </>
  )
}
