from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from auth_utils import require_role

from schemas import (
 EscrowCreate,
 EscrowResponse,
 LiberarEscrowRequest,
 BloquearEscrowRequest,
 ResumenFinancieroAdmin,
 BalanceVendedorResponse
)
from services import ContabilidadService
from config import settings

app = FastAPI(
 title="Marketplace USC - Servicio de Contabilidad & Escrow (Equipo 6)",
 description="Microservicio REST de tesorería, conciliación contable, cobro de comisiones del 5% y custodia de fondos (Escrow 72h / conformidad).",
 version="1.0.0"
)

# CORS
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

@app.get("/health", tags=["Salud"])
def health_check():
 return {
 "status": "healthy",
 "service": "contabilidad_escrow",
 "team": "Equipo 6",
 "commission_rate": "5.0%",
 "escrow_release_policy": "72h tras entrega o conformidad del comprador",
 "database": "Supabase PostgreSQL (cont_escrow, cont_movimientos, cont_cuentas)"
 }

@app.post(
 "/api/contabilidad/escrow/retener",
 response_model=EscrowResponse,
 status_code=status.HTTP_201_CREATED,
 tags=["Custodia Escrow"]
)
def retener_fondos(payload: EscrowCreate):
 """
 Crea una nueva partida de retención en custodia (Escrow).
 Invocado automáticamente por el Equipo 2 (Pasarela) o Equipo 1 (Órdenes)
 al aprobarse el pago.
 Calcula 5% de comisión para la universidad y 95% para el vendedor.
 """
 try:
 escrow = ContabilidadService.crear_retencion_escrow(payload)
 if not escrow:
 raise HTTPException(status_code=500, detail="Error al asentar retención Escrow en Supabase.")
 return escrow
 except Exception as e:
 raise HTTPException(status_code=400, detail=str(e))

@app.post(
 "/api/contabilidad/escrow/marcar-entrega/{pedido_id}",
 response_model=EscrowResponse,
 tags=["Custodia Escrow"]
)
def marcar_entrega(pedido_id: str):
 """
 Invocado por el Equipo 5 (Seguimiento de Entregas) al registrarse
 la entrega física del pedido. Inicia el reloj de 72 horas para liberación automática.
 """
 try:
 updated = ContabilidadService.marcar_entrega_inicia_72h(pedido_id)
 if not updated:
 raise HTTPException(status_code=404, detail="Orden en custodia no encontrada.")
 return updated
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.post(
 "/api/contabilidad/escrow/liberar/{pedido_id}",
 response_model=EscrowResponse,
 tags=["Custodia Escrow"]
)
def liberar_fondos(pedido_id: str, payload: LiberarEscrowRequest):
 """
 Libera los fondos retenidos a saldo disponible del vendedor.
 Condición: Ocurre a las 72 horas de entregado O cuando el comprador
 indica que no tiene problemas con el pedido (conformidad directa).
 """
 try:
 updated = ContabilidadService.liberar_escrow(pedido_id, payload.motivo)
 if not updated:
 raise HTTPException(status_code=404, detail="Partida de Escrow no encontrada.")
 return updated
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.post(
 "/api/contabilidad/escrow/bloquear/{pedido_id}",
 response_model=EscrowResponse,
 tags=["Custodia Escrow"]
)
def bloquear_fondos(pedido_id: str, payload: BloquearEscrowRequest):
 """
 Congela preventivamente los fondos en custodia debido a un reclamo PQR radicado.
 """
 try:
 updated = ContabilidadService.bloquear_escrow_por_pqr(pedido_id, payload.razon_pqr)
 if not updated:
 raise HTTPException(status_code=404, detail="Partida de Escrow no encontrada.")
 return updated
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.get(
 "/api/contabilidad/resumen-general",
 response_model=ResumenFinancieroAdmin,
 tags=["Reportes Contables"],
 dependencies=[Depends(require_role("ADMIN"))]
)
def obtener_resumen_admin():
 """
 Retorna los totales consolidados para el Administrador.
 PROTEGIDO: requiere claim app_metadata.role = ADMIN en el JWT (firmado por Supabase service_role).
 Ventas brutas, 5% comisiones ganadas, fondos retenidos y liberados.
 """
 try:
 return ContabilidadService.obtener_resumen_general()
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.get(
 "/api/contabilidad/vendedor/{vendedor_id}",
 response_model=BalanceVendedorResponse,
 tags=["Reportes Contables"]
)
def balance_vendedor(vendedor_id: str):
 """
 Retorna el estado de cuenta para un vendedor particular:
 Saldo disponible, saldo en custodia (Escrow) y comisiones pagadas.
 """
 try:
 return ContabilidadService.balance_vendedor(vendedor_id)
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
 import uvicorn
 uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
