import click
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

from twofas_cli.common import PRIVATE_KEY_FILE, PUBLIC_KEY_FILE


def generate_key_pair():
    click.echo('Generating new key pair...')

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    PRIVATE_KEY_FILE.write_bytes(private_key_bytes)
    PUBLIC_KEY_FILE.write_bytes(public_key_bytes)


def get_public_key() -> rsa.RSAPublicKey:
    public_key = serialization.load_pem_public_key(
        PUBLIC_KEY_FILE.read_bytes()
    )

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError('Expected RSA public key')

    return public_key


def get_private_key() -> rsa.RSAPrivateKey:
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_FILE.read_bytes(),
        password=None
    )

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError('Expected RSA private key')

    return private_key


def get_public_key_spki() -> str:
    public_key = get_public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key = public_key.replace(b'-----BEGIN PUBLIC KEY-----', b'')
    public_key = public_key.replace(b'-----END PUBLIC KEY-----', b'')
    public_key = public_key.replace(b'\n', b'')
    return public_key.decode('ascii')


def encrypt(message):
    return get_public_key().encrypt(message, _padding())


def decrypt(message):
    return get_private_key().decrypt(message, _padding())


def _padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA512()),
        algorithm=hashes.SHA512(),
        label=None
    )
