"""Microsoft Entra ID SSO — direct OAuth2 (no MSAL dependency).

Uses the standard OAuth2 authorization code flow directly via requests,
bypassing MSAL for reliability with new Entra ID tenants.
"""

from __future__ import annotations

import os
import secrets
import threading
import time
import urllib.parse
from typing import Any

import requests as _requests

TENANT_ID     = os.environ.get("ENTRA_TENANT_ID", "")
TENANT_DOMAIN = os.environ.get("ENTRA_TENANT_DOMAIN", "")
CLIENT_ID     = os.environ.get("ENTRA_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("ENTRA_CLIENT_SECRET", "")
REDIRECT_URI  = os.environ.get("ENTRA_REDIRECT_URI", "http://localhost:8501/")

# Use domain name in authority — more reliable for new tenants than GUID
_TENANT_REF   = TENANT_DOMAIN if TENANT_DOMAIN else TENANT_ID
_BASE         = f"https://login.microsoftonline.com/{_TENANT_REF}/oauth2/v2.0"
_SCOPES       = "openid profile"   # email scope removed — causes issues on some new tenants

_ENTRA_ENABLED = bool(TENANT_ID and CLIENT_ID and CLIENT_SECRET)

# ---- Server-side OAuth state store -------------------------------------------
# Streamlit creates a NEW session when Microsoft redirects back (fresh HTTP GET),
# so st.session_state loses the nonce. We store it server-side instead.
# Key = state nonce, value = creation timestamp. TTL = 10 minutes.
_STATE_STORE: dict[str, float] = {}
_STATE_LOCK  = threading.Lock()
_STATE_TTL   = 600.0  # seconds


def register_state(nonce: str) -> None:
    """Store a state nonce server-side before redirecting to Microsoft."""
    with _STATE_LOCK:
        _STATE_STORE[nonce] = time.monotonic()
        # Evict expired entries so the dict doesn't grow unbounded.
        cutoff = time.monotonic() - _STATE_TTL
        expired = [k for k, v in _STATE_STORE.items() if v < cutoff]
        for k in expired:
            del _STATE_STORE[k]


def consume_state(nonce: str) -> bool:
    """Return True and remove the nonce if it exists and hasn't expired."""
    with _STATE_LOCK:
        ts = _STATE_STORE.pop(nonce, None)
        if ts is None:
            return False
        return time.monotonic() - ts < _STATE_TTL


# ---- JWKS cache ---------------------------------------------------------------
# Microsoft rotates signing keys rarely; caching for 1 hour avoids repeated
# network round-trips while still picking up rotations within a reasonable window.
_JWKS_CLIENT_LOCK = threading.Lock()
_JWKS_CLIENT: Any = None
_JWKS_CLIENT_TS: float = 0.0
_JWKS_TTL = 3600.0  # seconds


def _get_jwks_client() -> Any:
    """Return a cached PyJWKClient, refreshing after _JWKS_TTL seconds."""
    global _JWKS_CLIENT, _JWKS_CLIENT_TS
    now = time.monotonic()
    with _JWKS_CLIENT_LOCK:
        if _JWKS_CLIENT is None or now - _JWKS_CLIENT_TS > _JWKS_TTL:
            from jwt import PyJWKClient  # PyJWT[cryptography]
            jwks_uri = (
                f"https://login.microsoftonline.com/{_TENANT_REF}/discovery/v2.0/keys"
            )
            _JWKS_CLIENT = PyJWKClient(jwks_uri, lifespan=int(_JWKS_TTL))
            _JWKS_CLIENT_TS = now
        return _JWKS_CLIENT


def _verify_id_token(token: str) -> dict:
    """Verify the ID token signature, audience, issuer, and expiry via JWKS.

    Fetches Microsoft's public keys and verifies the RS256 signature so a
    forged JWT is rejected before any claims are trusted.  Raises ValueError
    on any verification failure — callers must not admit the user if this raises.
    """
    try:
        import jwt as _jwt  # PyJWT
    except ImportError as exc:
        raise ValueError(
            "PyJWT[cryptography] is required for token verification. "
            "Run: pip install 'PyJWT[cryptography]>=2.8.0'"
        ) from exc

    jwks_client = _get_jwks_client()
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Cannot retrieve signing key for token: {exc}") from exc

    # Accept both v2.0 and v1.0 (sts.windows.net) issuers so the same code works
    # with single-tenant apps regardless of which endpoint issued the token.
    valid_issuers = {
        f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
        f"https://sts.windows.net/{TENANT_ID}/",
    }

    try:
        claims = _jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            options={"verify_iss": False},  # issuer checked manually below
        )
    except _jwt.ExpiredSignatureError as exc:
        raise ValueError("ID token has expired") from exc
    except _jwt.InvalidTokenError as exc:
        raise ValueError(f"ID token signature is invalid: {exc}") from exc

    if claims.get("iss") not in valid_issuers:
        raise ValueError(f"Untrusted token issuer: {claims.get('iss')!r}")

    return claims


def is_enabled() -> bool:
    return _ENTRA_ENABLED


def generate_state_nonce() -> str:
    """Return a cryptographically random nonce registered in the server-side store.

    The nonce is stored server-side (not just in Streamlit session state) so
    it survives the redirect: Microsoft's callback is a fresh HTTP GET which
    Streamlit treats as a new session, wiping st.session_state.
    Use consume_state() on callback to validate and invalidate the nonce.
    """
    nonce = secrets.token_urlsafe(32)
    register_state(nonce)
    return nonce


def get_auth_url(state: str) -> str:
    """Build the Microsoft authorization URL.

    `state` must be a per-session random nonce returned by
    `generate_state_nonce()`.  Passing a fixed string defeats the CSRF
    protection entirely.
    """
    params = {
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "response_mode": "query",
        "scope":         _SCOPES,
        "state":         state,
        "prompt":        "login",   # force completely fresh login, no cached session
    }
    return f"{_BASE}/authorize?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code: str) -> dict[str, Any]:
    """Exchange the authorization code for tokens."""
    data = {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
        "scope":         _SCOPES,
    }
    resp = _requests.post(f"{_BASE}/token", data=data, timeout=15)
    return resp.json()


def parse_user(token_result: dict) -> dict[str, Any]:
    """Verify the ID token and extract user info and role from claims.

    Raises ValueError if the ID token is missing or its signature cannot
    be verified against Microsoft's JWKS endpoint.  The caller must not
    store or trust the returned dict if this raises.
    """
    id_token = token_result.get("id_token", "")
    if not id_token:
        raise ValueError("Token response contains no id_token")

    claims = _verify_id_token(id_token)

    roles = claims.get("roles") or []
    roles_lower = [r.lower() for r in roles]
    if "admin" in roles_lower:
        role = "admin"
    elif "contributor" in roles_lower:
        role = "contributor"
    elif "viewer" in roles_lower:
        role = "viewer"
    else:
        # No explicit app role assigned — default to contributor so any
        # authenticated tenant user can run the demo without needing a
        # manual role assignment in the Azure portal (requires Entra P1).
        role = "contributor"

    return {
        "name":   claims.get("name") or claims.get("preferred_username", "Unknown"),
        "email":  claims.get("preferred_username", ""),
        "oid":    claims.get("oid", ""),
        "role":   role,
        "roles":  roles,
        "claims": claims,
    }
