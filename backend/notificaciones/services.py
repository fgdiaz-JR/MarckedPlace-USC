from datetime import datetime, timezone
from database import get_db
from schemas import NotificacionCreate

class NotificacionesService:
 @staticmethod
 def crear_notificacion(data: NotificacionCreate):
 db = get_db()
 payload = {
 "usuario_id": data.usuario_id,
 "tipo": data.tipo.value,
 "titulo": data.titulo,
 "mensaje": data.mensaje,
 "referencia_id": data.referencia_id,
 "referencia_tipo": data.referencia_tipo,
 "leido": False
 }
 res = db.table("notif_mensajes").insert(payload).execute()
 return res.data[0] if res.data else None

 @staticmethod
 def listar_por_usuario(usuario_id: str, limit: int = 50, solo_no_leidas: bool = False):
 db = get_db()
 query = db.table("notif_mensajes").select("*").eq("usuario_id", usuario_id)
 if solo_no_leidas:
 query = query.eq("leido", False)
 res = query.order("creado_en", desc=True).limit(limit).execute()
 return res.data or []

 @staticmethod
 def marcar_como_leida(notificacion_id: str):
 db = get_db()
 now = datetime.now(timezone.utc).isoformat()
 res = db.table("notif_mensajes").update({"leido": True, "leido_en": now}).eq("id", notificacion_id).execute()
 return res.data[0] if res.data else None

 @staticmethod
 def marcar_todas_leidas(usuario_id: str):
 db = get_db()
 now = datetime.now(timezone.utc).isoformat()
 res = db.table("notif_mensajes").update({"leido": True, "leido_en": now}).eq("usuario_id", usuario_id).execute()
 return res.data or []

 @staticmethod
 def contar_no_leidas(usuario_id: str) -> int:
 db = get_db()
 res = db.table("notif_mensajes").select("id", count="exact").eq("usuario_id", usuario_id).eq("leido", False).execute()
 return res.count or 0
