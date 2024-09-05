import json
import os
import posixpath
from typing import List
import pathlib
import socket


__NAMESERVERS: List[str] = []


def get_root_servers():
    global __NAMESERVERS
    optimus_root = pathlib.Path(os.path.abspath(os.path.dirname(__file__))).parent
    if not __NAMESERVERS:
        file_path = os.path.join(optimus_root, "root_servers.json")
        if not posixpath.exists(file_path):
            raise Exception("root servers file not found !")
        with open(file_path, "r") as f:
            __NAMESERVERS = json.load(f)["servers"]
    return __NAMESERVERS


def warmup_cache(cache):
    def inner(func):
        def wrapper(*args, **kwargs):
            addresses = get_root_servers()
            for addr in addresses:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.connect((addr, 53))
                cache.put(addr, sock)
            func(*args, **kwargs)

        return wrapper

    return inner
