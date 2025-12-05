# decrypt_seed.py
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(path: str, password: bytes | None = None):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=password)

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    ct = base64.b64decode(encrypted_seed_b64.strip())
    pt = private_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return pt.hex()
