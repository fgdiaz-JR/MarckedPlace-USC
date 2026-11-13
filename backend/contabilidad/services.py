from datetime import datetime, timezone, timedelta
from database import get_db
from schemas import EscrowCreate, MotivoLiberacion
from config import settings

class ContabilidadService:
    @staticmethod
    def crear_retencion_escrow(data: EscrowCreate):
        db = get_db()
        pct = settings.PLATFORM_COMMISSION_PERCENT # 5.0%
        comision = round(data.monto_bruto * (pct / 100.0), 2)
        neto = round(data.monto_bruto - comision, 2)

        payload = {
            "pedido_id": data.pedido_id,
            "vendedor_id": data.vendedor_id,
            "comprador_id": data.comprador_id,
            "monto_bruto": data.monto_bruto,
            "porcentaje_comision": pct,
            "comision_plataforma": comision,
            "monto_neto_vendedor": neto,
            "estado_escrow": "RETENIDO"
        }

        res = db.table("cont_escrow").insert(payload).execute()
        escrow = res.data[0] if res.data else None

        # Registrar asiento contable en libro diario
        db.table("cont_movimientos").insert({
            "pedido_id": data.pedido_id,
            "tipo": "VENTA_INGRESO_ESCROW",
            "naturaleza": "CREDITO",
            "monto": data.monto_bruto,
            "saldo_anterior": 0.0,
            "saldo_nuevo": data.monto_bruto,
            "descripcion": f"Retención en custodia Escrow por orden {data.pedido_id} (Neto: ${neto:,.0f}, Comisión 5%: ${comision:,.0f})"
        }).execute()

        return escrow

    @staticmethod
    def marcar_entrega_inicia_72h(pedido_id: str):
        """
        Invocado por el Equipo 5 cuando el repartidor entrega el paquete.
        Calcula fecha_limite_liberacion = now + 72 horas.
        """
        db = get_db()
        now = datetime.now(timezone.utc)
        limite = now + timedelta(hours=settings.ESCROW_EXPIRATION_HOURS)

        res = db.table("cont_escrow").update({
            "fecha_entrega": now.isoformat(),
            "fecha_limite_liberacion": limite.isoformat()
        }).eq("pedido_id", pedido_id).execute()

        return res.data[0] if res.data else None

    @staticmethod
    def liberar_escrow(pedido_id: str, motivo: MotivoLiberacion):
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()

        # Buscar registro
        escrow_res = db.table("cont_escrow").select("*").eq("pedido_id", pedido_id).execute()
        if not escrow_res.data:
            return None

        escrow = escrow_res.data[0]
        if escrow["estado_escrow"] == "LIBERADO":
            return escrow

        # Actualizar estado a LIBERADO
        res = db.table("cont_escrow").update({
            "estado_escrow": "LIBERADO",
            "motivo_liberacion": motivo.value,
            "fecha_liberacion_real": now
        }).eq("pedido_id", pedido_id).execute()

        # Actualizar cuenta contable del vendedor
        vendedor_id = escrow["vendedor_id"]
        neto = escrow["monto_neto_vendedor"]
        comision = escrow["comision_plataforma"]

        # Asiento contable de dispersión
        db.table("cont_movimientos").insert({
            "pedido_id": pedido_id,
            "tipo": "LIBERACION_ESCROW_A_SALDO",
            "naturaleza": "DEBITO",
            "monto": neto,
            "saldo_anterior": 0.0,
            "saldo_nuevo": neto,
            "descripcion": f"Liberación de fondos de custodia a saldo disponible del vendedor {vendedor_id}. Motivo: {motivo.value}"
        }).execute()

        # Asiento contable de la comisión del 5%
        db.table("cont_movimientos").insert({
            "pedido_id": pedido_id,
            "tipo": "COMISION_PLATAFORMA_5PCT",
            "naturaleza": "CREDITO",
            "monto": comision,
            "saldo_anterior": 0.0,
            "saldo_nuevo": comision,
            "descripcion": f"Reconocimiento de ingreso por comisión 5% plataforma sobre orden {pedido_id}"
        }).execute()

        return res.data[0] if res.data else None

    @staticmethod
    def bloquear_escrow_por_pqr(pedido_id: str, razon: str):
        db = get_db()
        res = db.table("cont_escrow").update({
            "estado_escrow": "BLOQUEADO_PQR"
        }).eq("pedido_id", pedido_id).execute()

        db.table("cont_movimientos").insert({
            "pedido_id": pedido_id,
            "tipo": "BLOQUEO_PQR",
            "naturaleza": "DEBITO",
            "monto": 0.0,
            "saldo_anterior": 0.0,
            "saldo_nuevo": 0.0,
            "descripcion": f"Congelamiento preventivo de fondos Escrow en orden {pedido_id}. Razón: {razon}"
        }).execute()

        return res.data[0] if res.data else None

    @staticmethod
    def obtener_resumen_general():
        db = get_db()
        res = db.table("cont_escrow").select("*").execute()
        items = res.data or []

        total_bruto = sum(float(i["monto_bruto"]) for i in items)
        total_comisiones = sum(float(i["comision_plataforma"]) for i in items)
        total_retenido = sum(float(i["monto_neto_vendedor"]) for i in items if i["estado_escrow"] == "RETENIDO")
        total_liberado = sum(float(i["monto_neto_vendedor"]) for i in items if i["estado_escrow"] == "LIBERADO")
        total_bloqueado = sum(float(i["monto_neto_vendedor"]) for i in items if i["estado_escrow"] == "BLOQUEADO_PQR")

        return {
            "total_ventas_brutas": total_bruto,
            "total_comisiones_5pct": total_comisiones,
            "total_en_custodia_retenido": total_retenido,
            "total_liberado_vendedores": total_liberado,
            "total_bloqueado_pqr": total_bloqueado,
            "cantidad_ordenes_escrow": len(items)
        }

    @staticmethod
    def balance_vendedor(vendedor_id: str):
        db = get_db()
        res = db.table("cont_escrow").select("*").eq("vendedor_id", vendedor_id).execute()
        items = res.data or []

        retenido = sum(float(i["monto_neto_vendedor"]) for i in items if i["estado_escrow"] == "RETENIDO")
        liberado = sum(float(i["monto_neto_vendedor"]) for i in items if i["estado_escrow"] == "LIBERADO")
        bruto = sum(float(i["monto_bruto"]) for i in items)
        comisiones = sum(float(i["comision_plataforma"]) for i in items)

        return {
            "vendedor_id": vendedor_id,
            "saldo_disponible": liberado,
            "saldo_en_custodia": retenido,
            "total_ventas_brutas": bruto,
            "total_comisiones_pagadas": comisiones
        }

