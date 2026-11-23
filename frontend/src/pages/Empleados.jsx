/**
 * Gestion de empleados y cargos (sugerencias del instructor, 8 de octubre):
 * busqueda, filtro por cargo, orden alfabetico o por tiempo laborado,
 * edicion y eliminacion con confirmacion.
 * Consume GET, POST, PATCH y DELETE /api/v1/empleados/.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Estado, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import {
  correo, fechaNoFutura, longitudMaxima, requerido, soloDigitos, telefono, validar,
} from '../utils/validaciones.js'

// Mismas opciones que el modelo Empleado (core/models.py). Los cargos son
// fijos porque cada uno define los permisos del usuario en el sistema.
const CARGOS = ['Gerente', 'Administrador', 'Supervisor', 'Comercial', 'Contador', 'Operario', 'Auxiliar']
const AREAS = ['Gerencia', 'Operaciones', 'Recursos Humanos', 'Seguridad Industrial', 'Finanzas',
  'Logística', 'Comercial', 'Gestión Ambiental']
const ESTADOS = ['Activo', 'Vacaciones', 'Inactivo']
const TONO_ESTADO = { Activo: 'bien', Vacaciones: 'aviso', Inactivo: 'neutro' }

const ORDENES = [
  ['nombres', 'Nombre (A–Z)'],
  ['-nombres', 'Nombre (Z–A)'],
  ['fecha_ingreso', 'Más tiempo laborado'],
  ['-fecha_ingreso', 'Menos tiempo laborado'],
]

const hoy = () => new Date().toISOString().slice(0, 10)
const VACIO = {
  documento: '', nombres: '', apellidos: '', correo: '', telefono: '',
  cargo: 'Operario', area: 'Operaciones', estado: 'Activo', fecha_ingreso: hoy(),
}

const REGLAS = {
  documento: [requerido, soloDigitos, longitudMaxima(20)],
  nombres: [requerido, longitudMaxima(100)],
  apellidos: [requerido, longitudMaxima(100)],
  correo: [requerido, correo],
  telefono: [requerido, telefono],
  fecha_ingreso: [requerido, fechaNoFutura],
}

/** Tiempo laborado legible a partir de la fecha de ingreso (AAAA-MM-DD). */
// oxlint-disable-next-line react/only-export-components
export function tiempoLaborado(fechaIngreso, referencia = new Date()) {
  const [a, m, d] = fechaIngreso.split('-').map(Number)
  let meses = (referencia.getFullYear() - a) * 12 + (referencia.getMonth() + 1 - m)
  if (referencia.getDate() < d) meses -= 1
  if (meses < 1) return 'Menos de un mes'
  const anios = Math.floor(meses / 12)
  const resto = meses % 12
  const partes = []
  if (anios) partes.push(`${anios} ${anios === 1 ? 'año' : 'años'}`)
  if (resto) partes.push(`${resto} ${resto === 1 ? 'mes' : 'meses'}`)
  return partes.join(' y ')
}

export default function Empleados() {
  const { puede } = useSesion()
  const [lista, setLista] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [cargo, setCargo] = useState('')
  const [orden, setOrden] = useState('nombres')
  const [datos, setDatos] = useState(VACIO)
  const [editando, setEditando] = useState(null)
  const [porEliminar, setPorEliminar] = useState(null)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const puedeFormulario = puede('empleados', 'crear') || (editando && puede('empleados', 'editar'))

  const cargar = useCallback(async () => {
    const params = new URLSearchParams({ ordering: orden })
    if (busqueda.trim()) params.set('search', busqueda.trim())
    if (cargo) params.set('cargo', cargo)
    setLista(await obtenerTodos(`/empleados/?${params}`))
  }, [busqueda, cargo, orden])

  useEffect(() => {
    const espera = setTimeout(() => { cargar().catch(() => setLista([])) }, 300)
    return () => clearTimeout(espera)
  }, [cargar])

  // Cuantos empleados hay por cargo en la lista actual (para los filtros).
  const conteo = useMemo(() => {
    const c = {}
    for (const e of lista ?? []) c[e.cargo] = (c[e.cargo] ?? 0) + 1
    return c
  }, [lista])

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value })

  function cancelar() {
    setEditando(null)
    setDatos(VACIO)
    setErrores({})
  }

  function editar(empleado) {
    setEditando(empleado)
    setPorEliminar(null)
    setErrores({})
    setAviso({ tipo: '', texto: '' })
    const copia = {}
    for (const campo of Object.keys(VACIO)) copia[campo] = empleado[campo] ?? ''
    setDatos(copia)
  }

  async function guardar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, REGLAS)
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return
    try {
      if (editando) {
        const actualizado = await peticion(`/empleados/${editando.id}/`, { metodo: 'PATCH', datos })
        setAviso({ tipo: 'exito', texto: `Datos de ${actualizado.nombre_completo} actualizados.` })
      } else {
        const creado = await peticion('/empleados/', { metodo: 'POST', datos })
        setAviso({ tipo: 'exito', texto: `Empleado ${creado.nombre_completo} registrado.` })
      }
      cancelar()
      cargar()
    } catch (error) {
      setErrores(erroresDeLaAPI(error))
      setAviso({ tipo: 'error', texto: 'Revise los datos del empleado.' })
    }
  }

  async function eliminar() {
    const empleado = porEliminar
    setPorEliminar(null)
    try {
      await peticion(`/empleados/${empleado.id}/`, { metodo: 'DELETE' })
      setAviso({ tipo: 'exito', texto: `Empleado ${empleado.nombre_completo} eliminado.` })
      if (editando?.id === empleado.id) cancelar()
      cargar()
    } catch (error) {
      // 409: tiene producción u otros registros asociados (on_delete=PROTECT).
      const sugerencia = error?.estado === 409 ? ' Cambie su estado a «Inactivo» para conservar el historial.' : ''
      setAviso({ tipo: 'error', texto: `${error?.message ?? 'No se pudo eliminar el empleado.'}${sugerencia}` })
    }
  }

  const columnas = [
    { clave: 'nombre_completo', titulo: 'Nombre' },
    { clave: 'documento', titulo: 'Documento' },
    { clave: 'cargo', titulo: 'Cargo' },
    { clave: 'area', titulo: 'Área' },
    { clave: 'fecha_ingreso', titulo: 'Tiempo laborado', celda: (e) => tiempoLaborado(e.fecha_ingreso) },
    { clave: 'estado', titulo: 'Estado', celda: (e) => <Estado tono={TONO_ESTADO[e.estado]}>{e.estado}</Estado> },
  ]
  if (puede('empleados', 'editar') || puede('empleados', 'eliminar')) {
    columnas.push({
      clave: 'acciones',
      titulo: 'Acciones',
      celda: (e) => (
        <div className="acciones-fila">
          {puede('empleados', 'editar') && (
            <button type="button" className="boton fantasma" onClick={() => editar(e)}
              aria-label={`Editar a ${e.nombre_completo}`}>Editar</button>
          )}
          {puede('empleados', 'eliminar') && (
            <button type="button" className="boton peligro" onClick={() => setPorEliminar(e)}
              aria-label={`Eliminar a ${e.nombre_completo}`}>Eliminar</button>
          )}
        </div>
      ),
    })
  }

  return (
    <>
      <Encabezado titulo="Empleados y cargos"
        descripcion="Personal de la empresa por cargo y área. El cargo define lo que cada empleado puede hacer en el sistema." />
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>

      {porEliminar && (
        <section className="tarjeta confirmacion" role="alertdialog" aria-labelledby="titulo-eliminar">
          <h2 id="titulo-eliminar">¿Eliminar a {porEliminar.nombre_completo}?</h2>
          <p>Esta acción no se puede deshacer. Si el empleado solo dejó de trabajar, es mejor cambiar su estado a «Inactivo» para conservar su historial.</p>
          <div className="acciones-fila">
            <button type="button" className="boton peligro" onClick={eliminar}>Sí, eliminar</button>
            <button type="button" className="boton secundario" onClick={() => setPorEliminar(null)}>Cancelar</button>
          </div>
        </section>
      )}

      <div className={puedeFormulario ? 'dos-columnas' : 'una-columna'}>
        {puedeFormulario && (
          <section className="tarjeta">
            <h2>{editando ? `Editar a ${editando.nombre_completo}` : 'Registrar empleado'}</h2>
            <form onSubmit={guardar} noValidate>
              <Campo etiqueta="Documento" nombre="documento" value={datos.documento} onChange={cambiar}
                error={errores.documento} inputMode="numeric" maxLength={20} />
              <Campo etiqueta="Nombres" nombre="nombres" value={datos.nombres} onChange={cambiar}
                error={errores.nombres} maxLength={100} />
              <Campo etiqueta="Apellidos" nombre="apellidos" value={datos.apellidos} onChange={cambiar}
                error={errores.apellidos} maxLength={100} />
              <Campo etiqueta="Correo" nombre="correo" type="email" value={datos.correo} onChange={cambiar}
                error={errores.correo} />
              <Campo etiqueta="Teléfono" nombre="telefono" value={datos.telefono} onChange={cambiar}
                error={errores.telefono} inputMode="tel" maxLength={15} />
              <Campo etiqueta="Cargo" nombre="cargo" como="select" value={datos.cargo} onChange={cambiar} error={errores.cargo}>
                {CARGOS.map((c) => <option key={c}>{c}</option>)}
              </Campo>
              <Campo etiqueta="Área" nombre="area" como="select" value={datos.area} onChange={cambiar} error={errores.area}>
                {AREAS.map((a) => <option key={a}>{a}</option>)}
              </Campo>
              <Campo etiqueta="Estado" nombre="estado" como="select" value={datos.estado} onChange={cambiar} error={errores.estado}>
                {ESTADOS.map((s) => <option key={s}>{s}</option>)}
              </Campo>
              <Campo etiqueta="Fecha de ingreso" nombre="fecha_ingreso" type="date" value={datos.fecha_ingreso}
                onChange={cambiar} error={errores.fecha_ingreso} max={hoy()} />
              <div className="acciones-fila">
                <button type="submit" className="boton primario">{editando ? 'Guardar cambios' : 'Guardar empleado'}</button>
                {editando && <button type="button" className="boton secundario" onClick={cancelar}>Cancelar</button>}
              </div>
            </form>
          </section>
        )}

        <section className="tarjeta">
          <div className="barra-filtros">
            <input type="search" placeholder="Buscar por documento, nombre o correo…" value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)} aria-label="Buscar empleados" />
            <select value={orden} onChange={(e) => setOrden(e.target.value)} aria-label="Ordenar empleados">
              {ORDENES.map(([valor, texto]) => <option key={valor} value={valor}>{texto}</option>)}
            </select>
          </div>
          <div className="chips" role="group" aria-label="Filtrar por cargo">
            <button type="button" className={`chip${cargo === '' ? ' activo' : ''}`} aria-pressed={cargo === ''}
              onClick={() => setCargo('')}>Todos</button>
            {CARGOS.map((c) => (
              <button key={c} type="button" className={`chip${cargo === c ? ' activo' : ''}`} aria-pressed={cargo === c}
                onClick={() => setCargo(cargo === c ? '' : c)}>
                {c}{cargo === '' && conteo[c] ? ` (${conteo[c]})` : ''}
              </button>
            ))}
          </div>
          {lista ? (
            <>
              <Tabla columnas={columnas} filas={lista} vacio="No hay empleados con esos criterios." />
              <p className="pie-tabla">{lista.length} {lista.length === 1 ? 'empleado' : 'empleados'}</p>
            </>
          ) : <Cargando />}
        </section>
      </div>
    </>
  )
}
