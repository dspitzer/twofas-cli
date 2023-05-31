import base64
import json

import click
import requests
import websockets.sync.client as ws

from twofas_cli.crypt import get_public_key_spki, decrypt


class TwoFasApi:
    API_DEFAULT_BASE_URL = 'https://api2.2fas.com'
    WS_DEFAULT_BASE_URL = 'wss://ws.2fas.com'

    def __init__(self, api_base_url: str = API_DEFAULT_BASE_URL, 
                 ws_base_url: str = WS_DEFAULT_BASE_URL):
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.api_base_url = api_base_url
        self.ws_base_url = ws_base_url

    @staticmethod
    def process_response(res):
        if 200 <= res.status_code < 400:
            return res.json()
        else:
            # Print body as json to stderr
            click.echo(f'Error: {res.status_code}', err=True)
            click.echo(json.dumps(res.json(), indent=2), err=True)
            res.raise_for_status()

    @staticmethod
    def create_browser_info(name: str) -> dict:
        return {
            'name': name,
            'browser_name': '2FAS CLI',
            'browser_version': '0.0.1',
            'public_key': get_public_key_spki()
        }

    def create_extension_instance(self, browser_name: str):
        res = requests.post(f'{self.api_base_url}/browser_extensions',
                            headers=self.headers,
                            data=json.dumps(self.create_browser_info(browser_name)))
        return self.process_response(res)

    def update_browser_extension(self, ext_id: str, browser_name: str):
        res = requests.put(f'{self.api_base_url}/browser_extensions/{ext_id}',
                           headers=self.headers,
                           data=json.dumps(self.create_browser_info(browser_name)))
        return self.process_response(res)

    def get_all_paired_devices(self, ext_id):
        res = requests.get(f'{self.api_base_url}/browser_extensions/{ext_id}/devices',
                           headers=self.headers)
        return self.process_response(res)

    def remove_paired_device(self, ext_id, device_id):
        res = requests.delete(f'{self.api_base_url}/browser_extensions/{ext_id}/devices'
                              f'/{device_id}', headers=self.headers)
        return self.process_response(res)

    def request2_fa_token(self, ext_id, domain):
        res = requests.post(f'{self.api_base_url}/browser_extensions/{ext_id}/commands'
                            f'/request_2fa_token',
                            headers=self.headers, data=json.dumps({"domain": domain}))
        return self.process_response(res)

    def close2_fa_request(self, ext_id, request_id, status=True):
        data = {"status": "completed" if status else "terminated"}
        res = requests.post(
            f'{self.api_base_url}/browser_extensions/{ext_id}/2fa_requests/{request_id}'
            f'/commands/close_2fa_request',
            headers=self.headers,
            data=json.dumps(data))
        return self.process_response(res)

    def fetch_2fa_token(self, token_request_id: str, extension_id: str) -> str:
        with ws.connect(
                f'{self.ws_base_url}/browser_extensions/{extension_id}/2fa_requests'
                f'/{token_request_id}', ) as socket:
            while True:
                data = json.loads(socket.recv())
                if data["event"] == "browser_extensions.device.2fa_response":
                    token_encrypted_base64 = data["token"]
                    token_encrypted = base64.b64decode(token_encrypted_base64)
                    return decrypt(token_encrypted)
                else:
                    click.echo(f'Unknown event: {data["event"]}', err=True)

    @staticmethod
    def generate_qr_link(browser_ext_id):
        return f'twofas_c://{browser_ext_id}'
