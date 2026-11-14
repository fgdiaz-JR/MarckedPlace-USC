"""
Módulo 5 — Seguimiento de Entregas
Configuración cargada desde variables de entorno (Render / .env)
"""
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

URL_CONTABILIDAD: str = os.getenv(
 "URL_CONTABILIDAD",
 "https://marketplace-usc-contabilidad.onrender.com/api"
)
URL_NOTIFICACIONES: str = os.getenv(
 "URL_NOTIFICACIONES",
 "https://marketplace-usc-notificaciones.onrender.com/api"
)

JWT_JWKS_URL: str = os.getenv(
 "JWT_JWKS_URL",
 "https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json"
)

# Estados válidos del ciclo de vida de un envío
ESTADOS_VALIDOS = [
 "PENDIENTE",
 "RECOGIDO",
 "EN_TRANSITO",
 "EN_DESTINO",
 "ENTREGADO",
 "FALLIDO",
 "DEVOLUCION",
]
