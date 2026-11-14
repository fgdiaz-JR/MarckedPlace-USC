"""
Módulo 5 — Seguimiento de Entregas
Lógica de negocio: crear seguimiento, actualizar estado, interop con Módulos 3 y 6
"""
from __future__ import annotations
import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from config import URL_CONTABILIDAD, URL_NOTIFICACIONES, ESTADOS_VALIDOS
from schemas import SeguimientoCreate, ActualizarEstadoInput, EntregarInput, PQRInput

# Helpers HTTP 

async def _notify(tipo: str, destinatario_id: str, titulo: str, mensaje: str, referencia_id: str):
 """Envía una notificación al Módulo 3 (Notificaciones)."""
 try:
 payload = {
 "tipo": tipo,
 "destinatario_id": destinatario_id,
 "titulo": titulo,
 "mensaje": mensaje,
 "referencia_id": referencia_id,
 }
 async with httpx.AsyncClient(timeout=10.0) as client:
 await client.post(f"{URL_NOTIFICACIONES}/notificaciones", json=payload)
 except Exception as exc:
 print(f"[WARN] No se pudo notificar al Módulo 3: {exc}")

async def _escrow_marcar_entrega(pedido_id: str):
 """Informa al Módulo 6 que el pedido fue entregado (inicia conteo 72h para liberar escrow)."""
 try:
 async with httpx.AsyncClient(timeout=10.0) as client:
 await client.post(
 f"{URL_CONTABILIDAD}/contabilidad/escrow/marcar-entrega/{pedido_id}"
 )
 except Exception as exc:
 print(f"[WARN] No se pudo marcar entrega en Módulo 6: {exc}")

async def _escrow_bloquear(pedido_id: str, motivo: str):
 """Bloquea el escrow en el Módulo 6 ante un PQR."""
 try:
 async with httpx.AsyncClient(timeout=10.0) as client:
 await client.post(
 f"{URL_CONTABILIDAD}/contabilidad/escrow/bloquear/{pedido_id}",
 json={"motivo": motivo},
 )
 except Exception as exc:
 print(f"[WARN] No se pudo bloquear escrow en Módulo 6: {exc}")

# CRUD Seguimiento 

def crear_seguimiento(data: SeguimientoCreate) -> dict:
 db = get_db()
 numero_guia = data.numero_guia or f"USC-{uuid.uuid4().hex[:8].upper()}"
 fecha_estimada = datetime.utcnow() + timedelta(days=5)

 row = {
 "pedido_id": data.pedido_id,
 "vendedor_id": data.vendedor_id,
 "comprador_id": data.comprador_id,
 "numero_guia": numero_guia,
 "transportadora": data.transportadora or "COORDINADORA",
 "estado": "PENDIENTE",
 "origen": data.origen,
 "destino": data.destino,
 "direccion_entrega": data.direccion_entrega,
 "peso_kg": data.peso_kg,
 "valor_declarado": data.valor_declarado,
 "fecha_estimada_entrega": fecha_estimada.isoformat(),
 "observaciones": data.observaciones,
 }

 result = db.table("ent_seguimientos").insert(row).execute()
 seguimiento = result.data[0] if result.data else row
 return seguimiento

def obtener_por_pedido(pedido_id: str) -> dict | None:
 db = get_db()
 result = (
 db.table("ent_seguimientos")
 .select("*")
 .eq("pedido_id", pedido_id)
 .order("created_at", desc=True)
 .limit(1)
 .execute()
 )
 return result.data[0] if result.data else None

def obtener_por_guia(numero_guia: str) -> dict | None:
 db = get_db()
 result = (
 db.table("ent_seguimientos")
 .select("*")
 .eq("numero_guia", numero_guia)
 .execute()
 )
 return result.data[0] if result.data else None

def listar_por_comprador(comprador_id: str) -> list:
 db = get_db()
 result = (
 db.table("ent_seguimientos")
 .select("*")
 .eq("comprador_id", comprador_id)
 .order("created_at", desc=True)
 .execute()
 )
 return result.data or []

def listar_por_vendedor(vendedor_id: str) -> list:
 db = get_db()
 result = (
 db.table("ent_seguimientos")
 .select("*")
 .eq("vendedor_id", vendedor_id)
 .order("created_at", desc=True)
 .execute()
 )
 return result.data or []

async def actualizar_estado(numero_guia: str, entrada: ActualizarEstadoInput) -> dict:
 db = get_db()

 if entrada.estado not in ESTADOS_VALIDOS:
 raise ValueError(
 f"Estado '{entrada.estado}' no válido. Válidos: {', '.join(ESTADOS_VALIDOS)}"
 )

 seguimiento = obtener_por_guia(numero_guia)
 if not seguimiento:
 raise LookupError(f"No se encontró seguimiento con guía {numero_guia}")

 updates: dict = {
 "estado": entrada.estado,
 "updated_at": datetime.utcnow().isoformat(),
 }
 if entrada.ubicacion_actual:
 updates["ubicacion_actual"] = entrada.ubicacion_actual
 if entrada.observaciones:
 updates["observaciones"] = entrada.observaciones

 result = (
 db.table("ent_seguimientos")
 .update(updates)
 .eq("numero_guia", numero_guia)
 .execute()
 )

 # Notificaciones automáticas
 if entrada.estado == "EN_TRANSITO":
 await _notify(
 tipo="ENVIO",
 destinatario_id=seguimiento["comprador_id"],
 titulo="Tu pedido está en camino ",
 mensaje=f"Tu pedido (guía {numero_guia}) ya está en tránsito hacia {seguimiento['destino']}.",
 referencia_id=seguimiento["pedido_id"],
 )
 elif entrada.estado == "EN_DESTINO":
 await _notify(
 tipo="ENVIO",
 destinatario_id=seguimiento["comprador_id"],
 titulo="Tu pedido llegó a tu ciudad ",
 mensaje=f"Tu pedido (guía {numero_guia}) está en destino. La entrega se realizará pronto.",
 referencia_id=seguimiento["pedido_id"],
 )

 return result.data[0] if result.data else updates

async def registrar_entrega(numero_guia: str, entrada: EntregarInput) -> dict:
 db = get_db()

 seguimiento = obtener_por_guia(numero_guia)
 if not seguimiento:
 raise LookupError(f"No se encontró seguimiento con guía {numero_guia}")

 updates = {
 "estado": "ENTREGADO",
 "fecha_entrega_real": datetime.utcnow().isoformat(),
 "receptor_nombre": entrada.receptor_nombre,
 "receptor_documento": entrada.receptor_documento,
 "observaciones": entrada.observaciones,
 "updated_at": datetime.utcnow().isoformat(),
 }

 db.table("ent_seguimientos").update(updates).eq("numero_guia", numero_guia).execute()

 # Guardar evidencia fotográfica
 if entrada.foto_evidencia_url:
 db.table("ent_evidencias").insert({
 "seguimiento_id": seguimiento["id"],
 "tipo_evidencia": "FOTO_ENTREGA",
 "url_archivo": entrada.foto_evidencia_url,
 "descripcion": f"Entrega a {entrada.receptor_nombre or 'receptor desconocido'}",
 }).execute()

 # Notificar al comprador
 await _notify(
 tipo="ENVIO",
 destinatario_id=seguimiento["comprador_id"],
 titulo="¡Tu pedido fue entregado! ",
 mensaje=(
 f"Tu pedido (guía {numero_guia}) fue entregado exitosamente"
 + (f" a {entrada.receptor_nombre}" if entrada.receptor_nombre else "")
 + ". Tienes 72 horas para reportar cualquier inconveniente."
 ),
 referencia_id=seguimiento["pedido_id"],
 )

 # Informar al Módulo 6 para iniciar conteo de liberación de escrow (72h)
 await _escrow_marcar_entrega(seguimiento["pedido_id"])

 seguimiento.update(updates)
 return seguimiento

async def registrar_pqr(numero_guia: str, entrada: PQRInput) -> dict:
 db = get_db()

 seguimiento = obtener_por_guia(numero_guia)
 if not seguimiento:
 raise LookupError(f"No se encontró seguimiento con guía {numero_guia}")

 # Guardar evidencia del PQR
 db.table("ent_evidencias").insert({
 "seguimiento_id": seguimiento["id"],
 "tipo_evidencia": f"PQR_{entrada.tipo_pqr}",
 "url_archivo": entrada.evidencia_url,
 "descripcion": entrada.descripcion,
 }).execute()

 # Actualizar estado a FALLIDO si aplica
 if entrada.tipo_pqr in ("PERDIDA", "DANO", "ENTREGA_INCORRECTA"):
 db.table("ent_seguimientos").update(
 {"estado": "FALLIDO", "updated_at": datetime.utcnow().isoformat()}
 ).eq("numero_guia", numero_guia).execute()

 # Notificar al comprador
 await _notify(
 tipo="PQR",
 destinatario_id=seguimiento["comprador_id"],
 titulo=f"PQR registrada: {entrada.tipo_pqr}",
 mensaje=f"Tu PQR fue registrada para el envío {numero_guia}. El equipo la revisará pronto.",
 referencia_id=seguimiento["pedido_id"],
 )

 # Notificar al vendedor
 await _notify(
 tipo="PQR",
 destinatario_id=seguimiento["vendedor_id"],
 titulo=f"PQR de tu envío: {entrada.tipo_pqr}",
 mensaje=f"El comprador reportó una PQR ({entrada.tipo_pqr}) en el envío {numero_guia}.",
 referencia_id=seguimiento["pedido_id"],
 )

 # Bloquear escrow en Módulo 6
 await _escrow_bloquear(seguimiento["pedido_id"], f"PQR_{entrada.tipo_pqr}: {entrada.descripcion[:200]}")

 return {
 "pedido_id": seguimiento["pedido_id"],
 "numero_guia": numero_guia,
 "pqr_tipo": entrada.tipo_pqr,
 "mensaje": "PQR registrada. Escrow congelado hasta resolución.",
 }
