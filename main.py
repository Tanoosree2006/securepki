from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from decrypt_seed import decrypt_seed, load_private_key
from totp import generate_totp_code, verify_totp_code

app = FastAPI()
DATA_DIR = "data"
SEED_FILE = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_FILE = "student_private.pem"

# -------------------- Request Models --------------------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class Verify2FARequest(BaseModel):
    code: str

# -------------------- Endpoint 1: Decrypt Seed --------------------
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    try:
        private_key = load_private_key(PRIVATE_KEY_FILE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load private key '{PRIVATE_KEY_FILE}': {e}")

    try:
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)
        if not hex_seed or len(hex_seed) % 2 != 0:
            raise ValueError("Decryption returned invalid hex.")
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            f.write(hex_seed)
        return {"status": "ok", "saved_to": SEED_FILE}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {e}")

# -------------------- Endpoint 2: Generate 2FA --------------------
@app.get("/generate-2fa")
def generate_2fa_endpoint():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        import time
        current_seconds = int(time.time()) % 30
        valid_for = 30 - current_seconds

        return {"code": code, "valid_for": valid_for}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

# -------------------- Endpoint 3: Verify 2FA --------------------
@app.post("/verify-2fa")
def verify_2fa_endpoint(request: Verify2FARequest):
    if not request.code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        is_valid = verify_totp_code(hex_seed, request.code, valid_window=1)
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
