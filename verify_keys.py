from cryptography.hazmat.primitives import serialization

priv = serialization.load_pem_private_key(open("student_private.pem","rb").read(), password=None)
pub_from_priv = priv.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

pub_file = open("student_public.pem","r",encoding="utf-8").read()

if pub_from_priv.strip() == pub_file.strip():
    print("MATCH ✅  private key matches student_public.pem")
else:
    print("MISMATCH ❌  your private key does NOT match student_public.pem")
