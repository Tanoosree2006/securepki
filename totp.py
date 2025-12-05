import base64
import pyotp

def hex_to_base32(hex_seed: str) -> str:
    """Convert 64-character hex seed to base32 string for TOTP"""
    seed_bytes = bytes.fromhex(hex_seed)          # Convert hex to bytes
    base32_seed = base64.b32encode(seed_bytes)    # Encode bytes to base32
    return base32_seed.decode('utf-8')            # Decode to string

def generate_totp_code(hex_seed: str) -> str:
    """Generate current 6-digit TOTP code from hex seed"""
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)  # SHA-1 default
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """Verify a TOTP code with time window tolerance"""
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)

# Example usage
if __name__ == "__main__":
    # Read seed from previous step
    with open("data/seed.txt", "r") as f:
        hex_seed = f.read().strip()
    
    # Generate TOTP
    current_code = generate_totp_code(hex_seed)
    print("Current TOTP code:", current_code)
    
    # Optional verification
    is_valid = verify_totp_code(hex_seed, current_code)
    print("Verification result:", is_valid)
