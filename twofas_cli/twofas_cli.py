import re
import signal
import sys
import os

import click

from . import crypt
from .api import TwoFasApi
from .common import get_settings_dir, get_extension_id, BARCODE_FILE, \
    PRIVATE_KEY_FILE, EXTENSION_ID_FILE, PUBLIC_KEY_FILE


@click.group(name="test")
def cli():
    pass


@click.command('register', help='Register with 2FAS as a new "browser extension"')
@click.option('--name', default=f'2FAS CLI {os.uname().sysname}', 
              help='The name that you want displayed for this CLI integration on your '
                   'mobile device',
              show_default=True, prompt=True)
@click.option('--api-base_url', default=TwoFasApi.API_DEFAULT_BASE_URL,
              help='Base URL for the 2FAS REST API', show_default=True)
def new(api_base_url: str, name: str):
    crypt.generate_key_pair()
    api = TwoFasApi(api_base_url)
    click.echo('Registering new "browser extension"...')
    ext = api.create_extension_instance(name)
    extension_id = ext['id']
    # Assert that extension_id is a valid uuid
    click.echo(f'Extension ID: {extension_id}')
    get_settings_dir().joinpath('extension_id').write_text(extension_id, 
                                                           encoding='utf-8')
    barcode_file = generate_barcode(api.generate_qr_link(extension_id))
    click.echo(f"Please scan the QR code image found under '{barcode_file}' with your "
               f"2FAS mobile app (under  Settings -> 'Browser extension')")


@click.command('get', help='Fetch a 2FA token for a website or service')
@click.option('--domain', help='Full URL of the website you want to get the 2FA token '
                               'for', type=str)
@click.option('--identifier', 
              help='Instead of a domain, you can also set a custom identifier that you '
                   'can associate with a 2FA code on your mobile device. Only ASCII '
                   'letters, whitespace and the following symbols are allowed: -.',
              type=str)
@click.option('--api-base-url', default=TwoFasApi.API_DEFAULT_BASE_URL, 
              help='Base URL for the 2FAS REST API', show_default=True)
@click.option('--ws-base-url', default=TwoFasApi.WS_DEFAULT_BASE_URL, 
              help='Base URL for the 2FAS Websockets API', show_default=True)
def get(domain: str, identifier: str, api_base_url: str, ws_base_url: str):
    check_if_registered() or sys.exit(1)
    if not domain and not identifier:
        click.echo('Either --domain or --identifier must be set', err=True)
        click.echo(click.get_current_context().get_help(), err=True)
        sys.exit(1)
    if domain and identifier:
        click.echo('Only one of --domain or --identifier can be set', err=True)
        click.echo(click.get_current_context().get_help(), err=True)
        sys.exit(1)

    if identifier:
        domain = re.sub(r'[^a-zA-Z0-9 -.]', '', identifier.strip()).lower()
        domain = 'https://' + domain.replace(' ', '.') + '.2fa.invalid'

    api = TwoFasApi(api_base_url, ws_base_url)
    extension_id = get_extension_id()
    response = api.request2_fa_token(extension_id, domain)

    token_request_id = response['token_request_id']
    if response['status'] != 'pending':
        click.echo(f'Invalid response status from TWOFAS: {response["status"]}', 
                   err=True)
        sys.exit(1)

    # noinspection PyUnusedLocal
    def signal_handler(sig, frame):
        click.echo('Aborting...', err=True)
        api.close2_fa_request(extension_id, token_request_id, status=False)
        sys.exit(2)

    signal.signal(signal.SIGINT, signal_handler)

    click.echo('Waiting for approval from 2FAS mobile app...', err=True)
    click.echo(api.fetch_2fa_token(token_request_id, extension_id))
    api.close2_fa_request(extension_id, token_request_id)


@click.group(name="devices", help="Manage mobile device pairings")
def devices():
    pass


@click.command("list", help="List all paired mobile devices")
@click.option('--api-base-url', default=TwoFasApi.API_DEFAULT_BASE_URL, 
              help='Base URL for the 2FAS REST API', show_default=True)
def list_devices(api_base_url: str):
    check_if_registered() or sys.exit(1)
    api = TwoFasApi(api_base_url)
    res = api.get_all_paired_devices(get_extension_id())
    click.echo('Device ID                             Device Name', err=True)
    for device in res:
        click.echo(f'{device["id"]}  {device["name"]}')


@click.command("delete", help="Delete a mobile device pairing. Pass the device ID of "
                              "the mobile device pairing to delete (use "
                              "`twofas-cli list` to see a list)")
@click.argument('device-id', type=str)
@click.option('--api-base-url', default=TwoFasApi.API_DEFAULT_BASE_URL,
              help='Base URL for the 2FAS REST API',
              show_default=True)
def delete_device(device_id: str, api_base_url: str):
    check_if_registered() or sys.exit(1)
    api = TwoFasApi(api_base_url)
    api.remove_paired_device(get_extension_id(), device_id)


def generate_barcode(barcode_link: str):
    import pyqrcode
    import click

    qr = pyqrcode.create(barcode_link)
    qr.png(BARCODE_FILE, scale=6)
    click.launch(str(BARCODE_FILE), locate=True)
    return str(BARCODE_FILE)


def check_if_registered() -> bool:
    if not PRIVATE_KEY_FILE.exists() or not PUBLIC_KEY_FILE.exists() \
            or not EXTENSION_ID_FILE.exists():
        click.echo('Please run "twofas-cli register" first', err=True)
        return False
    return True


cli.add_command(devices)
cli.add_command(get)
cli.add_command(new)
devices.add_command(list_devices)
devices.add_command(delete_device)
