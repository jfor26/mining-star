/**
 * Datos del sitio publico de la empresa.
 *
 * Todo lo que cambia (telefono, correo, redes sociales, preguntas frecuentes)
 * esta aqui, para actualizarlo sin tocar el codigo de las pantallas.
 * Los valores entre corchetes [ ] estan pendientes: la empresa debe
 * entregarlos. Un enlace vacio ('') no se muestra en el sitio.
 */

export const CONTACTO = {
  direccion: '[DIRECCIÓN], Payandé, San Luis (Tolima)',
  telefono: '[TELÉFONO]',
  correo: '[CORREO DE CONTACTO]',
  horario: '[HORARIO DE ATENCIÓN]',
  // Numero de WhatsApp Business en formato internacional sin "+" ni espacios,
  // por ejemplo '573001234567'. Vacio = el boton no aparece.
  whatsapp: '',
  // Enlace de Google Maps para el boton "Ver en el mapa". Vacio = no aparece.
  mapa: '',
}

// Enlaces de las redes sociales. Vacio = la red no aparece en el sitio.
export const REDES = [
  { nombre: 'WhatsApp', url: '' },
  { nombre: 'Facebook', url: '' },
  { nombre: 'Instagram', url: '' },
  { nombre: 'LinkedIn', url: '' },
]

export const CUMPLIMIENTO = [
  ['Contrato de concesión minera 15834', 'Agencia Nacional de Minería (ANM)'],
  ['Licencia ambiental [N.º DE RESOLUCIÓN]', 'CORTOLIMA'],
  ['Obligaciones al día en el sistema', 'ANM, CORTOLIMA, Ministerio del Trabajo, DIAN y SIC'],
]

export const PREGUNTAS = [
  ['¿Hacen despachos fuera de Payandé?', '[RESPUESTA DE LA EMPRESA SOBRE ZONAS Y COSTOS DE DESPACHO]'],
  ['¿Cuál es la cantidad mínima de compra?', '[RESPUESTA DE LA EMPRESA SOBRE PEDIDOS MÍNIMOS]'],
  ['¿Qué formas de pago aceptan?', 'En el portal de clientes puede solicitar su cotización; las formas de pago son [FORMAS DE PAGO].'],
  ['¿Cómo hago seguimiento a una PQRS?', 'Con el número de radicado y el documento con que la radicó, en la sección PQRS de esta página.'],
]

export const PRODUCTOS_DESTACADOS = [
  ['Caliza industrial', 'Caliza para cemento', 'Materia prima para clínker y cemento; caliza de bajo magnesio.'],
  ['Agregados', 'Agregado triturado 3/4"', 'Concretos, prefabricados y mantenimiento vial.'],
  ['Agregados', 'Recebo para vías', 'Afirmado de vías terciarias y explanaciones.'],
  ['Cal agrícola', 'Cal agrícola molida', 'Corrección de suelos ácidos en arroz y frutales del Tolima.'],
  ['Marmolina', 'Marmolina blanca', 'Pisos, pegantes, estucos y acabados.'],
  ['Mármol ornamental', 'Mármol travertino para enchape', 'Enchapes de fachadas, lobbies y escaleras.'],
]
