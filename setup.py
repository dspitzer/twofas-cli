from setuptools import setup, find_packages

# read the contents of your README.md file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="twofas-cli",
    version="0.0.1",
    author="dspd",
    author_email="inmost-chimps-0j@icloud.com",
    description="Unofficial CLI tool for 2FAS using the browser extension api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    keywords="2fas twofas",
    url="https://packages.python.org/twofas-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.7',
    install_requires=[
        'Click', 'requests', 'cryptography', 'pyqrcode', 'pypng', 'websockets'
    ],
    entry_points={
        'console_scripts': [
            'twofas-cli = twofas_cli:cli',
        ],
    },
)
