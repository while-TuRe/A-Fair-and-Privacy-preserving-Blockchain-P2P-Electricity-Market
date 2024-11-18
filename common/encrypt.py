import socket
import struct
from phe import paillier, PaillierPublicKey
import random
import sys

class EncryptClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        n = int(input())    # 从区块链上读
        self.public_key = PaillierPublicKey(n)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        print(f"Connected to server at {self.server_ip}:{self.server_port}")

    def send_to_compare(self, d1, d2):
        r = random.randint(0, sys.maxsize)
        # 加密数据
        enc_d1 = self.public_key.encrypt(d1+r).ciphertext()
        enc_d2 = self.public_key.encrypt(d2+r).ciphertext()
        msg = f"{enc_d1},{enc_d2}"
        data_length = len(msg)

        # 发送加密数据
        self.client_socket.sendall(struct.pack('!I', data_length))
        self.client_socket.sendall(f"{enc_d1},{enc_d2}".encode())
        print(f"Sent encrypted data: d1={d1}, d2={d2}")

        # 接收比较结果
        result = self.client_socket.recv(4)
        result = struct.unpack('!i', result)[0]
        print(f"Comparison result: {result}")
        return result

    def close_connection(self):
        self.client_socket.close()
        print("Connection closed")

# 示例调用
if __name__ == "__main__":
    client = EncryptClient('localhost', 13322)
    client.send_to_compare(10, 22)
    client.close_connection()
