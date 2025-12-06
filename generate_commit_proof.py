# generate_commit_proof.py
import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# ---------- helpers ----------

def get_latest_commit_hash() -> str:
    # returns ASCII hex hash (40 chars)
    h = subprocess.check_output(["git", "log", "-1", "--format=%H"], text=True).strip()
    if len(h) != 40:
        raise ValueError(f"Unexpected commit hash length: {h}")
    return h

def load_student_private_key(pem_path: Path):
    data = pem_path.read_bytes()
    # if your key has a passphrase, put it here as bytes instead of None
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())

def load_instructor_public_key(pem_path: Path):
    data = pem_path.read_bytes()
    return serialization.load_pem_public_key(data, backend=default_backend())

def sign_message_ascii_pss_sha256(message_ascii: str, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Sign ASCII string using RSA-PSS with SHA-256.
    Message must be the ASCII commit hash (40-char hex), not binary.
    """
    msg_bytes = message_ascii.encode("utf-8")
    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,   # maximum salt length
        ),
        hashes.SHA256(),
    )
    return signature

def encrypt_with_instructor_pub(signature: bytes, instructor_pub) -> bytes:
    """
    Encrypt the signature using RSA-OAEP with SHA-256.
    """
    ciphertext = instructor_pub.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext

# ---------- main flow ----------

def main():
    repo = Path(".")
    student_priv_pem = repo / "student_private.pem"
    instructor_pub_pem = repo / "instructor_public.pem"
    out_file = repo / "commit_proof.txt"

    # 1) get commit hash (ASCII hex)
    commit_hash = get_latest_commit_hash()
    print(f"[i] commit hash: {commit_hash}")

    # 2) load keys
    student_priv = load_student_private_key(student_priv_pem)
    instructor_pub = load_instructor_public_key(instructor_pub_pem)

    # 3) sign (RSA-PSS + SHA-256) — message is the ASCII commit hash
    signature = sign_message_ascii_pss_sha256(commit_hash, student_priv)
    print(f"[i] signature length: {len(signature)} bytes")

    # 4) encrypt signature with instructor's public key (RSA-OAEP + SHA-256)
    encrypted_sig = encrypt_with_instructor_pub(signature, instructor_pub)
    print(f"[i] encrypted length: {len(encrypted_sig)} bytes")

    # 5) base64 encode encrypted signature => proof
    proof_b64 = base64.b64encode(encrypted_sig).decode("ascii")

    # 6) save (commit hash + proof) to a text file
    out_file.write_text(
        f"commit: {commit_hash}\nproof_b64: {proof_b64}\n",
        encoding="utf-8"
    )
    print("\n=== PROOF (copy below) ===")
    print(f"commit: {commit_hash}")
    print(f"proof_b64: {proof_b64}")
    print(f"\n[i] saved to: {out_file.resolve()}")

if __name__ == "__main__":
    main()
