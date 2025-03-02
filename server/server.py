import socket
import threading
import queue
import time
import sys



data_size = 1024
client_threads = {}
thread_msg_queue = {}

def read_txt_file(file_path):
    """
    Đọc toàn bộ nội dung của một file văn bản (.txt).

    :param file_path: Đường dẫn đến file .txt cần đọc.
    :return: Nội dung của file dưới dạng chuỗi (string).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File không tồn tại."
    except Exception as e:
        return f"Lỗi khi đọc file: {e}"


def read_file_offset(file_path, offset, chunk_size=1024*1024):
    """
    Đọc một phần của file từ vị trí offset và trả về dữ liệu đã đọc.

    :param file_path: Đường dẫn tới file cần đọc.
    :param offset: Vị trí bắt đầu đọc trong file (tính bằng byte).
    :param chunk_size: Số byte cần đọc (mặc định là 1MB).
    :return: Dữ liệu đọc được dưới dạng bytes hoặc None nếu lỗi.
    """
    try:
        with open(file_path, 'rb') as file:
            file.seek(offset)  # Di chuyển con trỏ đến vị trí offset
            data = file.read(chunk_size)  # Đọc tối đa chunk_size byte
            return data
    except FileNotFoundError:
        print("❌ Lỗi: File không tồn tại.")
        return None
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return None


def handle_client(addr, server_socket, msg_queue):
    print(f"🟢 Bắt đầu xử lý client {addr}")
 
    while True:
        message = msg_queue.get()  # Chờ nhận dữ liệu từ queue
        if message == "exit":
            print(f"🔴 Client {addr} ngắt kết nối.")
            break
        elif (message == "ACK"):

            read_file_offset()
        
        if (message):
            server_socket.sendto(message.encode('utf-8'), addr)
        print(f"📩 Nhận từ {addr}: {message}")


def handle_client_file_download(addr, server_socket):
    msg_queue = queue.Queue()
    while True:
        data, addr = server_socket.recvfrom(1024)
        if (data.decode('utf-8') == "exit"):
            break
        if addr not in client_threads and len(client_threads) <= 4:
            # Khởi tạo một hàng đợi msg để truyền vào thread
            msg_queue.put("Hello")
            print("Hello")

            # Khởi tạo thread xử lí client
            client_thread = threading.Thread(target=handle_client, args=(addr, server_socket, msg_queue), daemon=True)
            client_threads[addr] = client_thread
            client_thread.start()
        elif addr in client_threads: 
            print("hello 2")
            time.sleep(0.01)
            msg_queue.put(data.decode('utf-8'))
    return 0


import socket

def start_udp_server(host='127.0.0.1', port=65432):
    """
    Khởi động UDP server để nhận và gửi dữ liệu qua lại với client.
    :param host: Địa chỉ IP server lắng nghe (mặc định là localhost).
    :param port: Cổng server lắng nghe (mặc định là 65432).
    """


    # Tạo socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # Bind socket đến host và port
        server_socket.bind((host, port))
        print(f"UDP Server đang lắng nghe trên {host}:{port}...")
        data, addr = server_socket.recvfrom(1024)  
        if (data.decode("utf-8") == "Hello"): 
            print("Da nhan duoc hello")
            #Hello nguoc lai client
            server_socket.sendto("Hello".encode('utf-8'), addr)
            data, addr = server_socket.recvfrom(1024)
            if (data.decode('utf-8') == "ListFileRequest"):
                # Đọc nội dung của file "list_file.txt" và lưu vào biến `list_file`
                list_file = read_txt_file("list_file.txt")
                # Gửi nội dung file dưới dạng chuỗi đã mã hóa UTF-8 đến client
                server_socket.sendto(list_file.encode('utf-8'), addr)
                handle_client_file_download(addr, server_socket)
        
            

if __name__ == "__main__":
    start_udp_server()
