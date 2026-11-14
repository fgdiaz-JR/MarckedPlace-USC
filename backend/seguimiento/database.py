"""
Módulo 5 — Seguimiento de Entregas
Conexión a Supabase (proyecto propio del equipo 5)
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "SUPABASE_URL y SUPABASE_KEY deben estar configurados en las variables de entorno."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

