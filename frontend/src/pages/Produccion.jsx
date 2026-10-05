/**
 * Produccion diaria de la mina (historia de usuario HU-001).
 *
 * Criterios de aceptacion que cubre:
 *  - seleccionar fecha y turno de trabajo;
 *  - seleccionar el material de una lista predefinida (marmol, caliza, recebo);
 *  - ingresar la cantidad en toneladas o metros cubicos;
 *  - al guardar, se actualiza el stock de materia prima y el registro queda
 *    visible en el reporte de produccion.
 */
import { useCallback, useEffect, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Indicador, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { cantidad, fecha, hoyISO } from '../utils/formato.js'
import { decimalEntre, fechaNoFutura, longitudMaxima, requerido, validar } from '../utils/validaciones.js'

const TURNOS = [['Manana', 'Mañana (6:00 - 14:00)'], ['Tarde', 'Tarde (14:00 - 22:00)'], ['Noche', 'Noche (22:00 - 6:00)']]
const MATERIALES = [['Marmol', 'Mármol'], ['Caliza', 'Caliza'], ['Recebo', 'Recebo']]
const UNIDADES = [['t', 'Toneladas (t)'], ['m3', 'Metros cúbicos (m³)']]

const nuevo = () => ({ fecha: hoyISO(), turno: '', material: '', unidad: 't', cantidad: '', supervisor: '', observaciones: '' })

const REGLAS = {
  fecha: [requerido, fechaNoFutura],
  turno: [requerido],
  material: [requerido],
  unidad: [requerido],
  cantidad: [requerido, decimalEntre(0.01, 5000)],
  observaciones: [longitudMaxima(300)],
}

/** Pide a la API el stock y los ultimos registros. No toca el estado. */
async function obtenerDatos() {
  const [stock, registros] = await Promise.all([
    peticion('/produccion/stock-materia-prima/'),
    peticion('/produccion/?ordering=-fecha'),
  ])
  return { stock, registros: registros.results }
}

export default function Produccion() {
  const [datos, setDatos] = useState(nuevo)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })
  const [stock, setStock] = useState(null)
  const [registros, setRegistros] = useState([])
  const [supervisores, setSupervisores] = useState([])

  const aplicar = useCallback((d) => { setStock(d.stock); setRegistros(d.registros) }, [])
  const cargar = useCallback(async () => aplicar(await obtenerDatos()), [aplicar])

  useEffect(() => {
    let vigente = true
    obtenerDatos()
      .then((d) => { if (vigente) aplicar(d) })
      .catch(() => { if (vigente) setAviso({ tipo: 'error', texto: 'No fue posible cargar la producción.' }) })
    obtenerTodos('/empleados/?estado=Activo&ordering=nombres')
      .then((lista) => { if (vigente) setSupervisores(lista) })
      .catch(() => {})
    return () => { vigente = false }
  }, [aplicar])

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value })

  async function guardar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, REGLAS)
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return

    try {
      const creado = await peticion('/produccion/', {
        metodo: 'POST',
        datos: { ...datos, supervisor: datos.supervisor ? Number(datos.supervisor) : null },
      })
      setAviso({ tipo: 'exito', texto: `Registrado: ${cantidad(creado.cantidad)} ${creado.unidad} de ${creado.material_nombre}, turno ${creado.turno_nombre}.` })
      setDatos(nuevo())
      cargar()
    } catch (error) {
      const deCampo = erroresDeLaAPI(error)
      setErrores(deCampo)
      // El duplicado de fecha, turno y material llega como error general.
      setAviso({ tipo: 'error', texto: deCampo.non_field_errors ?? 'Revise los datos del registro.' })
    }
  }

  const columnas = [
    { clave: 'fecha', titulo: 'Fecha', celda: (r) => fecha(`${r.fecha}T12:00:00`) },
    { clave: 'turno_nombre', titulo: 'Turno' },
    { clave: 'material_nombre', titulo: 'Material' },
    { clave: 'cantidad', titulo: 'Cantidad', celda: (r) => `${cantidad(r.cantidad)} ${r.unidad}` },
    { clave: 'supervisor_nombre', titulo: 'Supervisor', celda: (r) => r.supervisor_nombre ?? '—' },
  ]

  return (
    <>
      <Encabezado titulo="Producción de la mina" descripcion="Material extraído por turno y stock de materia prima." />
      <section className="rejilla-indicadores">
        {stock === null ? <Cargando /> : stock.length === 0
          ? <Indicador titulo="Materia prima" valor="0" detalle="Sin producción registrada" />
          : stock.map((s, i) => (
            <Indicador key={`${s.material}-${s.unidad}`} titulo={s.material_nombre}
              valor={cantidad(s.total)} detalle={s.unidad === 't' ? 'toneladas en stock' : 'metros cúbicos en stock'}
              tono={['azul', 'verde', 'naranja', 'morado'][i % 4]} />
          ))}
      </section>

      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      <div className="dos-columnas">
        <section className="tarjeta">
          <h2>Registrar producción del turno</h2>
          <form onSubmit={guardar} noValidate>
            <Campo etiqueta="Fecha" nombre="fecha" type="date" max={hoyISO()} value={datos.fecha} onChange={cambiar} error={errores.fecha} />
            <Campo como="select" etiqueta="Turno" nombre="turno" value={datos.turno} onChange={cambiar} error={errores.turno}>
              <option value="">Seleccione el turno</option>
              {TURNOS.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </Campo>
            <Campo como="select" etiqueta="Material" nombre="material" value={datos.material} onChange={cambiar} error={errores.material}>
              <option value="">Seleccione el material</option>
              {MATERIALES.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </Campo>
            <div className="fila-campos">
              <Campo etiqueta="Cantidad" nombre="cantidad" inputMode="decimal" placeholder="Ej. 35.50"
                value={datos.cantidad} onChange={cambiar} error={errores.cantidad} />
              <Campo como="select" etiqueta="Unidad" nombre="unidad" value={datos.unidad} onChange={cambiar} error={errores.unidad}>
                {UNIDADES.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
              </Campo>
            </div>
            <Campo como="select" etiqueta="Supervisor" nombre="supervisor" value={datos.supervisor} onChange={cambiar} error={errores.supervisor}>
              <option value="">Sin asignar</option>
              {supervisores.map((s) => <option key={s.id} value={s.id}>{s.nombre_completo}</option>)}
            </Campo>
            <Campo como="textarea" etiqueta="Observaciones" nombre="observaciones" rows="2" maxLength={300}
              value={datos.observaciones} onChange={cambiar} error={errores.observaciones} />
            <button type="submit" className="boton primario">Guardar registro</button>
          </form>
        </section>
        <section className="tarjeta">
          <h2>Últimos registros</h2>
          <Tabla columnas={columnas} filas={registros} vacio="Todavía no hay producción registrada." />
        </section>
      </div>
    </>
  )
}
