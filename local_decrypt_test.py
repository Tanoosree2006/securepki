from decrypt_seed import load_private_key, decrypt_seed
try:
    priv = load_private_key("student_private.pem")
    enc = open("encrypted_seed.txt","r",encoding="utf-8").read().strip()
    hex_seed = decrypt_seed(enc, priv)
    print("Decrypted HEX length:", len(hex_seed))
    print("Preview:", hex_seed[:16], "...")
except Exception as e:
    print("Decrypt error :", e)
