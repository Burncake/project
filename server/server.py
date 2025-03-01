import socket
import struct

MAGIC_NUMBER = 0x12345678
PACKET_TYPE_DATA = 1
PACKET_TYPE_CONTROL = 2
PACKET_TYPE_HANDSHAKE = 3
PACKET_TYPE_FILE_REQUEST = 4

def create_header(packet_type, sequence_number=0):
    """Creates a custom header."""
    return struct.pack("!IHH", MAGIC_NUMBER, packet_type, sequence_number)

def parse_header(header_bytes):
    """Parses a custom header."""
    magic, packet_type, sequence_number = struct.unpack("!IHH", header_bytes)
    return magic, packet_type, sequence_number

def file_response(sock, addr, requested_file):
    """Sends the contents of file_list.txt to the client."""
    try:
        with open("file_list.txt", "r") as file:
            file_list = file.read()
        print(f"File requested: {requested_file} by {addr}")
        sock.sendto(create_header(PACKET_TYPE_FILE_REQUEST) + file_list.encode(), addr)
    except FileNotFoundError:
        sock.sendto(create_header(PACKET_TYPE_FILE_REQUEST) + "file_list.txt not found".encode(), addr)

def udp_server(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        print(f"UDP server listening on {host}:{port}")

        while True:
            data, addr = sock.recvfrom(1024)
            header_bytes = data[:8]  # Header is 8 bytes
            payload = data[8:]

            magic, packet_type, sequence_number = parse_header(header_bytes)

            if magic == MAGIC_NUMBER:
                if packet_type == PACKET_TYPE_HANDSHAKE:
                    print(f"Received handshake packet from {addr}")
                    sock.sendto(create_header(PACKET_TYPE_HANDSHAKE) + "Handshake acknowledged".encode(), addr)
                elif packet_type == PACKET_TYPE_DATA:
                    print(f"Received data packet from {addr}: {payload.decode()}")
                    sock.sendto(create_header(PACKET_TYPE_DATA) + "Message received!".encode(), addr)
                elif packet_type == PACKET_TYPE_CONTROL:
                    print(f"Received control packet from {addr}: {payload.decode()}")
                    sock.sendto(create_header(PACKET_TYPE_CONTROL) + "Control message received!".encode(), addr)
                elif packet_type == PACKET_TYPE_FILE_REQUEST:
                    requested_file = payload.decode()
                    print(f"Received file request from {addr}")
                    file_response(sock, addr, requested_file)
                else:
                    print(f"Unknown packet type from {addr}")
            else:
                print(f"Invalid magic number from {addr}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'sock' in locals():
            sock.close()

if __name__ == "__main__":
    host = "127.0.0.1"  # Bind to all available interfaces
    port = 5000
    udp_server(host, port)