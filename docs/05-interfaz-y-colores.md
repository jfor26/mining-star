# Interfaz, colores, botones y banner

## Revisión del banner (`static/img/banner.png`)

| Hallazgo | Riesgo | Decisión |
|---|---|---|
| La excavadora muestra el logotipo **CAT** (Caterpillar), una marca registrada de un tercero | Uso de marca ajena sin autorización en un producto que se presenta como propio | En el login de React se usa un recorte (`frontend/public/banner-login.jpg`) que deja solo la estrella, el nombre y el lema. **Recomendación:** reemplazar el banner por una foto real de la cantera de Payandé. |
| Imagen de minería a gran escala (volquetas mineras, tajo abierto enorme) | No representa una cantera de pequeña minería de caliza y mármol | Igual que arriba: usar fotos propias. |
| Formato vertical 1086 × 1448 | Se recorta mal en pantallas anchas | El recorte se diseñó para el panel izquierdo del login. |
| Textos "Seguridad, Confiabilidad, Rendimiento" | Correctos y coherentes con el proyecto | Se conservan. |

## Paleta

Tomada del logo (fondo azul noche, brillo azul, estrella plata):

| Uso | Color |
|---|---|
| Menú lateral | `#0a1633` → `#0f2557` |
| Acción principal (botones, enlaces) | `#1d5bd8` |
| Fondo | `#f3f6fb` |
| Texto | `#0f172a` / secundario `#55627a` |
| Sello SENA | verde institucional `#39a900` (solo en el logo del SENA) |

**Gráficas:** paleta categórica de orden fijo (azul `#2a78d6`, naranja `#eb6834`, aguamarina `#1baf7a`, amarillo `#eda100`) validada para daltonismo. Los colores de estado (cumplido, en trámite, pendiente, vencido) son exclusivos de estados y siempre van con icono y texto, nunca solo color. Cada gráfica tiene botón **Ver tabla**.

## Botones

| Variante | Clase | Uso |
|---|---|---|
| Primario | `boton primario` | La acción principal de la pantalla (una sola) |
| Secundario | `boton secundario` | Acciones alternativas (Imprimir, Seguir comprando) |
| Fantasma | `boton fantasma` | Acciones de poco peso (Ver tabla, mover tarjeta) |
| Peligro | `boton peligro` | Anular, Quitar, Desactivar |
| Éxito | `boton exito` | Aprobar pago |
| Tamaños | `pequeno`, `grande`, `icono-solo` | Tablas, formularios principales, controles + / − |

Todos tienen estado *hover*, foco visible con teclado, efecto al presionar y estado deshabilitado mientras se envía (`Verificando…`, `Creando pedido…`). Los botones que el cargo no puede usar **no se muestran**.

## Accesibilidad

- Etiquetas `label` en todos los campos y mensajes de error asociados (`aria-describedby`).
- Avisos con `role="alert"`/`status` para lectores de pantalla.
- Pestañas con `role="tablist"` y `aria-selected`.
- Diseño adaptable: en celular el menú se abre con el botón ☰.
- Brochure imprimible: la hoja de impresión oculta menús y botones.
