/**
 * Componentes pequenos reutilizados por todas las pantallas.
 * Reunirlos evita que cada pagina resuelva a su manera algo tan repetido
 * como un aviso, una tarjeta de indicador o un campo con su error.
 */

/** Encabezado de pagina con titulo, descripcion y acciones opcionales. */
export function Encabezado({ titulo, descripcion, children }) {
  return (
    <div className="encabezado">
      <div>
        <h1>{titulo}</h1>
        {descripcion && <p>{descripcion}</p>}
      </div>
      {children && <div className="acciones">{children}</div>}
    </div>
  )
}

/** Tarjeta con un indicador numerico. */
export function Indicador({ titulo, valor, detalle, tono = 'azul' }) {
  return (
    <article className={`indicador ${tono}`}>
      <h3>{titulo}</h3>
      <span className="valor">{valor}</span>
      {detalle && <small>{detalle}</small>}
    </article>
  )
}

/** Aviso de exito o error. role="alert" hace que un lector de pantalla lo anuncie. */
export function Aviso({ tipo = 'exito', children, alCerrar }) {
  if (!children) return null
  return (
    <div className={`aviso ${tipo}`} role={tipo === 'error' ? 'alert' : 'status'}>
      <span>{children}</span>
      {alCerrar && (
        <button type="button" onClick={alCerrar} aria-label="Cerrar aviso">×</button>
      )}
    </div>
  )
}

/**
 * Campo de formulario con etiqueta y mensaje de error.
 * Admite input, select o textarea segun la prop "como".
 */
export function Campo({ etiqueta, nombre, error, como = 'input', children, ...resto }) {
  const Control = como
  const id = `campo-${nombre}`
  return (
    <div className={`campo${error ? ' con-error' : ''}`}>
      <label htmlFor={id}>{etiqueta}</label>
      <Control
        id={id}
        name={nombre}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : undefined}
        {...resto}
      >
        {children}
      </Control>
      {error && <small id={`${id}-error`} className="error">{error}</small>}
    </div>
  )
}

/** Indicador de carga. */
export function Cargando({ texto = 'Cargando…' }) {
  return <p className="cargando" role="status">{texto}</p>
}

/**
 * Tabla generica.
 * @param columnas [{ clave, titulo, celda?: (fila) => contenido }]
 */
export function Tabla({ columnas, filas, vacio = 'No hay registros.', claveFila = 'id' }) {
  return (
    <div className="tabla-contenedor">
      <table>
        <thead>
          <tr>{columnas.map((c) => <th key={c.clave} scope="col">{c.titulo}</th>)}</tr>
        </thead>
        <tbody>
          {filas.length === 0 ? (
            <tr><td colSpan={columnas.length} className="vacio">{vacio}</td></tr>
          ) : (
            filas.map((fila) => (
              <tr key={fila[claveFila]}>
                {columnas.map((c) => (
                  <td key={c.clave}>{c.celda ? c.celda(fila) : fila[c.clave]}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

/**
 * Convierte los errores de la API ({campo: ["mensaje"]}) en {campo: "mensaje"}
 * para mostrarlos debajo de cada campo del formulario.
 */
// oxlint-disable-next-line react/only-export-components
export function erroresDeLaAPI(error) {
  const salida = {}
  for (const [campo, mensajes] of Object.entries(error?.errores ?? {})) {
    if (Array.isArray(mensajes)) salida[campo] = mensajes.join(' ')
  }
  return salida
}
