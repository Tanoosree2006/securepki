import base64
path = "encrypted_seed.txt"
s = open(path, "r", encoding="utf-8").read().strip()
try:
    raw = base64.b64decode(s, validate=True)
    print("OK base64   length:", len(raw), "bytes")
except Exception as e:
    print("Invalid base64 :", e)
