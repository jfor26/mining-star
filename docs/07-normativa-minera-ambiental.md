# Repositorio de requisitos mineros y ambientales

Módulo **Normativa** del aplicativo (`/normativa`, API `/api/v1/normativa/`). Cada requisito guarda autoridad, categoría, norma de referencia, periodicidad, vencimiento, estado, responsable y evidencia (radicado). El dashboard alerta lo vencido y lo que vence en 30 días o menos.

> ⚠️ Es un repositorio de **referencia** para el proyecto formativo. Las fechas cargadas por `cargar_demo` son de demostración y la lista debe validarla el asesor jurídico minero de la empresa antes de usarse para decisiones reales.

| Autoridad | Categoría | Requisito | Norma de referencia | Periodicidad |
|---|---|---|---|---|
| ANM | Minero | Póliza minero-ambiental vigente | Ley 685 de 2001 (Código de Minas), art. 280 | Anual |
| ANM | Minero | Formato Básico Minero (FBM) | Ley 685 de 2001; reglamentación de la ANM | Anual |
| ANM | Minero | Declaración y pago de regalías | Ley 2056 de 2020; Ley 685 de 2001, art. 227 | Trimestral |
| ANM | Minero | Inscripción y actualización en el RUCOM | Registro Único de Comercializadores de Minerales | Anual |
| ANM | Minero | Informe de recursos y reservas (ECRR / CRIRSCO) | Resolución ANM 100 de 2020 | Al actualizar el PTO |
| ANM | Minero | Plan de Gestión Social | Plan de Gestión Social – ANM | Anual |
| CORTOLIMA | Ambiental | Licencia ambiental y Plan de Manejo Ambiental | Decreto 1076 de 2015 | Permanente |
| CORTOLIMA | Ambiental | Informe de cumplimiento ambiental (ICA) | Decreto 1076 de 2015 | Según acto administrativo |
| CORTOLIMA | Ambiental | Permiso de emisiones atmosféricas | Decreto 1076 de 2015 | Según vigencia |
| CORTOLIMA | Ambiental | Concesión de aguas y vertimientos (si aplica) | Decreto 1076 de 2015 | Según vigencia |
| MinTrabajo | SST | Sistema de Gestión de SST | Decreto 1072 de 2015; Resolución 0312 de 2019 | Anual |
| MinEnergía | SST | Seguridad en labores mineras a cielo abierto | Decreto 2222 de 1993 | Permanente |
| MinEnergía | Minero | Permiso para uso de explosivos | Decreto 2535 de 1993 | Por consumo |
| SIC | Datos | Política de tratamiento de datos personales | Ley 1581 de 2012; Decreto 1377 de 2013 | Permanente |
| DIAN | Tributario | Facturación electrónica | Estatuto Tributario, art. 616-1 | Por operación |

Cómo se usa: el Supervisor ambiental o el Gerente cambian el estado desde la tabla (Cumplido, En trámite, Pendiente, Vencido) y registran el radicado como evidencia. El Contador solo consulta.
