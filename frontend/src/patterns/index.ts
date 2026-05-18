// src/patterns/index.ts
export type ProposalCategory =
  | 'actor' | 'objeto' | 'operacion' | 'estado' | 'relacion'
  | 'regla' | 'evento' | 'tiempo' | 'recurso' | 'espacio'
  | 'comunicacion' | 'modulo' | 'objetivo';

export type Severity = 'ALTA' | 'MEDIA' | 'BAJA';

export interface PatternItem {
  name: string;
  category: ProposalCategory;
  rationale: string;
  priority: Severity;
}

export interface SystemPattern {
  id: string;
  display: string;
  backendMappings: string[];
  rbac: boolean;
  description: string;
  items: PatternItem[];
}

// ============================================================
// PATRÓN CRM
// ============================================================
const CRM_ITEMS: PatternItem[] = [
  // Actores (FASE_0)
  { name: 'Vendedor', category: 'actor', rationale: 'Gestiona leads y oportunidades de venta', priority: 'ALTA' },
  { name: 'Gerente de Ventas', category: 'actor', rationale: 'Supervisa pipeline y metas del equipo', priority: 'ALTA' },
  { name: 'Cliente', category: 'actor', rationale: 'Recibe comunicaciones y cotizaciones', priority: 'MEDIA' },
  { name: 'Administrador CRM', category: 'actor', rationale: 'Configura flujos y permisos', priority: 'MEDIA' },
  
  // Objetos (FASE_1)
  { name: 'Lead', category: 'objeto', rationale: 'Prospecto inicial sin calificar', priority: 'ALTA' },
  { name: 'Oportunidad', category: 'objeto', rationale: 'Lead calificado con potencial de cierre', priority: 'ALTA' },
  { name: 'Contacto', category: 'objeto', rationale: 'Información detallada del cliente', priority: 'ALTA' },
  { name: 'Cuenta', category: 'objeto', rationale: 'Organización o empresa cliente', priority: 'ALTA' },
  { name: 'Cotización', category: 'objeto', rationale: 'Propuesta de precio enviada al cliente', priority: 'MEDIA' },
  { name: 'Pedido', category: 'objeto', rationale: 'Orden de compra generada', priority: 'ALTA' },
  
  // Operaciones (FASE_2)
  { name: 'CrearLead', category: 'operacion', rationale: 'Ingresar nuevo prospecto al sistema', priority: 'ALTA' },
  { name: 'CalificarLead', category: 'operacion', rationale: 'Determinar si el lead es oportunidad', priority: 'ALTA' },
  { name: 'AsignarVendedor', category: 'operacion', rationale: 'Distribuir leads entre el equipo', priority: 'MEDIA' },
  { name: 'AvanzarEtapa', category: 'operacion', rationale: 'Mover oportunidad en el pipeline', priority: 'ALTA' },
  { name: 'GenerarCotizacion', category: 'operacion', rationale: 'Crear propuesta comercial', priority: 'MEDIA' },
  { name: 'CerrarGanado', category: 'operacion', rationale: 'Registrar venta exitosa', priority: 'ALTA' },
  { name: 'CerrarPerdido', category: 'operacion', rationale: 'Registrar venta no concretada', priority: 'MEDIA' },
  
  // Estados (FASE_3)
  { name: 'Nuevo', category: 'estado', rationale: 'Lead recién ingresado', priority: 'ALTA' },
  { name: 'Contactado', category: 'estado', rationale: 'Se ha establecido comunicación', priority: 'ALTA' },
  { name: 'Calificado', category: 'estado', rationale: 'Lead evaluado como oportunidad', priority: 'ALTA' },
  { name: 'PropuestaEnviada', category: 'estado', rationale: 'Cotización presentada al cliente', priority: 'MEDIA' },
  { name: 'Negociación', category: 'estado', rationale: 'En proceso de cierre', priority: 'ALTA' },
  { name: 'Ganado', category: 'estado', rationale: 'Venta concretada', priority: 'ALTA' },
  { name: 'Perdido', category: 'estado', rationale: 'Venta no concretada', priority: 'MEDIA' },
  
  // Reglas (FASE_4)
  { name: 'No vender a clientes morosos', category: 'regla', rationale: 'Evita riesgo crediticio', priority: 'ALTA' },
  { name: 'No duplicar leads por email', category: 'regla', rationale: 'Mantiene integridad de datos', priority: 'ALTA' },
  { name: 'No asignar más de 50 leads activos por vendedor', category: 'regla', rationale: 'Evita saturación', priority: 'MEDIA' },
  { name: 'No modificar historial de cliente sin justificación', category: 'regla', rationale: 'Garantiza auditoría', priority: 'ALTA' },
  { name: 'No eliminar leads cerrados', category: 'regla', rationale: 'Conserva histórico', priority: 'MEDIA' },
  
  // Eventos (FASE_5)
  { name: 'LeadCreado', category: 'evento', rationale: 'Se ingresó un nuevo lead', priority: 'ALTA' },
  { name: 'LeadCalificado', category: 'evento', rationale: 'Lead pasó a oportunidad', priority: 'ALTA' },
  { name: 'OportunidadAvanzada', category: 'evento', rationale: 'Cambio de etapa en pipeline', priority: 'MEDIA' },
  { name: 'VentaCerrada', category: 'evento', rationale: 'Se concretó una venta', priority: 'ALTA' },
  
  // Tiempo (FASE_6)
  { name: 'SLA Contacto Inicial', category: 'tiempo', rationale: 'Tiempo para contactar lead nuevo', priority: 'ALTA' },
  { name: 'SLA Respuesta Cotización', category: 'tiempo', rationale: 'Tiempo para enviar presupuesto', priority: 'MEDIA' },
  { name: 'Tiempo Promedio Cierre', category: 'tiempo', rationale: 'Lead-to-cash cycle time', priority: 'ALTA' },
  
  // Recursos (FASE_7)
  { name: 'API Calls', category: 'recurso', rationale: 'Límite de integraciones externas', priority: 'MEDIA' },
  { name: 'Almacenamiento Documentos', category: 'recurso', rationale: 'Cotizaciones y anexos', priority: 'MEDIA' },
  
  // Espacio (FASE_7B)
  { name: 'Zona Horaria Local', category: 'espacio', rationale: 'Ubicación geográfica del vendedor', priority: 'MEDIA' },
  
  // Comunicación (FASE_7C)
  { name: 'Email', category: 'comunicacion', rationale: 'Notificaciones y cotizaciones', priority: 'ALTA' },
  { name: 'Webhook', category: 'comunicacion', rationale: 'Integración con marketing tools', priority: 'MEDIA' },
  
  // Módulos (FASE_8)
  { name: 'Dashboard Ventas', category: 'modulo', rationale: 'Reportes y métricas del equipo', priority: 'ALTA' },
  { name: 'Email Integración', category: 'modulo', rationale: 'Sincronización con correo', priority: 'MEDIA' },
  
  // Objetivos (FASE_8B)
  { name: 'Reducir ciclo de ventas 30%', category: 'objetivo', rationale: 'Mayor eficiencia comercial', priority: 'ALTA' },
  { name: 'Aumentar tasa de conversión', category: 'objetivo', rationale: 'Mejor calificación de leads', priority: 'ALTA' },
];

// ============================================================
// PATRÓN ERP
// ============================================================
const ERP_ITEMS: PatternItem[] = [
  { name: 'Contador', category: 'actor', rationale: 'Gestiona finanzas y contabilidad', priority: 'ALTA' },
  { name: 'Almacenista', category: 'actor', rationale: 'Controla inventario y movimientos', priority: 'ALTA' },
  { name: 'Compras', category: 'actor', rationale: 'Gestiona órdenes a proveedores', priority: 'ALTA' },
  { name: 'Ventas', category: 'actor', rationale: 'Registra pedidos de clientes', priority: 'ALTA' },
  { name: 'RH', category: 'actor', rationale: 'Administra personal y nóminas', priority: 'MEDIA' },
  { name: 'Gerente General', category: 'actor', rationale: 'Supervisa estados financieros', priority: 'ALTA' },
  
  { name: 'Factura', category: 'objeto', rationale: 'Documento fiscal de venta', priority: 'ALTA' },
  { name: 'OrdenCompra', category: 'objeto', rationale: 'Solicitud a proveedor', priority: 'ALTA' },
  { name: 'Producto', category: 'objeto', rationale: 'Artículo en inventario', priority: 'ALTA' },
  { name: 'Proveedor', category: 'objeto', rationale: 'Entidad que suministra productos', priority: 'ALTA' },
  { name: 'Empleado', category: 'objeto', rationale: 'Personal de la empresa', priority: 'ALTA' },
  { name: 'AsientoContable', category: 'objeto', rationale: 'Registro de transacción financiera', priority: 'ALTA' },
  { name: 'Inventario', category: 'objeto', rationale: 'Stock de productos', priority: 'ALTA' },
  
  { name: 'RegistrarFactura', category: 'operacion', rationale: 'Emitir comprobante fiscal', priority: 'ALTA' },
  { name: 'ActualizarInventario', category: 'operacion', rationale: 'Ajustar stock por venta/compra', priority: 'ALTA' },
  { name: 'ConciliarBancos', category: 'operacion', rationale: 'Comparar movimientos vs estado de cuenta', priority: 'ALTA' },
  { name: 'GenerarNómina', category: 'operacion', rationale: 'Calcular sueldos y deducciones', priority: 'MEDIA' },
  { name: 'CalcularISR', category: 'operacion', rationale: 'Determinar impuesto a pagar', priority: 'ALTA' },
  
  { name: 'Borrador', category: 'estado', rationale: 'Documento iniciado sin validar', priority: 'MEDIA' },
  { name: 'Validado', category: 'estado', rationale: 'Documento revisado y aprobado', priority: 'ALTA' },
  { name: 'Pagado', category: 'estado', rationale: 'Factura liquidada', priority: 'ALTA' },
  { name: 'Cancelado', category: 'estado', rationale: 'Documento anulado', priority: 'MEDIA' },
  
  { name: 'No registrar factura sin RFC', category: 'regla', rationale: 'Cumplimiento fiscal', priority: 'ALTA' },
  { name: 'No permitir inventario negativo', category: 'regla', rationale: 'Control de stock', priority: 'ALTA' },
  { name: 'No eliminar asientos contables', category: 'regla', rationale: 'Pista de auditoría', priority: 'ALTA' },
  
  { name: 'FacturaEmitida', category: 'evento', rationale: 'Se generó un comprobante fiscal', priority: 'ALTA' },
  { name: 'StockBajo', category: 'evento', rationale: 'Inventario por debajo del mínimo', priority: 'ALTA' },
  { name: 'PagoRegistrado', category: 'evento', rationale: 'Cliente liquidó factura', priority: 'MEDIA' },
  
  { name: 'SLA Facturación', category: 'tiempo', rationale: 'Tiempo para emitir factura', priority: 'ALTA' },
  { name: 'Cierre Contable Mensual', category: 'tiempo', rationale: 'Fecha límite de registros', priority: 'ALTA' },
  
  { name: 'Procesamiento Batch', category: 'recurso', rationale: 'Nómina y cálculos masivos', priority: 'MEDIA' },
  
  { name: 'Módulo Contabilidad', category: 'modulo', rationale: 'Registro financiero', priority: 'ALTA' },
  { name: 'Módulo Inventarios', category: 'modulo', rationale: 'Control de stock', priority: 'ALTA' },
  { name: 'Módulo Ventas', category: 'modulo', rationale: 'Gestión de pedidos', priority: 'ALTA' },
  
  { name: 'Reducir errores contables 50%', category: 'objetivo', rationale: 'Automatización de registros', priority: 'ALTA' },
  { name: 'Optimizar rotación inventario', category: 'objetivo', rationale: 'Mejor gestión de stock', priority: 'MEDIA' },
];

// ============================================================
// PATRÓN ECOMMERCE
// ============================================================
const ECOMMERCE_ITEMS: PatternItem[] = [
  { name: 'Cliente', category: 'actor', rationale: 'Realiza compras en línea', priority: 'ALTA' },
  { name: 'Vendedor', category: 'actor', rationale: 'Gestiona productos y precios', priority: 'ALTA' },
  { name: 'Soporte', category: 'actor', rationale: 'Atención al cliente postventa', priority: 'MEDIA' },
  { name: 'Logística', category: 'actor', rationale: 'Prepara y envía pedidos', priority: 'ALTA' },
  
  { name: 'Producto', category: 'objeto', rationale: 'Artículo en catálogo', priority: 'ALTA' },
  { name: 'Carrito', category: 'objeto', rationale: 'Selección temporal de productos', priority: 'ALTA' },
  { name: 'Pedido', category: 'objeto', rationale: 'Compra realizada', priority: 'ALTA' },
  { name: 'Pago', category: 'objeto', rationale: 'Transacción financiera', priority: 'ALTA' },
  { name: 'Envío', category: 'objeto', rationale: 'Información de entrega', priority: 'ALTA' },
  { name: 'Reseña', category: 'objeto', rationale: 'Opinión del cliente', priority: 'MEDIA' },
  
  { name: 'BuscarProducto', category: 'operacion', rationale: 'Búsqueda por categoría/texto', priority: 'ALTA' },
  { name: 'AgregarAlCarrito', category: 'operacion', rationale: 'Añadir producto al carrito', priority: 'ALTA' },
  { name: 'Checkout', category: 'operacion', rationale: 'Proceso de pago', priority: 'ALTA' },
  { name: 'ProcesarPago', category: 'operacion', rationale: 'Ejecutar transacción', priority: 'ALTA' },
  { name: 'GenerarGuía', category: 'operacion', rationale: 'Crear envío', priority: 'MEDIA' },
  { name: 'CalificarProducto', category: 'operacion', rationale: 'Dejar reseña', priority: 'MEDIA' },
  
  { name: 'CarritoActivo', category: 'estado', rationale: 'Cliente agregó productos sin pagar', priority: 'ALTA' },
  { name: 'Pagado', category: 'estado', rationale: 'Transacción completada', priority: 'ALTA' },
  { name: 'Enviado', category: 'estado', rationale: 'Pedido en ruta', priority: 'ALTA' },
  { name: 'Entregado', category: 'estado', rationale: 'Cliente recibió producto', priority: 'ALTA' },
  { name: 'Cancelado', category: 'estado', rationale: 'Pedido anulado', priority: 'MEDIA' },
  { name: 'Devuelto', category: 'estado', rationale: 'Cliente solicitó reembolso', priority: 'MEDIA' },
  
  { name: 'No vender producto sin inventario', category: 'regla', rationale: 'Evita sobreventa', priority: 'ALTA' },
  { name: 'No permitir checkout sin autenticación', category: 'regla', rationale: 'Seguridad', priority: 'ALTA' },
  { name: 'No mostrar precio sin stock', category: 'regla', rationale: 'Transparencia', priority: 'MEDIA' },
  
  { name: 'CarritoAbandonado', category: 'evento', rationale: 'Cliente no completó compra', priority: 'ALTA' },
  { name: 'PagoExitoso', category: 'evento', rationale: 'Transacción aprobada', priority: 'ALTA' },
  { name: 'PagoFallido', category: 'evento', rationale: 'Rechazo de tarjeta', priority: 'ALTA' },
  { name: 'ProductoAgotado', category: 'evento', rationale: 'Stock llegó a cero', priority: 'MEDIA' },
  
  { name: 'SLA Despacho', category: 'tiempo', rationale: 'Tiempo de preparación', priority: 'ALTA' },
  { name: 'Tiempo de Entrega', category: 'tiempo', rationale: 'Días estimados de envío', priority: 'ALTA' },
  { name: 'Tiempo Abandono Carrito', category: 'tiempo', rationale: 'Minutos para recordatorio', priority: 'MEDIA' },
  
  { name: 'Pasarela de Pagos', category: 'comunicacion', rationale: 'Conexión con banco', priority: 'ALTA' },
  { name: 'API Envíos', category: 'comunicacion', rationale: 'Integración con paquetería', priority: 'MEDIA' },
  
  { name: 'Recomendador Productos', category: 'modulo', rationale: 'Sugerencias personalizadas', priority: 'MEDIA' },
  { name: 'Chat Soporte', category: 'modulo', rationale: 'Atención en tiempo real', priority: 'MEDIA' },
  
  { name: 'Reducir carritos abandonados 40%', category: 'objetivo', rationale: 'Email recovery', priority: 'ALTA' },
  { name: 'Aumentar conversión checkout', category: 'objetivo', rationale: 'Optimizar UX de pago', priority: 'ALTA' },
];

// ============================================================
// PATRÓN POS (Punto de Venta)
// ============================================================
const POS_ITEMS: PatternItem[] = [
  { name: 'Cajero', category: 'actor', rationale: 'Registra ventas en mostrador', priority: 'ALTA' },
  { name: 'Gerente Tienda', category: 'actor', rationale: 'Supervisa cierres de caja', priority: 'ALTA' },
  { name: 'Cliente', category: 'actor', rationale: 'Realiza compra física', priority: 'ALTA' },
  
  { name: 'Venta', category: 'objeto', rationale: 'Transacción de mostrador', priority: 'ALTA' },
  { name: 'Producto', category: 'objeto', rationale: 'Artículo con código de barras', priority: 'ALTA' },
  { name: 'Ticket', category: 'objeto', rationale: 'Comprobante impreso/digital', priority: 'ALTA' },
  { name: 'CorteCaja', category: 'objeto', rationale: 'Cierre de turno', priority: 'ALTA' },
  { name: 'Devolución', category: 'objeto', rationale: 'Reembolso de producto', priority: 'MEDIA' },
  
  { name: 'EscanearProducto', category: 'operacion', rationale: 'Leer código de barras', priority: 'ALTA' },
  { name: 'RegistrarVenta', category: 'operacion', rationale: 'Capturar transacción', priority: 'ALTA' },
  { name: 'AplicarDescuento', category: 'operacion', rationale: 'Reducir precio por promoción', priority: 'MEDIA' },
  { name: 'CerrarTurno', category: 'operacion', rationale: 'Generar corte de caja', priority: 'ALTA' },
  { name: 'ProcesarEfectivo', category: 'operacion', rationale: 'Calcular cambio', priority: 'ALTA' },
  
  { name: 'Abierta', category: 'estado', rationale: 'Caja en operación', priority: 'ALTA' },
  { name: 'Cerrada', category: 'estado', rationale: 'Turno finalizado', priority: 'ALTA' },
  
  { name: 'No vender sin inventario', category: 'regla', rationale: 'Validar stock antes de cobrar', priority: 'ALTA' },
  { name: 'No cerrar caja con discrepancias', category: 'regla', rationale: 'Forzar auditoría', priority: 'ALTA' },
  
  { name: 'VentaRegistrada', category: 'evento', rationale: 'Transacción completada', priority: 'ALTA' },
  { name: 'StockCritico', category: 'evento', rationale: 'Producto por agotarse', priority: 'ALTA' },
  
  { name: 'SLA Atención Mostrador', category: 'tiempo', rationale: 'Tiempo por cliente', priority: 'MEDIA' },
  
  { name: 'Impresora Tickets', category: 'recurso', rationale: 'Dispositivo físico', priority: 'ALTA' },
  { name: 'Lector Códigos', category: 'recurso', rationale: 'Scanner de barras', priority: 'ALTA' },
  
  { name: 'Modulo Inventario', category: 'modulo', rationale: 'Control de stock', priority: 'ALTA' },
  { name: 'Modulo Clientes', category: 'modulo', rationale: 'Programa de lealtad', priority: 'MEDIA' },
  
  { name: 'Reducir tiempo por transacción', category: 'objetivo', rationale: 'Mayor eficiencia', priority: 'ALTA' },
];

// ============================================================
// PATRÓN MANUFACTURA
// ============================================================
const MANUFACTURA_ITEMS: PatternItem[] = [
  { name: 'Operador Máquina', category: 'actor', rationale: 'Ejecuta procesos productivos', priority: 'ALTA' },
  { name: 'Supervisor Planta', category: 'actor', rationale: 'Monitorea producción', priority: 'ALTA' },
  { name: 'Planeador', category: 'actor', rationale: 'Programa órdenes de producción', priority: 'ALTA' },
  { name: 'Control Calidad', category: 'actor', rationale: 'Inspecciona productos', priority: 'ALTA' },
  { name: 'Mantenimiento', category: 'actor', rationale: 'Gestiona equipos', priority: 'MEDIA' },
  
  { name: 'OrdenProducción', category: 'objeto', rationale: 'Instrucción de fabricación', priority: 'ALTA' },
  { name: 'ProductoTerminado', category: 'objeto', rationale: 'Bien final', priority: 'ALTA' },
  { name: 'MaterialPrima', category: 'objeto', rationale: 'Insumo para producción', priority: 'ALTA' },
  { name: 'Lote', category: 'objeto', rationale: 'Agrupación trazable', priority: 'ALTA' },
  { name: 'Máquina', category: 'objeto', rationale: 'Equipo de producción', priority: 'ALTA' },
  { name: 'Defecto', category: 'objeto', rationale: 'Producto no conforme', priority: 'MEDIA' },
  
  { name: 'IniciarProducción', category: 'operacion', rationale: 'Arrancar orden', priority: 'ALTA' },
  { name: 'RegistrarProducción', category: 'operacion', rationale: 'Reportar cantidad fabricada', priority: 'ALTA' },
  { name: 'ConsumirMaterial', category: 'operacion', rationale: 'Descontar insumo', priority: 'ALTA' },
  { name: 'InspeccionarCalidad', category: 'operacion', rationale: 'Verificar especificaciones', priority: 'ALTA' },
  { name: 'CerrarOrden', category: 'operacion', rationale: 'Finalizar producción', priority: 'ALTA' },
  { name: 'RegistrarParo', category: 'operacion', rationale: 'Reportar detención de máquina', priority: 'MEDIA' },
  
  { name: 'Planeada', category: 'estado', rationale: 'Orden programada', priority: 'ALTA' },
  { name: 'EnProceso', category: 'estado', rationale: 'Fabricación activa', priority: 'ALTA' },
  { name: 'Completada', category: 'estado', rationale: 'Producción finalizada', priority: 'ALTA' },
  { name: 'Detenida', category: 'estado', rationale: 'Paro no programado', priority: 'MEDIA' },
  { name: 'Cancelada', category: 'estado', rationale: 'Orden anulada', priority: 'MEDIA' },
  
  { name: 'No producir sin material', category: 'regla', rationale: 'Validar inventario', priority: 'ALTA' },
  { name: 'No liberar producto sin QA', category: 'regla', rationale: 'Control de calidad', priority: 'ALTA' },
  
  { name: 'OrdenIniciada', category: 'evento', rationale: 'Producción arrancada', priority: 'ALTA' },
  { name: 'OrdenCompletada', category: 'evento', rationale: 'Fabricación finalizada', priority: 'ALTA' },
  { name: 'ParoMáquina', category: 'evento', rationale: 'Falla detectada', priority: 'ALTA' },
  
  { name: 'Tiempo Ciclo', category: 'tiempo', rationale: 'Tasa de producción', priority: 'ALTA' },
  { name: 'OEE', category: 'tiempo', rationale: 'Efectividad global del equipo', priority: 'ALTA' },
  
  { name: 'MES', category: 'modulo', rationale: 'Sistema ejecución manufactura', priority: 'ALTA' },
  { name: 'SCADA', category: 'modulo', rationale: 'Monitoreo en tiempo real', priority: 'MEDIA' },
  
  { name: 'Aumentar OEE 20%', category: 'objetivo', rationale: 'Reducir paros', priority: 'ALTA' },
  { name: 'Reducir defectos 50%', category: 'objetivo', rationale: 'Mejorar calidad', priority: 'ALTA' },
];

// ============================================================
// PATRÓN LOGÍSTICA
// ============================================================
const LOGISTICA_ITEMS: PatternItem[] = [
  { name: 'Operador Ruta', category: 'actor', rationale: 'Conduce vehículo de reparto', priority: 'ALTA' },
  { name: 'Despachador', category: 'actor', rationale: 'Prepara cargas', priority: 'ALTA' },
  { name: 'Coordinador Flota', category: 'actor', rationale: 'Asigna rutas', priority: 'ALTA' },
  { name: 'Cliente', category: 'actor', rationale: 'Recibe mercancía', priority: 'ALTA' },
  
  { name: 'Envío', category: 'objeto', rationale: 'Paquete a entregar', priority: 'ALTA' },
  { name: 'Ruta', category: 'objeto', rationale: 'Trayecto planificado', priority: 'ALTA' },
  { name: 'Vehículo', category: 'objeto', rationale: 'Unidad de transporte', priority: 'ALTA' },
  { name: 'Manifiesto', category: 'objeto', rationale: 'Lista de envíos', priority: 'ALTA' },
  { name: 'EventoGPS', category: 'objeto', rationale: 'Posición geográfica', priority: 'MEDIA' },
  
  { name: 'AsignarRuta', category: 'operacion', rationale: 'Vincular envíos a vehículo', priority: 'ALTA' },
  { name: 'IniciarRuta', category: 'operacion', rationale: 'Comenzar recorrido', priority: 'ALTA' },
  { name: 'RegistrarEntrega', category: 'operacion', rationale: 'Confirmar recepción', priority: 'ALTA' },
  { name: 'ReportarIncidencia', category: 'operacion', rationale: 'Retraso o falla', priority: 'MEDIA' },
  
  { name: 'Pendiente', category: 'estado', rationale: 'Envío sin asignar', priority: 'ALTA' },
  { name: 'EnRuta', category: 'estado', rationale: 'Vehículo transportando', priority: 'ALTA' },
  { name: 'Entregado', category: 'estado', rationale: 'Cliente recibió', priority: 'ALTA' },
  { name: 'Devuelto', category: 'estado', rationale: 'No entregado', priority: 'MEDIA' },
  
  { name: 'No entregar sin firma', category: 'regla', rationale: 'Evidencia de recepción', priority: 'ALTA' },
  { name: 'No desviarse de ruta', category: 'regla', rationale: 'Eficiencia', priority: 'MEDIA' },
  
  { name: 'EnvíoAsignado', category: 'evento', rationale: 'Paquete en ruta', priority: 'ALTA' },
  { name: 'EntregaConfirmada', category: 'evento', rationale: 'Recepción exitosa', priority: 'ALTA' },
  { name: 'RetrasoDetectado', category: 'evento', rationale: 'Desviación de horario', priority: 'ALTA' },
  
  { name: 'SLA Entrega', category: 'tiempo', rationale: 'Días máximos', priority: 'ALTA' },
  { name: 'Tiempo Ruta', category: 'tiempo', rationale: 'Duración estimada', priority: 'ALTA' },
  
  { name: 'GPS Rastreo', category: 'espacio', rationale: 'Ubicación en tiempo real', priority: 'ALTA' },
  { name: 'Zonas Geográficas', category: 'espacio', rationale: 'Regiones de reparto', priority: 'MEDIA' },
  
  { name: 'API Mapas', category: 'comunicacion', rationale: 'Cálculo de rutas', priority: 'ALTA' },
  
  { name: 'Optimizador Rutas', category: 'modulo', rationale: 'Reducción de km', priority: 'ALTA' },
  
  { name: 'Reducir tiempo entrega 24h', category: 'objetivo', rationale: 'Velocidad logística', priority: 'ALTA' },
  { name: 'Disminuir costo por envío 15%', category: 'objetivo', rationale: 'Eficiencia', priority: 'ALTA' },
];

// ============================================================
// PATRÓN HOSPITALARIO
// ============================================================
const HOSPITALARIO_ITEMS: PatternItem[] = [
  { name: 'Médico', category: 'actor', rationale: 'Atiende pacientes y prescribe', priority: 'ALTA' },
  { name: 'Enfermera', category: 'actor', rationale: 'Aplica tratamientos', priority: 'ALTA' },
  { name: 'Paciente', category: 'actor', rationale: 'Recibe atención médica', priority: 'ALTA' },
  { name: 'Administrativo', category: 'actor', rationale: 'Gestiona citas y facturación', priority: 'ALTA' },
  { name: 'Farmacia', category: 'actor', rationale: 'Dispensa medicamentos', priority: 'MEDIA' },
  
  { name: 'Expediente', category: 'objeto', rationale: 'Historial clínico', priority: 'ALTA' },
  { name: 'Cita', category: 'objeto', rationale: 'Agendamiento de consulta', priority: 'ALTA' },
  { name: 'Receta', category: 'objeto', rationale: 'Prescripción médica', priority: 'ALTA' },
  { name: 'Diagnóstico', category: 'objeto', rationale: 'Condición identificada', priority: 'ALTA' },
  { name: 'Estudio', category: 'objeto', rationale: 'Laboratorio o imagen', priority: 'MEDIA' },
  
  { name: 'AgendarCita', category: 'operacion', rationale: 'Reservar horario', priority: 'ALTA' },
  { name: 'RegistrarAtención', category: 'operacion', rationale: 'Notas médicas', priority: 'ALTA' },
  { name: 'Prescribir', category: 'operacion', rationale: 'Emitir receta', priority: 'ALTA' },
  { name: 'SolicitarEstudio', category: 'operacion', rationale: 'Orden de laboratorio', priority: 'MEDIA' },
  
  { name: 'Agendada', category: 'estado', rationale: 'Cita programada', priority: 'ALTA' },
  { name: 'EnCurso', category: 'estado', rationale: 'Atención en proceso', priority: 'ALTA' },
  { name: 'Completada', category: 'estado', rationale: 'Consulta finalizada', priority: 'ALTA' },
  { name: 'Cancelada', category: 'estado', rationale: 'No atendida', priority: 'MEDIA' },
  
  { name: 'No atender sin expediente', category: 'regla', rationale: 'Continuidad médica', priority: 'ALTA' },
  { name: 'No prescribir sin diagnóstico', category: 'regla', rationale: 'Seguridad', priority: 'ALTA' },
  
  { name: 'CitaCreada', category: 'evento', rationale: 'Nuevo agendamiento', priority: 'ALTA' },
  { name: 'RecetaEmitida', category: 'evento', rationale: 'Prescripción generada', priority: 'MEDIA' },
  
  { name: 'Tiempo Espera', category: 'tiempo', rationale: 'Minutos hasta atención', priority: 'ALTA' },
  { name: 'Duración Consulta', category: 'tiempo', rationale: 'Tiempo promedio con médico', priority: 'MEDIA' },
  
  { name: 'HIS', category: 'modulo', rationale: 'Sistema hospitalario', priority: 'ALTA' },
  { name: 'Laboratorio', category: 'modulo', rationale: 'Gestión de estudios', priority: 'MEDIA' },
  
  { name: 'Reducir espera 30%', category: 'objetivo', rationale: 'Optimizar agenda', priority: 'ALTA' },
];

// ============================================================
// REGISTRO COMPLETO DE PATRONES
// ============================================================
export const PATTERNS: Record<string, SystemPattern> = {
  CRM: {
    id: 'CRM',
    display: 'CRM / Ventas',
    backendMappings: ['WEB_B2C'],
    rbac: true,
    description: 'Sistema de gestión de relaciones con clientes y pipeline de ventas',
    items: CRM_ITEMS,
  },
  ERP: {
    id: 'ERP',
    display: 'ERP / Gestión Empresarial',
    backendMappings: ['BATCH_ETL', 'WEB_B2C'],
    rbac: true,
    description: 'Sistema integrado de planificación de recursos empresariales',
    items: ERP_ITEMS,
  },
  POS: {
    id: 'POS',
    display: 'POS / Punto de Venta',
    backendMappings: ['WEB_B2C'],
    rbac: true,
    description: 'Sistema de punto de venta para comercios físicos',
    items: POS_ITEMS,
  },
  ECOMMERCE: {
    id: 'ECOMMERCE',
    display: 'E-Commerce',
    backendMappings: ['WEB_B2C', 'API_PUBLICA'],
    rbac: false,
    description: 'Plataforma de ventas en línea',
    items: ECOMMERCE_ITEMS,
  },
  MANUFACTURA: {
    id: 'MANUFACTURA',
    display: 'Manufactura',
    backendMappings: ['BATCH_ETL', 'TIEMPO_REAL_IOT'],
    rbac: true,
    description: 'Sistema de producción y control de calidad',
    items: MANUFACTURA_ITEMS,
  },
  LOGISTICA: {
    id: 'LOGISTICA',
    display: 'Logística / Rastreo',
    backendMappings: ['TIEMPO_REAL_IOT'],
    rbac: true,
    description: 'Sistema de gestión de flotas y rutas de entrega',
    items: LOGISTICA_ITEMS,
  },
  HOSPITALARIO: {
    id: 'HOSPITALARIO',
    display: 'Sistema Hospitalario',
    backendMappings: ['WEB_B2C'],
    rbac: true,
    description: 'Sistema de gestión clínica y administrativa',
    items: HOSPITALARIO_ITEMS,
  },
  RH: {
    id: 'RH',
    display: 'Recursos Humanos',
    backendMappings: ['DASHBOARD_INTERNO'],
    rbac: true,
    description: 'Sistema de gestión de personal, nómina y desarrollo',
    items: [
      { name: 'Empleado', category: 'actor', rationale: 'Gestiona su perfil y solicitudes', priority: 'ALTA' },
      { name: 'RH', category: 'actor', rationale: 'Administra contrataciones y nómina', priority: 'ALTA' },
      { name: 'Gerente', category: 'actor', rationale: 'Aprueba vacaciones y evaluaciones', priority: 'ALTA' },
      { name: 'Puesto', category: 'objeto', rationale: 'Posición organizacional', priority: 'ALTA' },
      { name: 'SolicitudVacaciones', category: 'objeto', rationale: 'Petición de días libres', priority: 'ALTA' },
      { name: 'EvaluaciónDesempeño', category: 'objeto', rationale: 'Review periódica', priority: 'MEDIA' },
      { name: 'Contratar', category: 'operacion', rationale: 'Proceso de selección', priority: 'ALTA' },
      { name: 'GenerarNómina', category: 'operacion', rationale: 'Cálculo de sueldos', priority: 'ALTA' },
      { name: 'No contratar sin vacante aprobada', category: 'regla', rationale: 'Control presupuestal', priority: 'ALTA' },
      { name: 'SLA Nómina', category: 'tiempo', rationale: 'Días para pago', priority: 'ALTA' },
      { name: 'Reducir rotación 25%', category: 'objetivo', rationale: 'Retención de talento', priority: 'ALTA' },
    ],
  },
  IA_MULTIAGENTE: {
    id: 'IA_MULTIAGENTE',
    display: 'IA Multiagente',
    backendMappings: ['API_PUBLICA', 'TIEMPO_REAL_IOT'],
    rbac: true,
    description: 'Sistema de agentes autónomos colaborativos',
    items: [
      { name: 'Agente', category: 'actor', rationale: 'Entidad autónoma', priority: 'ALTA' },
      { name: 'Coordinador', category: 'actor', rationale: 'Orquesta agentes', priority: 'ALTA' },
      { name: 'Usuario', category: 'actor', rationale: 'Interactúa con el sistema', priority: 'ALTA' },
      { name: 'Tarea', category: 'objeto', rationale: 'Unidad de trabajo asignada', priority: 'ALTA' },
      { name: 'Mensaje', category: 'objeto', rationale: 'Comunicación entre agentes', priority: 'ALTA' },
      { name: 'DelegarTarea', category: 'operacion', rationale: 'Asignar trabajo a agente', priority: 'ALTA' },
      { name: 'ResolverColaborativo', category: 'operacion', rationale: 'Múltiples agentes en paralelo', priority: 'ALTA' },
      { name: 'No tener conflictos sin resolver', category: 'regla', rationale: 'Consistencia', priority: 'ALTA' },
      { name: 'TareaCompletada', category: 'evento', rationale: 'Agente finalizó trabajo', priority: 'ALTA' },
    ],
  },
  IOT: {
    id: 'IOT',
    display: 'IoT / Sensores',
    backendMappings: ['TIEMPO_REAL_IOT'],
    rbac: true,
    description: 'Sistema de telemetría y control remoto',
    items: [
      { name: 'Sensor', category: 'actor', rationale: 'Dispositivo que captura datos', priority: 'ALTA' },
      { name: 'Operador', category: 'actor', rationale: 'Monitorea dashboards', priority: 'ALTA' },
      { name: 'Dispositivo', category: 'objeto', rationale: 'Hardware conectado', priority: 'ALTA' },
      { name: 'Lectura', category: 'objeto', rationale: 'Medición capturada', priority: 'ALTA' },
      { name: 'Alerta', category: 'objeto', rationale: 'Evento fuera de umbral', priority: 'ALTA' },
      { name: 'EnviarLectura', category: 'operacion', rationale: 'Publicar medición', priority: 'ALTA' },
      { name: 'No operar sin conectividad', category: 'regla', rationale: 'Buffer local', priority: 'ALTA' },
      { name: 'LecturaRecibida', category: 'evento', rationale: 'Nuevo dato', priority: 'ALTA' },
      { name: 'UmbralExcedido', category: 'evento', rationale: 'Alerta generada', priority: 'ALTA' },
      { name: 'Latencia Máxima', category: 'tiempo', rationale: 'Segundos de retardo', priority: 'ALTA' },
      { name: 'Reducir latencia a 100ms', category: 'objetivo', rationale: 'Tiempo real', priority: 'ALTA' },
    ],
  },
  FINTECH: {
    id: 'FINTECH',
    display: 'Fintech / Pagos',
    backendMappings: ['API_PUBLICA'],
    rbac: true,
    description: 'Sistema de pagos y transacciones financieras',
    items: [
      { name: 'Cliente', category: 'actor', rationale: 'Realiza pagos', priority: 'ALTA' },
      { name: 'Comercio', category: 'actor', rationale: 'Recibe pagos', priority: 'ALTA' },
      { name: 'Auditor', category: 'actor', rationale: 'Revisa compliance', priority: 'ALTA' },
      { name: 'Transacción', category: 'objeto', rationale: 'Movimiento financiero', priority: 'ALTA' },
      { name: 'Tarjeta', category: 'objeto', rationale: 'Instrumento de pago', priority: 'ALTA' },
      { name: 'Reembolso', category: 'objeto', rationale: 'Devolución de dinero', priority: 'MEDIA' },
      { name: 'ProcesarPago', category: 'operacion', rationale: 'Ejecutar transacción', priority: 'ALTA' },
      { name: 'ValidarAML', category: 'operacion', rationale: 'Anti-lavado', priority: 'ALTA' },
      { name: 'No procesar sin 3DS', category: 'regla', rationale: 'Seguridad PCI', priority: 'ALTA' },
      { name: 'PagoAprobado', category: 'evento', rationale: 'Transacción exitosa', priority: 'ALTA' },
      { name: 'FraudeDetectado', category: 'evento', rationale: 'Alerta de riesgo', priority: 'ALTA' },
      { name: 'SLA Procesamiento', category: 'tiempo', rationale: 'Segundos máximo', priority: 'ALTA' },
      { name: 'Gateway Pagos', category: 'comunicacion', rationale: 'Conexión con banco', priority: 'ALTA' },
      { name: 'Reducir fraudes 50%', category: 'objetivo', rationale: 'Seguridad', priority: 'ALTA' },
    ],
  },
  SAAS: {
    id: 'SAAS',
    display: 'SaaS Multitenant',
    backendMappings: ['API_PUBLICA', 'WEB_B2C'],
    rbac: true,
    description: 'Software como servicio con múltiples inquilinos',
    items: [
      { name: 'AdminGlobal', category: 'actor', rationale: 'Gestiona todos los tenants', priority: 'ALTA' },
      { name: 'AdminTenant', category: 'actor', rationale: 'Configura su organización', priority: 'ALTA' },
      { name: 'Usuario', category: 'actor', rationale: 'Usa funcionalidad del SaaS', priority: 'ALTA' },
      { name: 'Tenant', category: 'objeto', rationale: 'Cliente del SaaS', priority: 'ALTA' },
      { name: 'Plan', category: 'objeto', rationale: 'Suscripción con límites', priority: 'ALTA' },
      { name: 'Suscripción', category: 'objeto', rationale: 'Relación cliente-plan', priority: 'ALTA' },
      { name: 'CrearTenant', category: 'operacion', rationale: 'Alta de cliente', priority: 'ALTA' },
      { name: 'CambiarPlan', category: 'operacion', rationale: 'Upgrade/downgrade', priority: 'ALTA' },
      { name: 'No compartir datos entre tenants', category: 'regla', rationale: 'Aislamiento', priority: 'ALTA' },
      { name: 'TenantCreado', category: 'evento', rationale: 'Nuevo cliente', priority: 'ALTA' },
      { name: 'SuscripciónVencida', category: 'evento', rationale: 'Pago no realizado', priority: 'ALTA' },
      { name: 'Isolation Pool', category: 'espacio', rationale: 'Separación de datos', priority: 'ALTA' },
      { name: 'Billing', category: 'modulo', rationale: 'Gestión de pagos', priority: 'ALTA' },
      { name: 'Reducir churn 20%', category: 'objetivo', rationale: 'Retención', priority: 'ALTA' },
    ],
  },
  CUSTOM: {
    id: 'CUSTOM',
    display: 'Personalizado',
    backendMappings: [],
    rbac: false,
    description: 'Sistema personalizado - los items se detectan en entrevista',
    items: [],
  },
};

// ============================================================
// UTILIDADES EXPORTADAS
// ============================================================
export const BACKEND_TYPES: Record<string, SystemPattern> = {};

export function getPatternById(id: string): SystemPattern | undefined {
  return PATTERNS[id];
}

export function getAllPatterns(): SystemPattern[] {
  return Object.values(PATTERNS);
}

export function getItemsByCategory(pattern: SystemPattern, category: ProposalCategory): PatternItem[] {
  return pattern.items.filter(item => item.category === category);
}

export function getMissingItems(pattern: SystemPattern, existingItems: string[]): PatternItem[] {
  return pattern.items.filter(item => !existingItems.includes(item.name));
}

// Helper para obtener solo items de una fase específica
export function getItemsForPhase(pattern: SystemPattern, fase: string): PatternItem[] {
  const phaseCategoryMap: Record<string, ProposalCategory[]> = {
    FASE_0: ['actor'],
    FASE_1: ['objeto'],
    FASE_2: ['operacion'],
    FASE_3: ['estado'],
    FASE_3B: ['relacion'],
    FASE_4: ['regla'],
    FASE_5: ['evento'],
    FASE_6: ['tiempo'],
    FASE_7: ['recurso'],
    FASE_7B: ['espacio'],
    FASE_7C: ['comunicacion'],
    FASE_8: ['modulo',], 
    //FASE_8:['inferencia'],
    FASE_8B: ['objetivo'],
  };
  
  const categories = phaseCategoryMap[fase] || [];
  return pattern.items.filter(item => categories.includes(item.category));
}