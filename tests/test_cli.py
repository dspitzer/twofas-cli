def test_barcode_generation():
    from twofas_cli import generate_barcode
    from twofas_cli import BARCODE_FILE
    generate_barcode('https://example.com')
    assert BARCODE_FILE.exists(), "Barcode file should exist after generation"


def test_generate_keypair():
    from twofas_cli import generate_key_pair, get_public_key, get_private_key
    generate_key_pair()
    assert get_private_key(), "Private key file should exist after generation"
    assert get_public_key(), "Public key file should exist after generation"
