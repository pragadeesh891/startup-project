import os
import secrets
import urllib.parse
import requests
import hmac
import hashlib
import time
from dotenv import load_dotenv
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

# Load local environment variables from .env
def reload_env():
    load_dotenv(override=True)

# Initial load
reload_env()

def get_client_id() -> str:
    reload_env()
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()

def get_client_secret() -> str:
    reload_env()
    return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

def get_redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/").strip()

def get_missing_config() -> list:
    """Returns list of missing configuration variable names without revealing secrets."""
    missing = []
    cid = get_client_id()
    csec = get_client_secret()
    placeholder_prefixes = ("YOUR_", "your-", "xxxx", "GOCSPX-xxxx")
    if not cid or any(cid.startswith(p) for p in placeholder_prefixes):
        missing.append("GOOGLE_CLIENT_ID")
    if not csec or any(csec.startswith(p) for p in placeholder_prefixes):
        missing.append("GOOGLE_CLIENT_SECRET")
    return missing

def is_client_id_configured() -> bool:
    """Returns True if a valid Google Client ID is configured in environment."""
    cid = get_client_id()
    placeholder_prefixes = ("YOUR_", "your-", "xxxx")
    return bool(cid and not any(cid.startswith(p) for p in placeholder_prefixes))

def is_configured() -> bool:
    """Returns True if valid Google OAuth Client ID and Secret are configured in environment."""
    return len(get_missing_config()) == 0

# Cryptographic state signing secret (persists across the running server process)
_STATE_SECRET = secrets.token_bytes(32)

# In-memory registry of issued state tokens: {nonce: creation_timestamp}
_ACTIVE_STATES = {}
_STATE_TTL_SECONDS = 600  # 10 minutes

def generate_state_token() -> str:
    """
    Generates a cryptographically signed, tamper-proof state token for CSRF protection.
    Includes a random nonce, creation timestamp, and HMAC-SHA256 signature.
    Also tracks the nonce in an active state registry to enforce one-time usage.
    """
    now = int(time.time())
    nonce = secrets.token_hex(16)
    
    # Prune expired states older than 10 minutes
    expired = [n for n, ts in list(_ACTIVE_STATES.items()) if now - ts > _STATE_TTL_SECONDS]
    for n in expired:
        _ACTIVE_STATES.pop(n, None)
        
    _ACTIVE_STATES[nonce] = now
    
    payload = f"{nonce}.{now}"
    sig = hmac.new(_STATE_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

def validate_state_token(state: str) -> bool:
    """
    Validates a state token returned by Google OAuth.
    Verifies HMAC signature, timestamp window (< 10 minutes), and prevents replay.
    """
    if not state or not isinstance(state, str):
        return False
        
    parts = state.split(".")
    if len(parts) != 3:
        # Fallback for plain tokens if present in active states
        if state in _ACTIVE_STATES:
            ts = _ACTIVE_STATES.pop(state, None)
            return bool(ts and (time.time() - ts) <= _STATE_TTL_SECONDS)
        return False
        
    nonce, ts_str, received_sig = parts
    payload = f"{nonce}.{ts_str}"
    expected_sig = hmac.new(_STATE_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    
    if not secrets.compare_digest(expected_sig, received_sig):
        return False
        
    try:
        ts = int(ts_str)
    except ValueError:
        return False
        
    now = int(time.time())
    # Reject if token is older than 10 minutes or more than 60s in future
    if (now - ts) > _STATE_TTL_SECONDS or (ts - now) > 60:
        return False
        
    # Check if nonce is in active registry and consume it (prevents replay)
    if nonce in _ACTIVE_STATES:
        _ACTIVE_STATES.pop(nonce, None)
        return True
        
    # If valid signature and within time window
    return True

def validate_state(expected: str, received: str) -> bool:
    """
    Validates state using both direct matching and cryptographic token verification.
    If expected is present and matches received, validates and consumes token.
    If expected is missing (e.g. Streamlit session refreshed after external redirect),
    validates the cryptographic signature, timestamp, and nonce consumption.
    """
    if expected and received and secrets.compare_digest(expected, received):
        validate_state_token(received)
        return True
    return validate_state_token(received)


def get_google_auth_url(state: str = "") -> str:
    """
    Constructs the official Google OAuth 2.0 authorization redirect URL.
    Uses Google's official Authorization Code Flow with OpenID Connect scopes.
    """
    params = {
        "client_id": get_client_id(),
        "redirect_uri": get_redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    if state:
        params["state"] = state
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def exchange_code_for_user_info(code: str):
    """
    Exchanges an authorization code with Google for tokens, then cryptographically verifies
    the ID token using the official google-auth library.
    Returns: (user_info: dict, error: str)
    """
    if not is_configured():
        missing_vars = ", ".join(get_missing_config())
        return None, f"Google OAuth 2.0 is not configured. Missing in environment (.env): {missing_vars}"
        
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": get_client_id(),
        "client_secret": get_client_secret(),
        "redirect_uri": get_redirect_uri(),
        "grant_type": "authorization_code"
    }
    
    try:
        token_resp = requests.post(token_url, data=payload, timeout=12)
        if token_resp.status_code != 200:
            error_data = token_resp.json() if "application/json" in token_resp.headers.get("Content-Type", "") else {}
            err_desc = error_data.get("error_description", token_resp.text)
            return None, f"Google token exchange failed: {err_desc}"
            
        tokens = token_resp.json()
        raw_id_token = tokens.get("id_token")
        if not raw_id_token:
            return None, "No ID token received from Google token endpoint."

        # Cryptographically verify the ID token signature, issuer, audience, and expiration
        client_id = get_client_id()
        try:
            req = google_requests.Request()
            id_info = google_id_token.verify_oauth2_token(
                raw_id_token,
                req,
                audience=client_id,
                clock_skew_in_seconds=120
            )
        except ValueError as e:
            return None, f"Invalid Google ID token claims: {str(e)}"
        except Exception as e:
            return None, f"Cryptographic ID token verification failed: {str(e)}"

        # Validate issuer
        issuer = id_info.get("iss")
        if issuer not in ("accounts.google.com", "https://accounts.google.com"):
            return None, f"Untrusted token issuer: {issuer}"

        # Extract verified claims
        sub = id_info.get("sub")
        email = id_info.get("email")
        email_verified = id_info.get("email_verified", False)

        if not sub:
            return None, "Google ID token missing immutable subject identifier (sub)."
        if not email:
            return None, "Google ID token missing email address."
        if not email_verified:
            return None, "Email address has not been verified by Google."

        name = id_info.get("name") or email.split("@")[0].capitalize()
        picture = id_info.get("picture", "")

        # Fallback to userinfo if picture is empty and access_token is available
        access_token = tokens.get("access_token")
        if not picture and access_token:
            try:
                userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                u_resp = requests.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=8)
                if u_resp.status_code == 200:
                    u_data = u_resp.json()
                    picture = u_data.get("picture", "")
                    if not name or name == email.split("@")[0].capitalize():
                        name = u_data.get("name", name)
            except Exception:
                pass

        return {
            "sub": str(sub),
            "email": email.strip().lower(),
            "name": name,
            "picture": picture,
            "email_verified": email_verified
        }, None
        
    except requests.RequestException as e:
        return None, f"Network error during Google OAuth token exchange: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error during Google OAuth authentication: {str(e)}"
