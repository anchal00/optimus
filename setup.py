import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

META: dict = {}
with open(os.path.join(here, "optimus", "__version__.py")) as f:
    exec(f.read(), META)

setup(
    name="optimus",
    version=META.get("VERSION"),
    description="A toy DNS server",
    author="Anchal",
    author_email="anchal82199@gmail.com",
    url="https://github.com/anchal00/optimus",
    packages=find_packages(include=["optimus", "optimus.*"]),
    # install_requires=[
    #     "flake8==6.0.0",
    #     "isort==5.12.0",
    #     "mccabe==0.7.0",
    #     "pycodestyle==2.10.0",
    #     "pyflakes==3.0.1",
    # ],
    python_requires=">=3.9.6",
    entry_points={
        "console_scripts": [
            "optimus = optimus.cli.optimus:main_wrapper",
        ]
    },
)
