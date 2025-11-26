import base64
import hashlib
from cryptography.fernet import Fernet
from .config import settings

def _derive_key() -> bytes:
    h = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(h)

def get_fernet() -> Fernet:
    return Fernet(_derive_key())
