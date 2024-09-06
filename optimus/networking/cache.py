import socket
from typing import Optional


class SocketCacheMeta(type):
    __INSTANCE: dict[str, "SocketCache"] = dict()

    def __new__(cls, cls_name, cls_bases, cls_attrs):
        if cls_name not in cls.__INSTANCE:
            cls.__INSTANCE[cls_name] = type(cls_name, cls_bases, cls_attrs)
        return cls.__INSTANCE[cls_name]


class SocketCache(metaclass=SocketCacheMeta):
    def __init__(
        self,
    ) -> None:
        self.cache: dict[str, socket.socket] = dict()

    def put(self, server_addr: str, sock: socket.socket) -> None:
        self.cache[server_addr] = sock

    def get(self, server_addr: str) -> Optional[socket.socket]:
        return self.cache.get(server_addr)

    def delete(self, server_addr: str) -> None:
        if server_addr not in self.cache:
            return
        del self.cache[server_addr]


socket_cache = SocketCache()
