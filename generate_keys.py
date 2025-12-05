from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair
    Returns:
        Tuple of (private_key, public_key) objects
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # Generate public key
    public_key = private_key.public_key()

    return private_key, public_key


def save_keys_to_pem(private_key, public_key):
    # Save private key
    with open("student_private.pem", "wb") as priv_file:
        priv_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save public key
    with open("student_public.pem", "wb") as pub_file:
        pub_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo  # standard
        ))


if __name__ == "__main__":
    private_key, public_key = generate_rsa_keypair()
    save_keys_to_pem(private_key, public_key)
    print("RSA 4096-bit key pair generated and saved as student_private.pem & student_public.pem")
