from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoEscrow(str, Enum):
    RETENIDO = "RETENIDO"
    LIBERADO = "LIBERADO"
    BLOQUEADO_PQR = "BLOQUEADO_PQR"
    REEMBOLSADO = "REEMBOLSADO"

class MotivoLiberacion(str, Enum):
    EXPIRACION_72H = "72_HORAS_EXPIRADAS"
    CONFORMIDAD_CLIENTE = "CONFORMIDAD_CLIENTE"
    MANUAL_ADMIN = "MANUAL_ADMIN"

class EscrowCreate(BaseModel):
    pedido_id: str = Field(..., description="UUID de la orden de pedido")
    vendedor_id: str = Field(..., description="UUID del vendedor titular")
    comprador_id: str = Field(..., description="UUID del comprador")
    monto_bruto: float = Field(..., ge=0, description="Valor total pagado por el comprador en COP")

class EscrowResponse(BaseModel):
    id: str
    pedido_id: str
    vendedor_id: str
    comprador_id: str
    monto_bruto: float
    porcentaje_comision: float
    comision_plataforma: float
    monto_neto_vendedor: float
    estado_escrow: str
    motivo_liberacion: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    fecha_limite_liberacion: Optional[datetime] = None
    fecha_liberacion_real: Optional[datetime] = None
    creado_en: datetime

class LiberarEscrowRequest(BaseModel):
    motivo: MotivoLiberacion = Field(default=MotivoLiberacion.CONFORMIDAD_CLIENTE)
    observaciones: Optional[str] = None

class BloquearEscrowRequest(BaseModel):
    razon_pqr: str = Field(..., min_length=5, description="Motivo de la incidencia PQR que congela los fondos")

class ResumenFinancieroAdmin(BaseModel):
    total_ventas_brutas: float
    total_comisiones_5pct: float
    total_en_custodia_retenido: float
    total_liberado_vendedores: float
    total_bloqueado_pqr: float
    cantidad_ordenes_escrow: int

class BalanceVendedorResponse(BaseModel):
    vendedor_id: str
    saldo_disponible: float
    saldo_en_custodia: float
    total_ventas_brutas: float
    total_comisiones_pagadas: float

