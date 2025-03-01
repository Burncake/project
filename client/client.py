import socket
import struct
import time
import os
from queue import Queue
from threading import Thread

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

def perform_handshake(sock, host, port):
    """Performs the handshake with the server."""
    handshake_header = create_header(PACKET_TYPE_HANDSHAKE)
    sock.sendto(handshake_header, (host, port))

    # Wait for handshake acknowledgment
    data, addr = sock.recvfrom(1024)
    magic, packet_type, sequence_number = parse_header(data[:8])
    payload = data[8:]

    if magic == MAGIC_NUMBER and packet_type == PACKET_TYPE_HANDSHAKE:
        print(f"Received handshake acknowledgment from {addr}: {payload.decode()}")
        return True
    else:
        print("Invalid handshake acknowledgment.")
        return False

def udp_client(sock, host, port, message, packet_type):
    try:
        # Send the message with the header
        header = create_header(packet_type)
        sock.sendto(header + message.encode(), (host, port))

        # Receive the response
        data, addr = sock.recvfrom(1024)
        magic, packet_type, sequence_number = parse_header(data[:8])
        payload = data[8:]

        if magic == MAGIC_NUMBER:
            print(f"Received response from {addr}: {payload.decode()}")
        else:
            print("Invalid magic number in response.")

    except Exception as e:
        print(f"An error occurred: {e}")

def monitor_input_file(queue):
    """Monitors the input.txt file for new entries every 5 seconds."""
    last_position = 0
    while True:
        if os.path.exists("input.txt"):
            with open("input.txt", "r") as file:
                file.seek(last_position)
                lines = file.readlines()
                if lines:
                    for line in lines:
                        queue.put(line.strip())
                    last_position = file.tell()
        time.sleep(5)

if __name__ == "__main__":
    host = "127.0.0.1"  # Replace with the server's IP address if running on a different machine
    port = 5000

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Continue when handshake is established
        if perform_handshake(sock, host, port):
            file_queue = Queue()
            monitor_thread = Thread(target=monitor_input_file, args=(file_queue,))
            monitor_thread.daemon = True
            monitor_thread.start()

            while True:
                if not file_queue.empty():
                    file_request = file_queue.get()
                    print(f"Requesting file: {file_request}")
                    udp_client(sock, host, port, file_request, PACKET_TYPE_FILE_REQUEST)
                else:
                    message = input("Enter a message: ")
                    if message == "file_request":
                        udp_client(sock, host, port, message, PACKET_TYPE_FILE_REQUEST)
                    else:
                        udp_client(sock, host, port, message, PACKET_TYPE_DATA)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'sock' in locals():
            sock.close()