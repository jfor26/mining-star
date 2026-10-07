/**
 * Gestion de clientes: listado con busqueda y registro de clientes nuevos.
 * Consume GET y POST /api/v1/clientes/.
 */
import { useCallback, useEffect, useState } from 'react'

import { peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import {
  correo, longitudMaxima, requerido, soloDigitos, telefono, validar,
} from '../utils/validaciones.js'

const VACIO = { documento: '', nombre: '', correo: '', telefono: '', empresa: '' }

// Las mismas reglas que aplica el servidor (modelo Cliente y ClienteSerializer).
const REGLAS = {
  documento: [requerido, soloDigitos, longitudMaxima(20)],
  nombre: [requerido, longitudMaxima(150)],
  correo: [requerido, correo],
  telefono: [requerido, telefono],
  empresa: [requerido, longitudMaxima(150)],
}

export default function Clientes() {
  const { puede } = useSesion()
  const [lista, setLista] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [datos, setDatos] = useState(VACIO)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const cargar = useCallback(async () => {
    const ruta = `/clientes/${busqueda.trim() ? `?search=${encodeURIComponent(busqueda.trim())}` : ''}`
    setLista((await peticion(ruta)).results)
  }, [busqueda])

  useEffect(() => {
    const espera = setTimeout(() => { cargar().catch(() => setLista([])) }, 300)
    return () => clearTimeout(espera)
  }, [cargar])

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value })

  async function guardar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, REGLAS)
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return

    try {
      const creado = await peticion('/clientes/', { metodo: 'POST', datos })
      setAviso({ tipo: 'exito', texto: `Cliente ${creado.nombre} registrado.` })
      setDatos(VACIO)
      cargar()
    } catch (error) {
      // Errores que solo el servidor puede detectar, como un documento repetido.
      setErrores(erroresDeLaAPI(error))
      setAviso({ tipo: 'error', texto: 'Revise los datos del cliente.' })
    }
  }

  const columnas = [
    { clave: 'documento', titulo: 'Documento' },
    { clave: 'nombre', titulo: 'Nombre' },
    { clave: 'empresa', titulo: 'Empresa' },
    { clave: 'correo', titulo: 'Correo' },
    { clave: 'telefono', titulo: 'Teléfono' },
  ]

  return (
    <>
      <Encabezado titulo="Clientes" descripcion="Constructoras, marmolerías y personas que compran el material." />
      <div className={puede('clientes', 'crear') ? 'dos-columnas' : 'una-columna'}>
        {puede('clientes', 'crear') && (
          <section className="tarjeta">
            <h2>Registrar cliente</h2>
            <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
            <form onSubmit={guardar} noValidate>
              <Campo etiqueta="Documento" nombre="documento" value={datos.documento} onChange={cambiar}
                error={errores.documento} inputMode="numeric" maxLength={20} />
              <Campo etiqueta="Nombre" nombre="nombre" value={datos.nombre} onChange={cambiar}
                error={errores.nombre} maxLength={150} />
              <Campo etiqueta="Correo" nombre="correo" type="email" value={datos.correo} onChange={cambiar}
                error={errores.correo} />
              <Campo etiqueta="Teléfono" nombre="telefono" value={datos.telefono} onChange={cambiar}
                error={errores.telefono} inputMode="tel" maxLength={15} />
              <Campo etiqueta="Empresa" nombre="empresa" value={datos.empresa} onChange={cambiar}
                error={errores.empresa} maxLength={150} />
              <button type="submit" className="boton primario">Guardar cliente</button>
            </form>
          </section>
        )}

        <section className="tarjeta">
          <div className="barra-filtros">
            <input type="search" placeholder="Buscar por documento, nombre, empresa…" value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)} aria-label="Buscar clientes" />
          </div>
          {lista ? <Tabla columnas={columnas} filas={lista} vacio="No hay clientes registrados." /> : <Cargando />}
        </section>
      </div>
    </>
  )
}
