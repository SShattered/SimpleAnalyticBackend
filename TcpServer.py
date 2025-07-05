import socket
import threading
import struct
import MessageHandler
from Models import MessageModel
from dataclasses import asdict

class TcpServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.messageHandler = MessageHandler.MessageHandler(self.writeString)
        self.lock = threading.Lock()

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Tcp Server Started...")

    def __recv_exact(self, sock: socket.socket, size: int) -> bytes:
        buf = b''
        while len(buf) < size:
            chunk = sock.recv(size - len(buf))
            if not chunk:
                raise ConnectionError("Socket connection closed")
            buf += chunk
        return buf

    def __handleClient(self, client_socket: socket.socket) -> None:
        while True:
            try:
                #printing what the client sends
                buffer = self.__recv_exact(client_socket, 4)
                buffLength = struct.unpack(">I", buffer)[0]

                request = self.__recv_exact(client_socket, buffLength)
                #print(f"[+] Received: {request.decode("utf-8")}") 
                self.messageHandler.handleMessages(request.decode("utf-8"), client_socket)
                
            except socket.error as e:
                client_socket.close()
                print(f"Recv {e}")
                break

    def stop(self) -> None:
        self.server_socket.close()

    def writeString(self, message: str, client_socket: socket.socket) -> None:
        data_bytes = message.encode("utf-8")
        data_length_bytes = struct.pack(">I", len(data_bytes))
        with self.lock:
            try:
                client_socket.sendall(data_length_bytes)
                client_socket.sendall(data_bytes)
            except socket.error as e:
                print(f"Send {e}")

    def listen(self) -> None:
        while True: 
            try:
                client, addr = self.server_socket.accept()
                print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")
                client_handler = threading.Thread(target=self.__handleClient, args=(client,))
                client_handler.start()
            except socket.error: 
                print(f"socket error...")