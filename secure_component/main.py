from phe import paillier,command_line
from flask import Flask, request, jsonify
import json,sys,os,threading
middleware = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../Middleware')
sys.path.append(middleware)
import blockchainConnector as bc
from eth_account import Account

key_file = 'secure_key.pri'
default_account = Account.from_key("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d")

# public_key, private_key = paillier.generate_paillier_keypair()
# n = public_key.n
# p,q = private_key.p,private_key.q

# print(f"type is :{type(n)}, {type(p)}, {type(q)}")
# recover_pub_key = paillier.PaillierPublicKey(n)
# recover_pri_key = paillier.PaillierPrivateKey(recover_pub_key,p,q)

# secret_number_list = [3.141592653, 300, -4.6e-12,1,2]
# encrypted_number_list = [recover_pub_key.encrypt(x) for x in secret_number_list]

# test_encrypted = encrypted_number_list[-1]+encrypted_number_list[-2]
# Serialisation = [test_encrypted.ciphertext(),test_encrypted.exponent]
# send_msg= (json.dumps(Serialisation))
# receive = json.loads(send_msg)

# enc_nums_rec = paillier.EncryptedNumber(recover_pub_key, int(receive[0]), int(receive[1]))
# print(enc_nums_rec)
# print(recover_pri_key.decrypt(enc_nums_rec))

# 创建 Flask 应用
app = Flask(__name__)
# 创建一个事件对象来控制线程的停止
stop_event = threading.Event()

def main():
    bc.loadTokenContract(bc.Contract_address,bc.abi_file)
    print("输入 -g 生成新密钥，输入 'exit' 退出程序。")
    exist,public_key,private_key = load_exist_key()
    private_key = None
    if exist == False:
        print("key not exist,please generate new key")
    else:
        # push_homomorphic_publickey(public_key)
        pass

    while not stop_event.is_set():
        user_input = input("请输入命令：")  # 持续监听用户输入
        
        # 处理退出命令
        if user_input.lower() == 'exit':
            print("退出程序。")
            break
        
        # 检查用户输入
        if user_input.strip() == '-g':
            print("识别到命令：生成新密钥 and push to blockchain!")
            public_key,private_key =generate_new_key()
            push_homomorphic_publickey(public_key)
            # 在这里添加生成密钥的逻辑
        elif user_input.strip() == '-p':
            print("command:push to blockchain!")
            push_homomorphic_publickey(public_key)
            # 在这里添加生成密钥的逻辑
        elif user_input.strip() == '-s':
            print("Stopping threads...")
            stop_event.set()  # 设置标志位，通知其他线程停止
        else:
            print("未识别的命令。")

def load_exist_key():
    try:
        with open(key_file, 'r') as f:
            data = json.load(f)
            n = data['n']
            p = data['p']
            q = data['q']
            print(f"load n is len:{len(str(n))} {n}\r\n,p is len:{len(str(p))} {p}\r\n,q is :len:{len(str(q))} {q}\r\n")
            public_key = paillier.PaillierPublicKey(n)
            private_key = paillier.PaillierPrivateKey(public_key,p,q)
            return True,public_key,private_key
    except:
        return False,None,None

def generate_new_key():
    public_key, private_key = paillier.generate_paillier_keypair(n_length=1024)
    n = public_key.n
    p,q = private_key.p,private_key.q
    print(f"new n is len:{len(str(n))} {n}\r\n,p is len:{len(str(p))} {p}\r\n,q is :len:{len(str(q))} {q}\r\n")
    with open(key_file, 'w') as f:
        data = {'n':n, 'p':p, 'q':q}
        json.dump(data, f)
    return public_key,private_key


def push_homomorphic_publickey(public_key):
    n = public_key.n
    val = n.to_bytes((n.bit_length() + 7) // 8,byteorder='big')
    print(f"push publich to blockchain val is len:{len(val)} {val.hex()}")
    bc.UpdateHomomorphicKey(default_account,(val))

# 路由来处理网络请求
@app.route('/message', methods=['POST'])
def handle_message():
    data = request.json
    print(f"Received data from client: {data}")
    return jsonify({"response": "Hello, Client!"})

# 路由来处理网络请求
@app.route('/get_paillier_key', methods=['GET'])
def handle_get_paillier_key():
    print(f"received get_paillier_key")
    with open(key_file, 'r') as f:
        data = json.load(f)
    return jsonify({'response': data}), 200

# 启动 Flask 服务器线程
def run_flask_app():
    while not stop_event.is_set():
        app.run(host='127.0.0.1', port=65432, use_reloader=False)
if __name__ == "__main__":
    # 创建线程
    network_thread = threading.Thread(target=run_flask_app, daemon=True)
    input_thread = threading.Thread(target=main)

    # 启动线程
    network_thread.start()
    input_thread.start()

    # 等待输入线程结束
    input_thread.join()