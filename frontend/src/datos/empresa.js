/**
 * Contenido estrategico de la empresa (pagina "La empresa").
 *
 * Fuente: documentos del proyecto minero del Titulo 15834 (analisis de
 * mercado, Porter, Canvas y EDT), resumidos SOLO con informacion general:
 * se excluyen cifras financieras, datos de los titulares y todo lo marcado
 * como confidencial. El mismo contenido esta en docs/06-empresa-y-estrategia.md.
 */

export const IDENTIDAD = {
  marca: 'Mining Star Services and Products',
  razonSocial: 'Industrias Mineras S.A.S.',
  ubicacion: 'Payandé, San Luis (Tolima) – Contrato de concesión minera 15834',
  mision:
    'Extraer, transformar y comercializar mármol, caliza, recebo y sus derivados de forma legal, segura y trazable, '
    + 'para abastecer a la obra civil, la industria del cemento y el agro del centro del país, apoyados en un sistema '
    + 'de gestión digital que asegura el cumplimiento minero y ambiental.',
  vision:
    'En 2030 ser el proveedor formal de referencia de caliza y derivados en el corredor Payandé – Espinal – Ibagué, '
    + 'reconocido por su trazabilidad, su cumplimiento normativo y su gestión digital, y haber pasado de vender '
    + 'material de cantera a ofrecer productos con valor agregado como la cal agrícola y la marmolina.',
}

export const VALORES = [
  ['Legalidad', 'Operamos con título, licencia y permisos al día. Nada se vende sin origen demostrable.'],
  ['Seguridad primero', 'Ninguna meta de producción justifica un riesgo para las personas.'],
  ['Respeto por el territorio', 'Cuidamos el agua, el aire y la relación con la comunidad de Payandé.'],
  ['Transparencia', 'Cada despacho, venta y pago queda registrado y es trazable.'],
  ['Trabajo en equipo', 'Mina, ventas y administración comparten la misma información en tiempo real.'],
  ['Mejora continua', 'Todo problema es una oportunidad de aprender (ciclo PHVA).'],
]

export const CULTURA = {
  principios: [
    'Nada se despacha sin registro en el sistema.',
    'La seguridad no se negocia: cualquier persona puede detener una labor insegura.',
    'Decidimos con datos: el dashboard es la fuente única de la verdad.',
    'Toda idea cuenta: cualquier empleado propone mejoras desde el aplicativo.',
  ],
  rituales: [
    ['Charla de 5 minutos', 'Al inicio de cada turno: riesgos del día y lecciones aprendidas.'],
    ['Revisión semanal de indicadores', 'Gerencia, operaciones y comercial revisan el dashboard.'],
    ['Reconocimiento mensual', 'A la mejor propuesta de mejora implementada.'],
    ['Socialización trimestral', 'Encuentro con la comunidad del área de influencia.'],
  ],
}

// Estructura jerarquica. "rol" enlaza con el cargo del sistema.
export const ORGANIGRAMA = {
  cargo: 'Asamblea de accionistas',
  hijos: [{
    cargo: 'Gerencia General', rol: 'Gerente',
    apoyo: ['Asesor jurídico minero (externo)', 'Ingeniero de minas / geólogo (externo)'],
    hijos: [
      { cargo: 'Dirección de Operaciones', rol: 'Supervisor', hijos: [
        { cargo: 'Supervisor de mina (por turno)', rol: 'Supervisor' },
        { cargo: 'Operarios de cantera', rol: 'Operario' },
      ] },
      { cargo: 'Comercial', rol: 'Comercial', hijos: [
        { cargo: 'Ejecutivo comercial (CRM y tienda)', rol: 'Comercial' },
        { cargo: 'Auxiliar de logística y bodega', rol: 'Auxiliar' },
      ] },
      { cargo: 'Administrativa y Financiera', rol: 'Contador', hijos: [
        { cargo: 'Contador', rol: 'Contador' },
        { cargo: 'Administrador del sistema', rol: 'Administrador' },
      ] },
      { cargo: 'Gestión Ambiental y SST', rol: 'Supervisor', hijos: [
        { cargo: 'Profesional ambiental y SST', rol: 'Supervisor' },
      ] },
    ],
  }],
}

// Calificacion 1-5: 5 = mayor presion sobre la rentabilidad.
export const PORTER = [
  ['Amenaza de nuevos entrantes', 2, 'Baja',
    'Obtener una concesión nueva ante la ANM toma años y la licencia ambiental suma más tiempo; además exige capital alto.',
    'Un título vigente cerca del consumidor es un activo escaso: es el argumento central del negocio.'],
  ['Poder de negociación de proveedores', 4, 'Media-alta',
    'Explosivos con proveedor único autorizado; energía con distribuidor regional único; alquiler de maquinaria competitivo.',
    'Arrendar maquinaria al inicio y pactar contratos anuales de suministro.'],
  ['Rivalidad entre competidores', 4, 'Media-alta',
    'Grandes operadores integrados con caliza propia, pequeños productores y minería informal que baja precios.',
    'Diferenciarse por formalidad, trazabilidad y menor costo de flete.'],
  ['Amenaza de sustitutos', 2, 'Baja-media',
    'Para el cemento no hay sustituto económico de la caliza; en agregados compiten material de río y reciclados.',
    'Ampliar portafolio hacia cal agrícola y marmolina.'],
  ['Poder de negociación de compradores', 5, 'Alta',
    'Mercado cementero concentrado; el material sin transformar se compra por precio y cercanía.',
    'Ningún cliente por encima del 40 % de los ingresos y avanzar hacia productos transformados.'],
]

export const VALOR_AGREGADO = [
  ['Extracción legal', 'Material con título y licencia vigentes, registrado por turno en el sistema (HU-001).'],
  ['Clasificación y trituración', 'Rajón, recebo y agregado triturado con granulometría para cada uso.'],
  ['Molienda y empaque', 'Cal agrícola y marmolina en bulto: el mayor margen por tonelada.'],
  ['Venta digital', 'Catálogo, carrito y pago en línea con Stripe; CRM para seguimiento comercial.'],
  ['Entrega trazable', 'Factura electrónica y certificado de origen en cada despacho.'],
  ['Cumplimiento visible', 'Repositorio normativo con alertas: el cliente compra sin riesgo jurídico.'],
]

export const DIFERENCIAL = [
  ['Fuente legal y trazable', 'Elimina el riesgo de comprar a la minería informal.'],
  ['Cercanía al consumo', 'En materiales de bajo valor por tonelada, el flete decide la competitividad.'],
  ['Calidad del material', 'Caliza calcítica de bajo magnesio, favorable para cemento y cal (por confirmar con muestreo representativo).'],
  ['Gestión digital', 'Mining Star ERP: inventario, ventas, pagos, CRM y cumplimiento en una sola plataforma.'],
]

// poder/interes: alto|bajo -> estrategia de gestion
export const STAKEHOLDERS = [
  ['Socios y titulares del título', 'Interno', 'alto', 'alto', 'Gestionar de cerca: informes de avance y decisiones.'],
  ['Empleados', 'Interno', 'bajo', 'alto', 'Mantener informados: charlas de turno, aplicativo, reconocimiento.'],
  ['Clientes (obra civil, cementeras, agro, marmolerías)', 'Externo', 'alto', 'alto', 'Gestionar de cerca: CRM, contratos de suministro.'],
  ['Agencia Nacional de Minería (ANM)', 'Regulador', 'alto', 'medio', 'Mantener satisfecho: reportes y pagos al día.'],
  ['CORTOLIMA (autoridad ambiental)', 'Regulador', 'alto', 'medio', 'Mantener satisfecho: cumplimiento del PMA e informes.'],
  ['Comunidad de Payandé', 'Externo', 'medio', 'alto', 'Mantener informada: Plan de Gestión Social y socializaciones.'],
  ['Proveedores (explosivos, maquinaria, transporte)', 'Externo', 'medio', 'medio', 'Monitorear: contratos anuales y evaluación.'],
  ['Inversionista u operador', 'Externo', 'alto', 'alto', 'Gestionar de cerca: data room y reportes.'],
  ['DIAN, Ministerio del Trabajo, Alcaldía', 'Regulador', 'medio', 'bajo', 'Monitorear: obligaciones tributarias y laborales.'],
  ['SENA (proyecto formativo)', 'Académico', 'bajo', 'medio', 'Mantener informado: evidencias y presentación del MVP.'],
]

export const CANVAS = [
  ['Socios clave', ['Inversionista u operador minero', 'Proveedor autorizado de explosivos', 'Alquiler de maquinaria', 'Laboratorio y geólogo', 'Transportadores locales', 'Comunidad y alcaldía']],
  ['Actividades clave', ['Saneamiento y cumplimiento ante ANM y CORTOLIMA', 'Perforación, voladura, cargue y transporte', 'Trituración y molienda', 'Comercialización y contratos', 'Gestión digital (ERP)']],
  ['Recursos clave', ['Título minero vigente', 'Licencia ambiental', 'Yacimiento cercano al consumo', 'Equipo técnico', 'Mining Star ERP']],
  ['Propuesta de valor', ['Caliza y derivados con origen legal y trazable', 'Menor flete por cercanía', 'Suministro sostenido bajo contrato', 'Compra y pago en línea']],
  ['Relación con clientes', ['Contratos anuales de suministro', 'Seguimiento con CRM', 'Certificado de origen', 'Atención técnica directa']],
  ['Canales', ['Venta en boca de mina con báscula', 'Tienda en línea', 'Contratos con plantas industriales', 'Distribuidores agrícolas', 'Licitaciones públicas']],
  ['Segmentos de clientes', ['Obra civil y vías del Tolima', 'Cementeras y concreteras del corredor', 'Distribuidores de insumos agrícolas', 'Marmolerías y prefabricados']],
  ['Estructura de costos', ['Fijos: nómina, pólizas, impuestos', 'Variables: explosivos, combustible, maquinaria, regalías', 'De entrada: saneamiento, estudios, vías']],
  ['Fuentes de ingreso', ['Venta de rajón y agregados por tonelada', 'Caliza para cemento bajo contrato', 'Cal agrícola y marmolina (mayor margen)', 'Alternativa: regalía por contrato de operación']],
]

export const EDT_EMPRESA = [
  ['1', 'Gestión del proyecto', ['1.1 Dirección y planeación', '1.2 Seguimiento jurídico', '1.3 Relación con el inversionista', '1.4 Control documental']],
  ['2', 'Saneamiento minero (ANM)', ['2.1 Póliza minero-ambiental', '2.2 Formatos Básicos Mineros', '2.3 Regalías', '2.4 Actualización del PTO', '2.5 Registro en RUCOM']],
  ['3', 'Saneamiento ambiental (CORTOLIMA)', ['3.1 Estado de la licencia', '3.2 Permiso de emisiones', '3.3 Modificación de la licencia']],
  ['4', 'Estudios técnicos', ['4.1 Campaña de campo', '4.2 Geofísica', '4.3 Muestreo y laboratorio', '4.4 Informe de recursos y reservas']],
  ['5', 'Gestión social', ['5.1 Plan de Gestión Social', '5.2 Relacionamiento con la comunidad']],
  ['6', 'Estructuración de la inversión', ['6.1 Data room', '6.2 Debida diligencia', '6.3 Contrato de entrada']],
  ['7', 'Puesta en operación', ['7.1 Vías', '7.2 Infraestructura de mina', '7.3 Maquinaria', '7.4 Comercialización', '7.5 Arranque de producción']],
]

export const EDT_SOFTWARE = [
  ['1', 'Gestión del proyecto de software', ['1.1 Plan de trabajo', '1.2 Control de versiones (Git, ramas, pull requests)', '1.3 Seguimiento con el instructor']],
  ['2', 'Análisis', ['2.1 Requisitos funcionales y no funcionales', '2.2 Historias de usuario (HU-001 producción, HU-003 ventas)', '2.3 Casos de uso']],
  ['3', 'Diseño', ['3.1 Modelo entidad-relación', '3.2 Prototipo de interfaz', '3.3 Arquitectura cliente-servidor y API REST']],
  ['4', 'Construcción', ['4.1 Backend Django + DRF', '4.2 Frontend React', '4.3 Seguridad: roles y tokens JWT', '4.4 CRM y tienda con Stripe', '4.5 Normativa y mejora continua', '4.6 Dashboard']],
  ['5', 'Pruebas', ['5.1 Plan de pruebas', '5.2 Casos de prueba', '5.3 Pruebas automatizadas (unitarias y de API)', '5.4 Pruebas funcionales en navegador']],
  ['6', 'Entrega', ['6.1 Documentación técnica', '6.2 Respaldo de la base de datos', '6.3 Presentación del MVP']],
]
