import socket
import struct
from phe import paillier, PaillierPublicKey
class DecryptServer:
    def __init__(self, host='localhost', port=13322):
        self.host = host
        self.port = port
        # 创建Paillier 密钥对
        public_key, self.private_key = paillier.generate_paillier_keypair()
        print(public_key.n) #写到区块链
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected by {self.addr}")

    def receive_and_compare(self):
        while True:
            length_bytes = self.conn.recv(4)
            if not length_bytes:
                break
            data_length = struct.unpack('!I', length_bytes)[0]  # !I 表示 big-endian 无符号整型
            data = self.conn.recv(data_length).decode()
            # print(f'length {data_length},data:{data}')
            if not data:
                break
            enc_d1, enc_d2 = map(int, data.split(','))
            d1 = self.private_key.raw_decrypt(enc_d1)
            d2 = self.private_key.raw_decrypt(enc_d2)
            
            # 比较并发送结果
            if d1<d2:
                comparison_result = -1
            elif d1>d2:
                comparison_result = 1
            else:
                comparison_result =0
            print(f"Received and compared: d1={d1}, d2={d2}, result sent: {comparison_result}")
            self.conn.sendall(struct.pack('!i',comparison_result))
            

    def close_connection(self):
        self.conn.close()
        self.server_socket.close()
        print("Server connection closed")

# 示例调用
if __name__ == "__main__":
    server = DecryptServer()
    server.receive_and_compare()
    server.close_connection()
