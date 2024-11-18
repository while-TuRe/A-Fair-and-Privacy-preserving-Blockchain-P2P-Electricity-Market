from flask import Flask,jsonify
from flask_cors import CORS  # 导入 CORS
from flask import request
from flask import make_response
from eth_account import Account
import sys,os,traceback
import hashlib
from typing import Dict
middleware = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../Middleware')
sys.path.append(middleware)
import blockchainConnector as bc
import tool as mytool

app = Flask(__name__)
# 设置日志级别
app.logger.setLevel('ERROR')  # 只显示错误信息，关闭其他信息
CORS(app)  # 启用 CORS
Contract_address = '0x5fbdb2315678afecb367f032d93f642f64180aa3'  #change every depoly
# owner = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
abi_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../EsoToken/artifacts/contracts/EsoToken.sol/EsoToken.json')
bc.loadTokenContract(address=Contract_address,abi_file=abi_file)
g_user :Dict[str,Account]= {}
g_balance :Dict[str,Dict]={}# address:{'token':int,'electricity':int}
mytool.createUser(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def home():
    return 'Welcome to the Home Page!'

@app.route('/about')
def about():
    return 'This is the About Page.'

@app.route('/submit', methods=['POST'])
def submit():
    g_username = request.form.get('g_username')
    return f'Hello, {g_username}!'

@app.route('/custom_response')
def custom_response():
    response = make_response('This is a custom response!')
    response.headers['X-Custom-Header'] = 'Value'
    return response

@app.route('/login', methods=['POST'])
def login():
    global g_user
    try:
        print(f"request.json:{request.json},type:{type(request.json)}")
        address = request.json['address']
        pri_key = request.json['key']
    except:
        data = f'paraments wrong:{request.json}'
        status =1
        return jsonify({"error": "Missing address or key","data":data,"status":status}), 400
    try:
        account = Account.from_key(pri_key)
    except:
        data = f'key wrong:{request.json}'
        status =1
        return jsonify({"error": "wrong key","data":data,"status":status}), 400
    if account.address == address:
        g_user[account.address] = account
        status =1
        data = 'login success'
        g_balance[account.address] = {'token':0,'electricity':0}
        return jsonify({"data":data,"status":status}), 200
    else:
        data = 'address and key not match'
        error =data
        status =2
        return jsonify({"error":error,"data":data,"status":status}), 400 

@app.route('/board', methods=['POST'])
def process_board_post():
    print(f"receive board args:{request.args},data:{request.json}")
    # 获取请求参数
    method = request.json.get('method')
    global g_user
    if method == 'order':
        try:
            price = request.json['order']['price']
            quantity = request.json['order']['quantity']
            is_bid = int(request.json['order']['is_bid'])
            address = request.json.get('user')
            if address not in g_user:
                print(f"address :{address} not login,g_user:{g_user}")
                data = 'not login '
                return make_response(jsonify({'error': 'order fail','msg':data}), 400)
            if price <= 0 or quantity<=0 or is_bid>1:
                msg = f'paraments wrong:{request.json}'
                return make_response(jsonify({'msg':msg}), 400)
            user = g_user[address]
            if is_bid==1 :
                require_token = price*quantity
                balance_token=  g_balance[address]['token']
                print(f"address :{address} require_token:{require_token},balance_token:{balance_token}")
                if require_token>balance_token:
                    data = 'token not enough'
                    return make_response(jsonify({'msg':data}), 400)
        except:
            msg = f'paraments miss:{request.json}'
            print(msg)
            return make_response(jsonify({'msg':msg}), 400)
        try:
            result = bc.SubmitCommit(user,price,quantity,is_bid)
        except:
            msg = f'SubmitCommit fail:{request.json}'
            print(f"SubmitCommit fail,{sys.exc_info()}")
            print(traceback.print_exc())
            print(traceback.format_exc())
            return make_response(jsonify({'error': 'SubmitCommit fail','msg':msg}), 400)
        # 返回余额数据
        return make_response(jsonify({'msg':'success'}), 200,)
    else:
        print(f"process_board_post receive board method:{method}")
        return make_response(jsonify({'error': 'Invalid method','msg':msg}), 400)

@app.route('/board', methods=['GET'])
def process_board_get():
    print("receive process_board_get")
    # 获取请求参数
    method = request.args.get('method')
    global g_user
    if method == 'balance':
        balance_data = {
        'token': 0,  # 示例 token 余额
        'electricity': 0  # 示例电量余额
        }
        try:
            address = request.args.get('user')
            if address not in g_user:
                print(f"address :{address} not login,g_user:{g_user}")
                data = 'not login '
                return jsonify({'error': 'getBalance fail',data:'data'}), 400
            user = g_user[address]
            balance_data['token'],balance_data['electricity'] = bc.getBalance(user.address)
        except:
            print(f"getBalance fail {address},user.address:{user.address}")
            data = 'getBalance fail'
            return jsonify({'error': 'getBalance fail','data':data}), 400
        # 返回余额数据
        g_balance[address] = balance_data 
        return jsonify({'balance': balance_data}), 200
    else:
        print(f"receive board method:{method}")
        return jsonify({'error': 'Invalid method'}), 400

@app.errorhandler(Exception)
def handle_exception(e):
    # 打印错误信息
    print(e)
    return {'status': 'error', 'message': str(e)}, 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5123, debug=True)  # 监听所有可用的网络接口