import base64, subprocess
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# ---- functions from above ----
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
def sign_message(message: str, private_key) -> bytes:
    msg_bytes = message.encode("utf-8")
    return private_key.sign(
        msg_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    return public_key.encrypt(
        data,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
# --------------------------------

def get_commit_hash() -> str:
    h = subprocess.check_output(["git", "log", "-1", "--format=%H"], text=True).strip()
    if len(h) != 40:
        raise ValueError("Commit a change first; expected a 40-char hash.")
    return h

def load_priv(p: Path):
    return serialization.load_pem_private_key(p.read_bytes(), password=None, backend=default_backend())

def load_pub(p: Path):
    return serialization.load_pem_public_key(p.read_bytes(), backend=default_backend())

def main():
    repo = Path(".")
    student_priv = load_priv(repo/"student_private.pem")
    instructor_pub = load_pub(repo/"instructor_public.pem")

    commit = get_commit_hash()
    sig = sign_message(commit, student_priv)
    enc = encrypt_with_public_key(sig, instructor_pub)
    proof_b64 = base64.b64encode(enc).decode("ascii")

    (repo/"commit_proof.txt").write_text(f"commit: {commit}\nproof_b64: {proof_b64}\n", encoding="utf-8")
    print("commit:", commit)
    print("proof_b64:", proof_b64)
    print("saved to commit_proof.txt")

if __name__ == "__main__":
    main()
