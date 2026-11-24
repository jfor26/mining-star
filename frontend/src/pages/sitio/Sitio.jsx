/**
 * Sitio publico de la empresa (sin iniciar sesion): productos, nosotros,
 * cumplimiento, calculadora de recebo, contacto, PQRS con radicado,
 * preguntas frecuentes y redes sociales.
 * Los datos de contacto y redes estan en src/datos/sitio.js.
 */
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { peticion } from '../../api/cliente.js'
import { Aviso, erroresDeLaAPI } from '../../components/Comunes.jsx'
import { IDENTIDAD, VALORES } from '../../datos/empresa.js'
import { CONTACTO, CUMPLIMIENTO, PREGUNTAS, PRODUCTOS_DESTACADOS, REDES } from '../../datos/sitio.js'

const TIPOS_PQRS = [['Peticion', 'Petición'], ['Queja', 'Queja'], ['Reclamo', 'Reclamo'], ['Sugerencia', 'Sugerencia']]
const PQRS_VACIA = { tipo: 'Peticion', nombre: '', documento: '', correo: '', telefono: '', detalle: '', autoriza_datos: false }
const CONTACTO_VACIO = { nombre: '', correo: '', telefono: '', mensaje: '' }

/** Volumen compactado aproximado de recebo: largo × ancho × espesor. */
// oxlint-disable-next-line react/only-export-components
export function metrosCubicos(largo, ancho, espesorCm) {
  const v = Number(largo) * Number(ancho) * (Number(espesorCm) / 100)
  return Number.isFinite(v) && v > 0 ? Math.round(v * 10) / 10 : 0
}

function Error({ texto }) {
  return texto ? <small className="error">{texto}</small> : null
}

export default function Sitio() {
  const [medidas, setMedidas] = useState({ largo: 100, ancho: 6, espesor: 20 })
  const [pqrs, setPqrs] = useState(PQRS_VACIA)
  const [erroresPqrs, setErroresPqrs] = useState({})
  const [radicado, setRadicado] = useState(null)
  const [consulta, setConsulta] = useState({ radicado: '', documento: '' })
  const [resultado, setResultado] = useState(null)
  const [contacto, setContacto] = useState(CONTACTO_VACIO)
  const [erroresContacto, setErroresContacto] = useState({})
  const [aviso, setAviso] = useState({ seccion: '', tipo: '', texto: '' })
  const [abierta, setAbierta] = useState(0)

  const redes = REDES.filter((r) => r.url)
  const whatsapp = CONTACTO.whatsapp ? `https://wa.me/${CONTACTO.whatsapp}` : ''

  async function radicar(evento) {
    evento.preventDefault()
    try {
      const r = await peticion('/publico/pqrs/', { metodo: 'POST', datos: pqrs, conToken: false })
      setRadicado(r.radicado)
      setConsulta({ radicado: r.radicado, documento: pqrs.documento })
      setPqrs(PQRS_VACIA)
      setErroresPqrs({})
    } catch (error) {
      setErroresPqrs(erroresDeLaAPI(error))
      setAviso({ seccion: 'pqrs', tipo: 'error', texto: error.estado === 429 ? 'Ha enviado muchas solicitudes. Intente más tarde.' : 'Revise los datos marcados.' })
    }
  }

  async function consultar(evento) {
    evento.preventDefault()
    setResultado(null)
    try {
      const r = await peticion(`/publico/pqrs/${encodeURIComponent(consulta.radicado.trim())}/?documento=${encodeURIComponent(consulta.documento.trim())}`, { conToken: false })
      setResultado(r)
    } catch {
      setResultado({ noEncontrada: true })
    }
  }

  async function enviarContacto(evento) {
    evento.preventDefault()
    try {
      const r = await peticion('/publico/contacto/', { metodo: 'POST', datos: contacto, conToken: false })
      setContacto(CONTACTO_VACIO)
      setErroresContacto({})
      setAviso({ seccion: 'contacto', tipo: 'exito', texto: r.mensaje })
    } catch (error) {
      setErroresContacto(erroresDeLaAPI(error))
      setAviso({ seccion: 'contacto', tipo: 'error', texto: error.estado === 429 ? 'Ha enviado muchos mensajes. Intente más tarde.' : 'Revise los datos marcados.' })
    }
  }

  const cambiar = (setter, datos) => (e) => {
    const { name, value, type, checked } = e.target
    setter({ ...datos, [name]: type === 'checkbox' ? checked : value })
  }
  const paso = (campo, delta, minimo) => setMedidas({ ...medidas, [campo]: Math.max(minimo, medidas[campo] + delta) })

  return (
    <div className="sitio">
      <header className="sitio-barra">
        <div className="sitio-contenedor sitio-barra-fila">
          <a href="#inicio" className="sitio-marca">
            <img src="/logo.png" alt="" width="44" height="44" />
            <span><strong>Mining Star Services and Products</strong><small>{IDENTIDAD.razonSocial}</small></span>
          </a>
          <nav aria-label="Secciones" className="sitio-menu">
            <a href="#productos">Productos</a>
            <a href="#nosotros">Nosotros</a>
            <a href="#cumplimiento">Cumplimiento</a>
            <a href="#contacto">Contacto</a>
            <a href="#pqrs">PQRS</a>
          </nav>
          <div className="sitio-accesos">
            <Link to="/login" className="boton secundario">Acceso personal</Link>
            <Link to="/login?modo=cliente" className="boton primario">Portal de clientes</Link>
          </div>
        </div>
      </header>

      <main>
        <section id="inicio" className="sitio-portada">
          <div className="sitio-contenedor sitio-portada-fila">
            <div className="sitio-portada-texto">
              <span className="antetitulo">Payandé, San Luis · Tolima</span>
              <h1>Caliza, mármol y recebo con origen legal y trazable.</h1>
              <p>Abastecemos la obra civil, la industria del cemento y el agro del centro del país desde el contrato de concesión minera 15834.</p>
              <div className="acciones-fila">
                <a href="#productos" className="boton grande portada-claro">Ver productos</a>
                <Link to="/login?modo=cliente" className="boton grande portada-borde">Solicitar cotización</Link>
              </div>
            </div>
            <img className="sitio-portada-imagen" src="/banner-login.jpg" alt="Logotipo de Mining Star sobre una cantera" />
          </div>
        </section>

        <section id="productos" className="sitio-contenedor sitio-seccion">
          <h2>Productos</h2>
          <p className="sitio-intro">Material de cantera y productos con valor agregado, despachados con su soporte de origen.</p>
          <div className="sitio-rejilla">
            {PRODUCTOS_DESTACADOS.map(([categoria, nombre, uso]) => (
              <article key={nombre} className="tarjeta sitio-producto">
                <span className="categoria">{categoria}</span>
                <strong>{nombre}</strong>
                <span>{uso}</span>
              </article>
            ))}
          </div>
        </section>

        <section id="nosotros" className="sitio-franja">
          <div className="sitio-contenedor sitio-seccion sitio-dos">
            <div>
              <h2>Nosotros</h2>
              <p><strong>Misión.</strong> {IDENTIDAD.mision}</p>
              <p><strong>Visión.</strong> {IDENTIDAD.vision}</p>
            </div>
            <div className="sitio-valores">
              {VALORES.slice(0, 4).map(([nombre, texto]) => (
                <div key={nombre} className="tarjeta"><strong>{nombre}</strong><span>{texto}</span></div>
              ))}
            </div>
          </div>
        </section>

        <section id="cumplimiento" className="sitio-contenedor sitio-seccion">
          <h2>Cumplimiento y calculadora</h2>
          <div className="sitio-dos">
            <ul className="sitio-cumplimiento">
              {CUMPLIMIENTO.map(([titulo, entidad]) => <li key={titulo} className="tarjeta"><strong>{titulo}</strong><span>{entidad}</span></li>)}
            </ul>
            <div className="calculadora" aria-labelledby="titulo-calculadora">
              <h3 id="titulo-calculadora">¿Cuánto recebo necesita para su vía?</h3>
              <p>Volumen compactado aproximado. Confírmelo con su ingeniero.</p>
              <div className="calculadora-medidas">
                {[['largo', 'Largo', 'm', 10, 10], ['ancho', 'Ancho', 'm', 1, 1], ['espesor', 'Espesor', 'cm', 5, 5]].map(([campo, etiqueta, unidad, delta, minimo]) => (
                  <div key={campo}>
                    <span id={`et-${campo}`}>{etiqueta}</span>
                    <div className="contador" role="group" aria-labelledby={`et-${campo}`}>
                      <button type="button" aria-label={`Menos ${etiqueta.toLowerCase()}`} onClick={() => paso(campo, -delta, minimo)}>−</button>
                      <strong aria-live="polite">{medidas[campo]} {unidad}</strong>
                      <button type="button" aria-label={`Más ${etiqueta.toLowerCase()}`} onClick={() => paso(campo, delta, minimo)}>+</button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="calculadora-resultado">
                <span>Recebo para vías</span>
                <strong>≈ {metrosCubicos(medidas.largo, medidas.ancho, medidas.espesor).toLocaleString('es-CO')} m³</strong>
              </div>
            </div>
          </div>
        </section>

        <section id="contacto" className="sitio-franja">
          <div className="sitio-contenedor sitio-seccion sitio-dos">
            <div className="sitio-datos-contacto">
              <h2>Contacto</h2>
              <dl>
                <dt>Dirección</dt><dd>{CONTACTO.direccion}</dd>
                <dt>Teléfono</dt><dd>{CONTACTO.telefono}</dd>
                <dt>Correo</dt><dd>{CONTACTO.correo}</dd>
                <dt>Horario</dt><dd>{CONTACTO.horario}</dd>
              </dl>
              <div className="acciones-fila">
                {whatsapp && <a className="boton grande boton-whatsapp" href={whatsapp} target="_blank" rel="noopener noreferrer">Escríbanos por WhatsApp</a>}
                {CONTACTO.mapa && <a className="boton secundario" href={CONTACTO.mapa} target="_blank" rel="noopener noreferrer">Ver en el mapa</a>}
              </div>
            </div>
            <form className="tarjeta sitio-formulario" onSubmit={enviarContacto} noValidate>
              <h3>Escríbanos</h3>
              {aviso.seccion === 'contacto' && <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({})}>{aviso.texto}</Aviso>}
              <label htmlFor="c-nombre">Nombre o empresa</label>
              <input id="c-nombre" name="nombre" value={contacto.nombre} onChange={cambiar(setContacto, contacto)} maxLength={150} />
              <Error texto={erroresContacto.nombre} />
              <label htmlFor="c-correo">Correo</label>
              <input id="c-correo" name="correo" type="email" value={contacto.correo} onChange={cambiar(setContacto, contacto)} />
              <Error texto={erroresContacto.correo} />
              <label htmlFor="c-telefono">Teléfono (opcional)</label>
              <input id="c-telefono" name="telefono" inputMode="tel" value={contacto.telefono} onChange={cambiar(setContacto, contacto)} maxLength={20} />
              <label htmlFor="c-mensaje">Mensaje</label>
              <textarea id="c-mensaje" name="mensaje" rows="4" value={contacto.mensaje} onChange={cambiar(setContacto, contacto)} maxLength={2000} />
              <Error texto={erroresContacto.mensaje} />
              <button type="submit" className="boton primario grande">Enviar mensaje</button>
            </form>
          </div>
        </section>

        <section id="pqrs" className="sitio-contenedor sitio-seccion sitio-dos">
          <div>
            <h2>PQRS</h2>
            <p className="sitio-intro">Radique peticiones, quejas, reclamos o sugerencias. Recibirá un número de radicado para consultar el estado y la respuesta.</p>
            <form className="tarjeta sitio-formulario" onSubmit={consultar}>
              <h3>Consultar un radicado</h3>
              <label htmlFor="q-radicado">Radicado</label>
              <input id="q-radicado" placeholder="PQRS-2026-0001" value={consulta.radicado} onChange={(e) => setConsulta({ ...consulta, radicado: e.target.value })} />
              <label htmlFor="q-documento">Documento o NIT con que la radicó</label>
              <input id="q-documento" inputMode="numeric" value={consulta.documento} onChange={(e) => setConsulta({ ...consulta, documento: e.target.value })} />
              <button type="submit" className="boton secundario" disabled={!consulta.radicado || !consulta.documento}>Consultar</button>
              {resultado && (resultado.noEncontrada
                ? <p className="resultado-consulta" role="status">No encontramos una PQRS con ese radicado y documento.</p>
                : (
                  <div className="resultado-consulta" role="status">
                    <strong>{resultado.radicado} · {resultado.tipo}</strong>
                    <span>Estado: {resultado.estado}</span>
                    {resultado.respuesta && <p>{resultado.respuesta}</p>}
                  </div>
                ))}
            </form>
          </div>
          <form className="tarjeta sitio-formulario" onSubmit={radicar} noValidate>
            {radicado ? (
              <div className="radicado-ok" role="status">
                <h3>Solicitud radicada</h3>
                <p>Su número de radicado es</p>
                <strong>{radicado}</strong>
                <p>Guárdelo para consultar el estado. La respuesta llegará también al correo que indicó.</p>
                <button type="button" className="boton secundario" onClick={() => setRadicado(null)}>Radicar otra solicitud</button>
              </div>
            ) : (
              <>
                <h3>Radicar una solicitud</h3>
                {aviso.seccion === 'pqrs' && <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({})}>{aviso.texto}</Aviso>}
                <div className="tipos-pqrs" role="radiogroup" aria-label="Tipo de solicitud">
                  {TIPOS_PQRS.map(([valor, texto]) => (
                    <button key={valor} type="button" role="radio" aria-checked={pqrs.tipo === valor}
                      className={pqrs.tipo === valor ? 'activo' : undefined} onClick={() => setPqrs({ ...pqrs, tipo: valor })}>{texto}</button>
                  ))}
                </div>
                <label htmlFor="p-nombre">Nombre completo</label>
                <input id="p-nombre" name="nombre" value={pqrs.nombre} onChange={cambiar(setPqrs, pqrs)} maxLength={150} />
                <Error texto={erroresPqrs.nombre} />
                <label htmlFor="p-documento">Documento o NIT</label>
                <input id="p-documento" name="documento" inputMode="numeric" value={pqrs.documento} onChange={cambiar(setPqrs, pqrs)} maxLength={20} />
                <Error texto={erroresPqrs.documento} />
                <label htmlFor="p-correo">Correo para la respuesta</label>
                <input id="p-correo" name="correo" type="email" value={pqrs.correo} onChange={cambiar(setPqrs, pqrs)} />
                <Error texto={erroresPqrs.correo} />
                <label htmlFor="p-detalle">Describa su {TIPOS_PQRS.find(([v]) => v === pqrs.tipo)[1].toLowerCase()}</label>
                <textarea id="p-detalle" name="detalle" rows="4" value={pqrs.detalle} onChange={cambiar(setPqrs, pqrs)} maxLength={2000} />
                <Error texto={erroresPqrs.detalle} />
                <label className="casilla">
                  <input type="checkbox" name="autoriza_datos" checked={pqrs.autoriza_datos} onChange={cambiar(setPqrs, pqrs)} />
                  Autorizo el tratamiento de mis datos personales según la política de tratamiento de datos (Ley 1581 de 2012).
                </label>
                <Error texto={erroresPqrs.autoriza_datos} />
                <button type="submit" className="boton primario grande">Radicar</button>
              </>
            )}
          </form>
        </section>

        <section className="sitio-franja">
          <div className="sitio-contenedor sitio-seccion">
            <h2>Preguntas frecuentes</h2>
            <div className="preguntas">
              {PREGUNTAS.map(([pregunta, respuesta], i) => (
                <div key={pregunta} className="tarjeta pregunta">
                  <button type="button" aria-expanded={abierta === i} onClick={() => setAbierta(abierta === i ? -1 : i)}>
                    {pregunta}<span aria-hidden="true">{abierta === i ? '−' : '+'}</span>
                  </button>
                  {abierta === i && <p>{respuesta}</p>}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="sitio-pie">
        <div className="sitio-contenedor sitio-pie-fila">
          <div>
            <strong>Mining Star Services and Products</strong>
            <span>{IDENTIDAD.razonSocial} · {IDENTIDAD.ubicacion}</span>
          </div>
          {redes.length > 0 && (
            <div>
              <span className="antetitulo">Síganos</span>
              <div className="redes">
                {redes.map((r) => <a key={r.nombre} href={r.url} target="_blank" rel="noopener noreferrer">{r.nombre}</a>)}
              </div>
            </div>
          )}
          <div className="enlaces-pie">
            <a href="#pqrs">PQRS</a>
            <span>Política de tratamiento de datos personales (Ley 1581 de 2012): [ENLACE AL DOCUMENTO]</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
