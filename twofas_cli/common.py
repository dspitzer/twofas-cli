import os
from pathlib import Path


def get_settings_dir():
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    settings_dir = (Path(xdg_config_home) if xdg_config_home else 
                    Path.home().joinpath('.config'))\
        .joinpath('twofas-cli')
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir


def get_extension_id():
    return EXTENSION_ID_FILE.read_text(encoding='utf-8')


PRIVATE_KEY_FILE = get_settings_dir().joinpath('private_key.pem')
PUBLIC_KEY_FILE = get_settings_dir().joinpath('public_key.pem')
EXTENSION_ID_FILE = get_settings_dir().joinpath('extension_id')
QRCODE_FILE = get_settings_dir().joinpath('qrcode.png')
