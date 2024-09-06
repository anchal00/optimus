import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

META: dict[str, str] = {}
with open(os.path.join(here, "optimus", "__version__.py")) as f:
    exec(f.read(), META)

setup(
    name="optimus",
    version=META["VERSION"],
    description="A toy DNS server",
    author="Anchal",
    author_email="anchal82199@gmail.com",
    url="https://github.com/anchal00/optimus",
    package_data={"optimus": ["*.json"]},
    include_package_data=True,
    packages=find_packages(include=["optimus", "optimus.*"]),
    install_requires=["prometheus_client==0.20.0"],
    python_requires=">=3.9.6",
    entry_points={
        "console_scripts": [
            "optimus = optimus.cli.optimus:main_wrapper",
        ]
    },
)
