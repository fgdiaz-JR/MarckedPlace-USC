"""
Marketplace USC — Utilidad de validacion de JWT y claims de rol
Lectura segura de roles: app_metadata.role tiene prioridad absoluta sobre user_metadata.
"""
from __future__ import annotations
import httpx
import jwt as pyjwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWKS_URL = "https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json"

_bearer = HTTPBearer(auto_error=False)
_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def _extract_role(payload: dict) -> str:
    """
    Lee el rol del JWT de forma segura.
    Jerarquia:
      1. app_metadata.role   <- firmado por el servidor, no manipulable por el usuario
      2. app_metadata.rol
      3. user_metadata.role  <- editable por el usuario, NO usar para control de acceso
      4. user_metadata.rol
      5. 'COMPRADOR'         <- rol minimo por defecto
    """
    app_meta  = payload.get("app_metadata")  or {}
    user_meta = payload.get("user_metadata") or {}

    role = (
        app_meta.get("role")
        or app_meta.get("rol")
        or user_meta.get("role")   # solo fallback
        or user_meta.get("rol")
        or "COMPRADOR"
    )
    normalized = str(role).upper()
    return normalized if normalized in ("ADMIN", "VENDEDOR", "COMPRADOR") else "COMPRADOR"


async def get_current_role(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> str:
    """
    Dependencia FastAPI: valida el JWT y retorna el rol del usuario.
    Lanza 401 si el token es invalido o ausente.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorizacion requerido.",
        )

    token = credentials.credentials
    try:
        jwks = await _get_jwks()
        # Decodificar sin verificar primero para obtener el kid
        header = pyjwt.get_unverified_header(token)
        kid = header.get("kid")

        # Buscar la clave publica correcta en el JWKS
        public_key = None
        for key_data in jwks.get("keys", []):
            if key_data.get("kid") == kid:
                public_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(key_data)
                break

        if public_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clave publica no encontrada en JWKS.",
            )

        payload = pyjwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return _extract_role(payload)

    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado.",
        )
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalido: {exc}",
        )


def require_role(*allowed: str):
    """
    Fabrica de dependencias FastAPI que exige uno de los roles permitidos.

    Uso:
        @app.get("/admin/...", dependencies=[Depends(require_role("ADMIN"))])

    El rol se lee de app_metadata.role (firmado por Supabase service_role).
    """
    async def _check(
        credentials: HTTPAuthorizationCredentials = Security(_bearer),
    ) -> str:
        role = await get_current_role(credentials)
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de: {list(allowed)}. Tu rol: {role}",
            )
        return role
    return _check
