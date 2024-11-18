import sys,os,json,time,datetime,json
import colours
from eth_account import Account
from eth_account.signers.local import LocalAccount
import blockchainConnector as bc
from controllerSimulation import controllerSimulation
from controllerInterface import controllerBasic

Contract_address = '0x5fbdb2315678afecb367f032d93f642f64180aa3'  #change every depoly
owner = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
abi_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../EsoToken/artifacts/contracts/EsoToken.sol/EsoToken.json')

print(abi_file)
accounts_keys=["0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
        "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
        "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
        "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
        "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
        "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e"]
accounts=[Account.from_key(key) for key in accounts_keys]
meters=["0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
        "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",
        "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",
        "0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897",
        "0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82",
        "0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b1",
        "0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd"]
# returns current mWh power consumption/production
owner_account = Account.from_key(owner)
def loadContract():
    bc.loadTokenContract(address=Contract_address,abi_file=abi_file)

def create_meter():
    account=bc.createAccount()
    colours.printPurple("create new account,address:%s,private key :%s"%(account.address,account.key.hex()))

def enroleMeter(meter,owner):
    bc.enroleMeter(owner_account,meter,owner)

def mintTo(amount,to):
    bc.mintTo(owner_account,amount,to)
    colours.printGreen("mintTo")

def createUser(path):
    bc.loadTokenContract(address=Contract_address,abi_file=abi_file)
    file = 'user.json'
    file_path = os.path.join(path,file)
    if  os.path.exists(file):
        with open(file_path, "rb") as f:
            users = json.load(f)
            # print({f"users is {users}"})
            for user in users['users']:
                # print(f"user is {user}")
                token = bc.getBalance(user['address'])[0]
                # print(f"token of address:{user['address']} is {token},type:{type(token)}")
                if token <= 0:
                    account = Account.from_key(user['key'])
                    bc.set_eth_balance(account.address,100)
                    bc.mintTo(owner_account,1000000,user['address'])
    else:
        print(f"try load {file_path} fail")
        users={'users':[]}
        for count in range(0,100):
            account=bc.createAccount()
            bc.mintTo(owner_account,1000000,account.address)
            bc.set_eth_balance(account.address,100)
            user = {'address':account.address,'key':account.key.hex()}
            # print(f"user is {user}")
            users['users'].append(user)
            data = json.dumps(users)
            with open(file_path, "w",encoding='utf-8') as f:
                f.write(data)

if __name__ == '__main__':
    bc.loadTokenContract(address=Contract_address,abi_file=abi_file)
    createUser(os.path.dirname(os.path.abspath(__file__)))
    # participants = bc.FetchAllParticipants()
    # print(f"participants is {participants}")
    # CommitsEncryption = bc.FetchCommitsEncryption(0)
    # print(f"CommitsEncryption len:{len(CommitsEncryption)} is {CommitsEncryption}")
    # bc.mintTo(owner_account,80000,accounts[0].address)
    # balance = bc.getBalance(accounts[0].address)
    # print(f"token:{balance[0]},electricity:{balance[1]}")
    # bc.SubmitCommit(accounts[0],10000,10000000,0)
    # bc.BidSubmit(accounts[0] ,quantity=10000,price =7)
    # bc.BidSubmit(accounts[0] ,quantity=1250,price =7)
    # bc.offerSubmit(accounts[1] ,quantity=1000,price =6)
    # bc.offerSubmit(accounts[1] ,quantity=2000,price =7)
    # bc.offerSubmit(accounts[1] ,quantity=9000,price =6)
    # bc.settleDataContract(owner_account)
