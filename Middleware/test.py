from web3 import Web3, Account
import json

# 连接到Hardhat本地网络
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# 检查连接
if not w3.isConnected():
    print("Failed to connect to Hardhat network")
    exit()

# 存储账户信息
accounts_info = []

# 创建1000个账户
for _ in range(1000):
    # 生成新的账户
    account = Account.create()
    
    # 设置账户余额为100 ETH（转换为十六进制字符串，单位为wei）
    w3.provider.make_request("hardhat_setBalance", [
        account.address,
        hex(Web3.toWei(100, 'ether'))
    ])
    
    # 保存账户地址和私钥
    accounts_info.append({
        "address": account.address,
        "private_key": account.privateKey.hex()
    })

# 将账户信息写入JSON文件
with open('accounts_info.json', 'w') as file:
    json.dump(accounts_info, file, indent=4)

print("已创建1000个账户，并将地址和私钥写入accounts_info.json文件")
