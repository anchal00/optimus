import socket
from typing import Optional

from optimus.utils import SingletonMeta


class SocketCache(metaclass=SingletonMeta):
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
