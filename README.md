# An unofficial command line interface for 2FAS

twofas-cli is an unofficial client for [2FAS](https://2fas.com) written in Python that can retrieve 2fa codes stored on your mobile device by
registering itself as a browser extension with 2FAS. Every request this tool makes for a 2FA code needs to be approved on your mobile device, just like with 2FAS' browser extensions. You can use it for scripting automatic logins to services that require a
second factor via TOTPs.

## Installation

Install via pip from PyPi:

```shell
pip install twofas-cli
```

## Usage

In order to use twofas-cli you need to have the 2FAS app installed on your mobile device.
Head over to [2fas.com](https://2fas.com) for instructions and a download link for your app store.

After installing 2fas on your mobile device and PC, register twofas-cli as a browser extension by running:

```shell
twofas-cli register
```

After running this command successfully you should see a directory containing a QR code image called 
`qrcode.png`. Open it and scan it using your 2FAS app.

Afterward, you can run `twofas-cli get --help` to see the available options for retrieving 2fa codes or `twofas-cli --help` to see all possible actions.

## Compatibility

twofas-cli should be able to run anywhere its dependencies and Python itself runs, however, it has only been tested so far on MacOS and Linux. It requires a recentish Python 3 version (>= 3.7).

## Contributing

Contributions are welcome. Please use the [Github Page](https://github.com/dspitzer/twofas-cli) to report issues or submit Pull Requests.
