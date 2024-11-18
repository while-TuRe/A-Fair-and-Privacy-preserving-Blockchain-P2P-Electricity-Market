from phe import paillier,command_line
import json,sys,os,threading,random,requests
middleware = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../Middleware')
sys.path.append(middleware)
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../common'))
import blockchainConnector as bc
import rsa_expend
from eth_account import Account
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import DSS
from Crypto.Random import get_random_bytes

key_file = 'private.pem'
default_account = Account.from_key("0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a")
paillier_random =0
# key = RSA.generate(2048)
# data = key.public_key().export_key(format='DER')
# print(f"data lenis {len(data)} is {data}")
# recover_key = RSA.import_key(data)
# print(f"recover_key data is {key.public_key().export_key()}")

# session_key = bytes([1,2,3,4,5,6])
# pub_cipher_rsa = PKCS1_OAEP.new(recover_key)
# enc_session_key = pub_cipher_rsa.encrypt(session_key)
# pri_cipher_rsa =PKCS1_OAEP.new(key)
# recover_session_key = pri_cipher_rsa.decrypt(enc_session_key)
# message = get_random_bytes(2000)
# encrypted_data = rsa_expend.encrypt_in_chunks(message,pub_cipher_rsa,190)
# print(f"encrypted_data len:{len(encrypted_data),type is {type(encrypted_data)}}")
# decrypted_data = rsa_expend.decrypt_in_chunks(encrypted_data,pri_cipher_rsa,key.size_in_bytes())
# print(f"decrypted_data len:{len(decrypted_data),type is {type(decrypted_data)}}")
# print(f"result is :{message==decrypted_data}")
# exit()



def main():
    bc.loadTokenContract(bc.Contract_address,bc.abi_file)
    print("输入 -g 生成新密钥，输入 'exit' 退出程序。")
    exist,key = load_exist_key()
    if exist == False:
        print("key not exist,please generate new key")
    else:
        # push_auctioneer_publickey(key)
        pass

    while True:  # 检查标志位是否被设置
        user_input = input("请输入命令：")  # 持续监听用户输入
        
        # 处理退出命令
        if user_input.lower() == 'exit':
            print("退出程序。")
            break
        
        # 检查用户输入
        if user_input.strip() == '-g':
            print("识别到命令：生成新密钥 and push to blockchain!")
            key =generate_new_key()
            push_auctioneer_publickey(key)
        elif user_input.strip() == '-p':
            print("command:push to blockchain!")
            push_auctioneer_publickey(key)
        elif user_input.strip() == '-s':
            print("settlement!")
            settlement(key)
            # 在这里添加生成密钥的逻辑
        elif user_input.strip() == '-q':
            print("query_paillier_key!")
            query_paillier_key()
        else:
            print("未识别的命令。")

def load_exist_key():
    try:
        with open(key_file, "rt") as f:
            data = f.read()
            mykey = RSA.import_key(data)
            return True, mykey
    except:
        return False,None

def generate_new_key():
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open(key_file, "wb") as f:
        f.write(private_key)
    return key


def push_auctioneer_publickey(key):
    data = key.public_key().export_key(format='DER')
    print(f"push key to blockchain val is len:{len(data)},type:{type(data)} {data.hex()}")
    bc.UpdateAuctioneerKey(default_account,(data))

    # commit_bytes = len(price_ciphertext_bytes).to_bytes(2, byteorder='big') + len(price_exponent_bytes).to_bytes(2, byteorder='big')\
    #     + len(quantity_ciphertext_bytes).to_bytes(2, byteorder='big') + len(quantity_exponent_bytes).to_bytes(2, byteorder='big')\
    #     + price_ciphertext_bytes+ price_exponent_bytes + quantity_ciphertext_bytes + quantity_exponent_bytes

def query_paillier_key():
    response  = requests.get('http://127.0.0.1:65432/get_paillier_key')
    # print(f"query_paillier_key response is {response.json()}")
    data = response.json()['response']
    n = data['n']
    p = data['p']
    q = data['q']
    print(f"load n is len:{len(str(n))} {n}\r\n,p is len:{len(str(p))} {p}\r\n,q is :len:{len(str(q))} {q}\r\n")
    public_key = paillier.PaillierPublicKey(n)
    private_key = paillier.PaillierPrivateKey(public_key,p,q)
    return True,public_key,private_key

class CommitInfo:
    def __init__(self,address,is_bid,price,quantity) -> None:
        self.address = address
        self.is_bid =is_bid
        self.price =price
        self.quantity =quantity
        self.actual_quantity = 0
Commits :list[CommitInfo]= []
def settlement(key):
    paillier_random = random.randint(0,100)
    exist,public_key,private_key = query_paillier_key()
    if not exist:
        print("query_paillier_key fail")
        exit()
    pri_cipher_rsa =PKCS1_OAEP.new(key)
    participants = bc.FetchAllParticipants()
    CommitsEncryption = []
    # print(f"publickey_bytes is {key.public_key().export_key(format='DER').hex()}")
    Commits :list[CommitInfo]= []
    for i in range(0,len(participants)):
        Commit = bc.FetchCommitsEncryption(i)
        # print(f"index:{i} len{len(Commit)}, is {Commit.hex()}")
        decrypted_data = rsa_expend.decrypt_in_chunks(Commit,pri_cipher_rsa,key.size_in_bytes())
        # print(f"\r\ndecrypt data is:{i} len{len(decrypted_data)}, is {decrypted_data.hex()}")
        CommitsEncryption.append(decrypted_data)
        is_bid = int.from_bytes(decrypted_data[0:1], byteorder='big', signed=False)
        offset = 1
        quantity = int.from_bytes(decrypted_data[offset:offset+4], byteorder='big', signed=False)
        offset = offset+4
        price_ciphertext_bytes_len = int.from_bytes(decrypted_data[offset:offset+2], byteorder='big', signed=False)
        offset=offset+2
        price_exponent_bytes_len = int.from_bytes(decrypted_data[offset:offset+2], byteorder='big', signed=False)
        offset=offset+2
        price_ciphertext_bytes = int.from_bytes(decrypted_data[offset:offset+price_ciphertext_bytes_len], byteorder='big', signed=False)
        offset = offset + price_ciphertext_bytes_len
        price_exponent_bytes = int.from_bytes(decrypted_data[offset:offset+price_exponent_bytes_len], byteorder='big', signed=False)
        recover_pub_key = bc.get_PaillierPublicKey()
        price_rec = paillier.EncryptedNumber(recover_pub_key, int(price_ciphertext_bytes), int(price_exponent_bytes))
        price = private_key.decrypt(price_rec)
        Commits.append(CommitInfo(participants[i],is_bid,price,quantity))
        print(f"settlement {i}:decript price is {price}")
    print(f"participants is {participants}")
    marginal_price = caculate_marginal_price(Commits)
    bc.UploadMarginalPriceFouce(default_account,marginal_price)
    


#participants is {'price':int,'quantity':int,'is_bid':bool}
def caculate_marginal_price(Commits:list[CommitInfo]):
    Commits_sorted = sorted(Commits, key=lambda commit: commit.price)
    bids = [commit for commit in Commits if commit.is_bid==1]
    sort_bids = sorted(bids, key=lambda commit: commit.price)
    offs = [commit for commit in Commits if not commit.is_bid]
    if len(bids) == 0 or len(offs) == 0 :
        return 0
    sort_offs = sorted(offs, key=lambda commit: commit.price)
    supply = 0
    demand = 0
    marginal_supply = 0
    marginal_demand = 0
    max_trading_volume = 0
    trading_volume = 0
    marginal_price = 0
    for j in range(0,len(sort_bids)):
        # print("sort_bids[%d] price:%d,quantity:%d",j,sort_bids[j].price, sort_bids[j].quantity)
        demand = demand+sort_bids[j].quantity
    # print("all demand is %d",demand)
    j = 0
    i = 0
    last_j =0
    while i<len(sort_offs):
        supply = supply+sort_offs[i].quantity
        # print("sort_offs[%d] price:%d,quantity:%d",i,sort_offs[i].price,sort_offs[i].quantity)
        bid_index =0

        while j<len(sort_bids):
            # print(f"********sort_bids :{sort_bids[j].price},{sort_offs[i].price}")
            if sort_bids[j].price < sort_offs[i].price:
                demand = demand-sort_bids[j].quantity
                j=j+1
            else:
                break
        print(f"supply:{supply},demand:{demand},i:{i},j:{j}")
        if(supply >= demand) :
            trading_volume = demand
        else:
            trading_volume = supply
        if(trading_volume >= max_trading_volume):
            max_trading_volume = trading_volume
            marginal_supply = supply
            marginal_demand = demand
            marginal_price = sort_offs[i].price
            last_j = j
        else:    # last price is marginal_price
            i = i-1
            j = last_j
            break
        if(i+1 < len(sort_offs)):
            i = i+1
        else:
            break
    if(marginal_supply >= marginal_demand):
        excess_supply = marginal_supply-marginal_demand
        while i>=0:
            print("2 i:%d,j:%d",i,j)
            if(excess_supply == 0):
                sort_offs[i].actual_quantity = sort_offs[i].quantity
            elif (sort_offs[i].quantity <= excess_supply):
                excess_supply =excess_supply-sort_offs[i].quantity
                sort_offs[i].actual_quantity =0
            else:
                sort_offs[i].actual_quantity = sort_offs[i].quantity - excess_supply
                excess_supply = 0
            if(i>0) :
                i=i-1
            else:
                break
        while j< len(sort_bids):
            print("3 i:%d,j:%d",i,j)
            sort_bids[j].actual_quantity = sort_bids[j].quantity
            j=j+1
    else:
        excess_consumer = marginal_demand - marginal_supply
        while j< len(sort_bids):
            print("4 i:%d,j:%d",i,j)
            if(excess_consumer == 0):
                sort_bids[j].actual_quantity = sort_bids[j].quantity
            elif (sort_bids[j].quantity <= excess_consumer):
                excess_consumer =excess_consumer-sort_bids[j].quantity
                sort_bids[j].actual_quantity = 0
            else:
                sort_bids[j].actual_quantity = sort_bids[j].quantity - excess_consumer
                excess_consumer = 0
            j = j+1
        while i>=0:
            print("5 i:%d,j:%d",i,j)
            sort_offs[i].actual_quantity = sort_offs[i].quantity
            if (i>0):
                i=i-1
            else:
                break
    print("marginal_price:%d,max_trading_volume:%d,marginal_supply:%d,marginal_demand:%d"%(marginal_price,max_trading_volume,marginal_supply,marginal_demand))  
    for bid in sort_bids:
        print(f"bid: price:{bid.price},quantity:{bid.quantity},actual_quantity:{bid.actual_quantity}")
        if bid.actual_quantity!=0:
            bc.addBidBalance(default_account,bid.address,marginal_price*bid.actual_quantity, bid.actual_quantity)
    for off in sort_offs:
        print(f"off: price:{off.price},quantity:{off.quantity},actual_quantity:{off.actual_quantity}")
        if off.actual_quantity!=0:
            bc.addoOffBalance(default_account,off.address,marginal_price*off.actual_quantity, off.actual_quantity)
    return marginal_price

if __name__ == "__main__":
    # 创建线程
    main()
    #test
    # commits=[]
    # commits.append(CommitInfo(bytes(0),0,10,100))
    # commits.append(CommitInfo(bytes(1),0,9,80))
    # commits.append(CommitInfo(bytes(2),0,8,60))
    # commits.append(CommitInfo(bytes(3),0,7,30))
    # commits.append(CommitInfo(bytes(3),0,6,200))

    # commits.append(CommitInfo(bytes(4),1,6,100))
    # commits.append(CommitInfo(bytes(5),1,7,55))
    # commits.append(CommitInfo(bytes(6),1,8,40))
    # commits.append(CommitInfo(bytes(7),1,10,5))
    # caculate_marginal_price(commits)