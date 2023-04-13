import socket

from utils.parser import Parser

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5000))
# Connect to google's DNS server
sock.connect(("8.8.8.8", 53))

# Create a Query Packet
packet = Parser.create_query_dns_packet(domain='google.com', recursion_desired=False)
# Send the Query Packet
sock.send(packet)
# Receive response
print(Parser(sock.recv(600)).get_dns_packet()) # Read 600 bytes only for now
sock.close()
