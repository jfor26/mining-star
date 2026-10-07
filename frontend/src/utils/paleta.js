/**
 * Paleta de las graficas. Orden categorico fijo y validado para daltonismo
 * (diferencia perceptual >= 8 entre series vecinas). Los colores de estado
 * se reservan para estados (cumplido, en tramite...) y nunca se usan como
 * "serie 4".
 */
export const SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300']
export const ESTADOS = { bien: '#0ca30c', aviso: '#fab219', serio: '#ec835a', critico: '#d03b3b' }
export const EJE = { stroke: '#94a3b8', fontSize: 12, tickLine: false }
