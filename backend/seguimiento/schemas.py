"""
Módulo 5 — Seguimiento de Entregas
Schemas Pydantic para validación de datos
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Seguimiento 

class SeguimientoCreate(BaseModel):
 pedido_id: str = Field(..., description="UUID del pedido (Equipo 1)")
 vendedor_id: str = Field(..., description="UUID del vendedor")
 comprador_id: str = Field(..., description="UUID del comprador")
 numero_guia: Optional[str] = Field(None, description="Guía de la transportadora")
 transportadora: Optional[str] = Field(None, description="Nombre de la transportadora")
 origen: str = Field(..., description="Ciudad de origen")
 destino: str = Field(..., description="Ciudad de destino")
 direccion_entrega: str = Field(..., description="Dirección completa de entrega")
 peso_kg: Optional[float] = Field(None, ge=0)
 valor_declarado: Optional[float] = Field(None, ge=0)
 observaciones: Optional[str] = None

class ActualizarEstadoInput(BaseModel):
 estado: str = Field(
 ...,
 description="Nuevo estado: PENDIENTE | RECOGIDO | EN_TRANSITO | EN_DESTINO | ENTREGADO | FALLIDO | DEVOLUCION"
 )
 ubicacion_actual: Optional[str] = None
 observaciones: Optional[str] = None

class EntregarInput(BaseModel):
 foto_evidencia_url: Optional[str] = Field(None, description="URL de la foto de evidencia")
 receptor_nombre: Optional[str] = Field(None, description="Nombre de quien recibe")
 receptor_documento: Optional[str] = Field(None, description="Documento de identidad del receptor")
 observaciones: Optional[str] = None

class PQRInput(BaseModel):
 tipo_pqr: str = Field(
 ...,
 description="Tipo: PERDIDA | DANO | RETRASO | ENTREGA_INCORRECTA | OTRO"
 )
 descripcion: str = Field(..., min_length=10, description="Descripción del incidente")
 evidencia_url: Optional[str] = None

# Evidencias 

class EvidenciaResponse(BaseModel):
 id: str
 seguimiento_id: str
 tipo_evidencia: str
 url_archivo: Optional[str]
 descripcion: Optional[str]
 created_at: datetime

# Respuestas 

class SeguimientoResponse(BaseModel):
 id: str
 pedido_id: str
 vendedor_id: str
 comprador_id: str
 numero_guia: Optional[str]
 transportadora: Optional[str]
 estado: str
 origen: str
 destino: str
 direccion_entrega: str
 peso_kg: Optional[float]
 valor_declarado: Optional[float]
 fecha_estimada_entrega: Optional[datetime]
 fecha_entrega_real: Optional[datetime]
 receptor_nombre: Optional[str]
 receptor_documento: Optional[str]
 observaciones: Optional[str]
 created_at: datetime
 updated_at: Optional[datetime]

class HealthResponse(BaseModel):
 status: str
 service: str
 team: str
 version: str
 supabase_connected: bool

class APIResponse(BaseModel):
 success: bool
 message: str
 data: Optional[dict] = None
