from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from schemas import NotificacionCreate, NotificacionResponse, UnreadCountResponse
from services import NotificacionesService
from config import settings

app = FastAPI(
 title="Marketplace USC - Servicio de Notificaciones (Equipo 3)",
 description="Microservicio REST para gestión y despacho de avisos automáticos derivados de eventos de compras, pagos y logística.",
 version="1.0.0"
)

# Habilitar CORS para conectar con el Frontend
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
 "service": "notificaciones",
 "team": "Equipo 3",
 "database": "Supabase PostgreSQL (notif_mensajes)"
 }

@app.post(
 "/api/notificaciones",
 response_model=NotificacionResponse,
 status_code=status.HTTP_201_CREATED,
 tags=["Notificaciones"]
)
def crear_notificacion(payload: NotificacionCreate):
 """
 Crea una nueva notificación.
 Invocado por otros microservicios (Órdenes, Pasarela de Pago, Envíos, Contabilidad)
 ante eventos de negocio.
 """
 try:
 nueva = NotificacionesService.crear_notificacion(payload)
 if not nueva:
 raise HTTPException(status_code=500, detail="No se pudo registrar la notificación en la base de datos.")
 return nueva
 except Exception as e:
 raise HTTPException(status_code=400, detail=str(e))

@app.get(
 "/api/notificaciones/usuario/{usuario_id}",
 response_model=List[NotificacionResponse],
 tags=["Notificaciones"]
)
def listar_notificaciones(
 usuario_id: str,
 limit: int = Query(50, ge=1, le=100),
 solo_no_leidas: bool = False
):
 """
 Obtiene el listado cronológico de notificaciones de un usuario específico.
 """
 try:
 return NotificacionesService.listar_por_usuario(usuario_id, limit, solo_no_leidas)
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.get(
 "/api/notificaciones/usuario/{usuario_id}/no-leidas/conteo",
 response_model=UnreadCountResponse,
 tags=["Notificaciones"]
)
def contar_no_leidas(usuario_id: str):
 """
 Retorna la cantidad de notificaciones sin leer para badges en la UI.
 """
 try:
 count = NotificacionesService.contar_no_leidas(usuario_id)
 return {"usuario_id": usuario_id, "no_leidas": count}
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.put(
 "/api/notificaciones/{notificacion_id}/leer",
 response_model=NotificacionResponse,
 tags=["Notificaciones"]
)
def marcar_como_leida(notificacion_id: str):
 """
 Marca un aviso individual como leído.
 """
 try:
 updated = NotificacionesService.marcar_como_leida(notificacion_id)
 if not updated:
 raise HTTPException(status_code=404, detail="Notificación no encontrada.")
 return updated
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.put(
 "/api/notificaciones/usuario/{usuario_id}/leer-todas",
 tags=["Notificaciones"]
)
def marcar_todas_leidas(usuario_id: str):
 """
 Marca todas las notificaciones pendientes de un usuario como leídas.
 """
 try:
 NotificacionesService.marcar_todas_leidas(usuario_id)
 return {"message": "Todas las notificaciones fueron marcadas como leídas."}
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
 import uvicorn
 uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
