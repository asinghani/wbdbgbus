from setuptools import setup

setup(
    name = "wbdbgbus",
    version = "1.0.0",
    author = "Anish Singhani",
    description = "Host-side library for wishbone debug bus",
    url = "https://github.com/asinghani/wbdbgbus",
    packages = ["wbdbgbus"],
    #scripts = ["scripts/wb"],
    install_requires = [
        "pyserial==3.4",
        "click==7.1.2"
    ]
)
