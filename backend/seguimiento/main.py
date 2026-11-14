"""
Módulo 5 — Seguimiento de Entregas y Transportadoras
API REST con FastAPI — Equipo 5 (integración con Módulos 3 y 6)
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
 SeguimientoCreate,
 ActualizarEstadoInput,
 EntregarInput,
 PQRInput,
)
import services
from database import get_db

# App 

app = FastAPI(
 title="Módulo 5 — Seguimiento de Entregas",
 description=(
 "API REST para el seguimiento de envíos del Marketplace USC. "
 "Interopera con Módulo 3 (Notificaciones) y Módulo 6 (Contabilidad/Escrow)."
 ),
 version="1.0.0",
 docs_url="/docs",
 redoc_url="/redoc",
)

app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

# Health 

@app.get("/health", tags=["Sistema"])
def health_check():
 supabase_ok = False
 try:
 db = get_db()
 db.table("ent_seguimientos").select("id").limit(1).execute()
 supabase_ok = True
 except Exception:
 pass
 return {
 "status": "healthy" if supabase_ok else "degraded",
 "service": "seguimiento_entregas",
 "team": "Equipo 5",
 "version": "1.0.0",
 "supabase_connected": supabase_ok,
 }

# Crear seguimiento 

@app.post("/api/seguimiento/crear", tags=["Seguimiento"])
def crear_seguimiento(data: SeguimientoCreate):
 """
 Crea un nuevo seguimiento de envío para un pedido.
 **Llama Equipo 1** al confirmar el pedido y necesitar un número de guía.
 """
 try:
 seguimiento = services.crear_seguimiento(data)
 return {"success": True, "data": seguimiento}
 except Exception as exc:
 raise HTTPException(status_code=400, detail=str(exc))

# Consultas 

@app.get("/api/seguimiento/pedido/{pedido_id}", tags=["Seguimiento"])
def seguimiento_por_pedido(pedido_id: str):
 """Obtiene el seguimiento de un pedido específico."""
 result = services.obtener_por_pedido(pedido_id)
 if not result:
 raise HTTPException(status_code=404, detail=f"No hay seguimiento para el pedido {pedido_id}")
 return {"success": True, "data": result}

@app.get("/api/seguimiento", tags=["Seguimiento"])
def seguimiento_por_guia(numero_guia: str = Query(..., description="Número de guía de la transportadora")):
 """Consulta el estado de un envío por número de guía (uso del comprador en frontend)."""
 result = services.obtener_por_guia(numero_guia)
 if not result:
 raise HTTPException(status_code=404, detail=f"Guía '{numero_guia}' no encontrada")
 return {"success": True, "data": result}

@app.get("/api/seguimiento/comprador/{comprador_id}", tags=["Seguimiento"])
def seguimientos_por_comprador(comprador_id: str):
 """Lista todos los envíos de un comprador."""
 return {"success": True, "data": services.listar_por_comprador(comprador_id)}

@app.get("/api/seguimiento/vendedor/{vendedor_id}", tags=["Seguimiento"])
def seguimientos_por_vendedor(vendedor_id: str):
 """Lista todos los envíos de un vendedor."""
 return {"success": True, "data": services.listar_por_vendedor(vendedor_id)}

# Actualizar estado 

@app.put("/api/seguimiento/{numero_guia}/estado", tags=["Seguimiento"])
async def actualizar_estado(numero_guia: str, entrada: ActualizarEstadoInput):
 """
 Actualiza el estado del envío.
 Al pasar a EN_TRANSITO o EN_DESTINO se envía notificación automática al comprador.
 """
 try:
 result = await services.actualizar_estado(numero_guia, entrada)
 return {"success": True, "data": result}
 except LookupError as exc:
 raise HTTPException(status_code=404, detail=str(exc))
 except ValueError as exc:
 raise HTTPException(status_code=422, detail=str(exc))
 except Exception as exc:
 raise HTTPException(status_code=500, detail=str(exc))

# Registrar entrega 

@app.post("/api/seguimiento/{numero_guia}/entregar", tags=["Seguimiento"])
async def registrar_entrega(numero_guia: str, entrada: EntregarInput):
 """
 Registra la entrega exitosa del pedido.
 - Guarda evidencia fotográfica
 - Notifica al comprador (Módulo 3)
 - Inicia conteo de 72h para liberar escrow (Módulo 6)
 """
 try:
 result = await services.registrar_entrega(numero_guia, entrada)
 return {"success": True, "message": "Entrega registrada exitosamente", "data": result}
 except LookupError as exc:
 raise HTTPException(status_code=404, detail=str(exc))
 except Exception as exc:
 raise HTTPException(status_code=500, detail=str(exc))

# PQR 

@app.post("/api/seguimiento/{numero_guia}/pqr", tags=["PQR"])
async def registrar_pqr(numero_guia: str, entrada: PQRInput):
 """
 Registra una PQR (Petición, Queja o Reclamo) por un envío.
 - Tipos: PERDIDA | DANO | RETRASO | ENTREGA_INCORRECTA | OTRO
 - Congela el escrow en Módulo 6
 - Notifica a comprador y vendedor vía Módulo 3
 """
 try:
 result = await services.registrar_pqr(numero_guia, entrada)
 return {"success": True, "data": result}
 except LookupError as exc:
 raise HTTPException(status_code=404, detail=str(exc))
 except Exception as exc:
 raise HTTPException(status_code=500, detail=str(exc))

# Endpoint raíz 

@app.get("/", tags=["Sistema"])
def root():
 return {
 "servicio": "Módulo 5 - Seguimiento de Entregas",
 "equipo": "Equipo 5",
 "docs": "/docs",
 "health": "/health",
 }
