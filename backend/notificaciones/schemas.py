from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoNotificacion(str, Enum):
 ORDEN_CREADA = "ORDEN_CREADA"
 PAGO_APROBADO = "PAGO_APROBADO"
 PAGO_RECHAZADO = "PAGO_RECHAZADO"
 ENVIO_EN_TRANSITO = "ENVIO_EN_TRANSITO"
 ENVIO_ENTREGADO = "ENVIO_ENTREGADO"
 STOCK_BAJO = "STOCK_BAJO"
 DEVOLUCION_SOLICITADA = "DEVOLUCION_SOLICITADA"
 REEMBOLSO_PROCESADO = "REEMBOLSO_PROCESADO"
 ESCROW_LIBERADO = "ESCROW_LIBERADO"
 INCIDENCIA_PQR = "INCIDENCIA_PQR"
 SISTEMA_INFO = "SISTEMA_INFO"

class NotificacionCreate(BaseModel):
 usuario_id: str = Field(..., description="UUID del usuario destinatario")
 tipo: TipoNotificacion = Field(..., description="Tipo o categoría del evento")
 titulo: str = Field(..., max_length=200, description="Título breve del aviso")
 mensaje: str = Field(..., description="Cuerpo explicativo de la notificación")
 referencia_id: Optional[str] = Field(None, description="ID del pedido o recurso asociado")
 referencia_tipo: Optional[str] = Field("ORDEN", description="Entidad vinculada")

class NotificacionResponse(BaseModel):
 id: str
 usuario_id: str
 tipo: str
 titulo: str
 mensaje: str
 referencia_id: Optional[str] = None
 referencia_tipo: Optional[str] = None
 leido: bool
 creado_en: datetime
 leido_en: Optional[datetime] = None

class UnreadCountResponse(BaseModel):
 usuario_id: str
 no_leidas: int
