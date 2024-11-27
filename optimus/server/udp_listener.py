import socket
from concurrent import futures

from optimus.dns.models.packet import DNSPacket, ResponseCode
from optimus.dns.parser.parse import DNSParser
from optimus.dns.resolver import resolve
from optimus.logging.logger import log, log_error
from optimus.networking.cache import socket_cache
from optimus.prometheus import record_metrics, with_prometheus_metrics_server
from optimus.server.context import warmup_cache
from optimus.utils import SingletonMeta


class UdpServer(metaclass=SingletonMeta):
    def __init__(self, port: int, worker_threads: int) -> None:
        self.__port = port
        self.__threads = worker_threads

    @with_prometheus_metrics_server
    @warmup_cache(socket_cache)
    def run(self) -> None:
        self.__master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__master_socket.bind(("0.0.0.0", self.__port))
        log(f"Started Optimus Server on Port {self.__port} with {self.__threads} threads")
        # TODO: Test with ProcessPoolExecutor and EPOLL
        try:
            with futures.ThreadPoolExecutor(max_workers=self.__threads) as pool:
                while True:
                    received_bytes, address = self.__master_socket.recvfrom(600)
                    pool.submit(self.__handle_request, received_bytes, address)
        except KeyboardInterrupt:
            log("Goodbye ! Shutting Down the server...")
        finally:
            self.__master_socket.close()

    @record_metrics
    def __handle_request(self, received_bytes: bytes, return_address: tuple[str, int]) -> bool:
        query_packet: DNSPacket = DNSParser(bytearray(received_bytes)).get_dns_packet()
        log(f"Received query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype}")
        # if query_packet.questions[0].name.split(".")[-1] == "hgu_lan":
        #     self.__master_socket.sendto(b"", return_address)
        #     return True
        response_packet: DNSPacket = resolve(query_packet)
        response_packet.header.is_recursion_available = True
        self.__master_socket.sendto(response_packet.to_bin(), return_address)
        if response_packet.header.response_code != ResponseCode.NOERROR:
            log_error(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} errored out")
            return False
        log(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} successfully processed")
        return True
