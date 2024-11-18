# blockchain imports
from web3 import Web3, HTTPProvider
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_abi import encode
from phe import paillier,command_line
# from web3.contract import ConciseContract

# other imports
import json
import colours
import sys,time
import os
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../common'))
import rsa_expend

web3Provider = 'http://127.0.0.1:8545/'
Contract_address = '0x5fbdb2315678afecb367f032d93f642f64180aa3'  #change every depoly
# owner = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
abi_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../EsoToken/artifacts/contracts/EsoToken.sol/EsoToken.json')

try:
    web3 = Web3(HTTPProvider(web3Provider))
    colours.printGreen("Connected to RPC blockchain endpoint on: "+web3Provider)
except:
    colours.printRed("Failed to connect to blockchain...closing")
    sys.exit()
_address = None
tokenContract = None

def loadTokenContract(address,abi_file):
    global tokenContract
    global _address
    _address = Web3.to_checksum_address(address)
    colours.printBlack("address is {}".format(_address))
    # if Web3.to_checksum_address(address) is not True:
    #     colours.printRed("Contract address toChecksumAddress failed...closing")
    #     sys.exit()
    if tokenContract == None:
        with open(abi_file) as f:
            abi = json.load(f)['abi']   #only need the abi part
        try:
            tokenContract = web3.eth.contract(abi=abi, address=_address)
            colours.printGreen("Token contract loaded!")
        except:
            colours.printRed("Token contract loading failed...closing")
            sys.exit()

def set_eth_balance(address,eth_count):
    web3.provider.make_request("hardhat_setBalance", [
        address,
        hex(Web3.to_wei(eth_count, 'ether'))
    ])

def getTokenContractAddress():
    return _address


# def getNodeAddress(meter_addr):
#     return web3.eth.accounts[Web3.to_checksum_address(meter_addr)]

def createAccount():
    return web3.eth.account.create()

def getBalance(address):
    return tokenContract.functions.getBalance(address).call()


def getTotalSupply():
    return tokenContract.functions.totalSupply().call() 


def getSymbol():
    return tokenContract.functions.symbol().call() 


def getName():
    return tokenContract.functions.name().call()    #or tokenContract.functions['name'].call()


def transfer(meter_addr,address_to, ammount):
    return tokenContract.transfer(address_to, ammount, transact={'from': web3.eth.accounts[meter_addr]})


def mintToken(account:LocalAccount,meter,value):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.meterMint(value,meter).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)  


def burnToken(meter_addr,value):
    return tokenContract.functions.burn(value, transact={'from': web3.eth.accounts[meter_addr]}).call()

def enroleMeter(account:LocalAccount,meterAddress,ownerAddress):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.enroleMeter(meterAddress, ownerAddress).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)  

def getmeterToOwner(meter_addr):
    return tokenContract.functions.meterToOwner(meter_addr).call()    #or tokenContract.functions['name'].call()


def mintTo(owner:LocalAccount,amount,recipient):
    transaction = {
        'nonce':web3.eth.get_transaction_count(owner.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.mintTo(amount, recipient).build_transaction(transaction)
    signed_df_tx = owner.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction) 

def _get_field_hex(x):
    return hex(x)[2:].zfill(32)

def _caculate_commit(price,quantity,is_bid):
    hex_str= _get_field_hex(price)+_get_field_hex(quantity)+_get_field_hex(is_bid)+_get_field_hex(0)
    data = int(hex_str,16).to_bytes(64, byteorder='big')
    return [bytes([d]) for d in (hashlib.sha256(data).digest() + bytes(32))]

def get_PaillierPublicKey():
    key = tokenContract.functions.getHomomorphicKey().call()
    # print(f"key type is {type(key)}, key is {key}")
    n = int.from_bytes(key, byteorder='big', signed=False)
    # print(f"len of n is {len(key)},n is {n} ")
    if n == 0:
        return None
    else:
        return paillier.PaillierPublicKey(n)

def SubmitCommit(account:LocalAccount,price:int,quantity:int,is_bid:int):
    commit_hash = _caculate_commit(price,quantity,is_bid)
    # print(f"commit_hash is {commit_hash},len is {len(commit_hash)}")
    public_key = get_PaillierPublicKey()
    if public_key is None:
        raise RuntimeWarning("PaillierPublicKey not exist !")
    price_commit_middle = price.to_bytes(4, byteorder='big')# + quantity.to_bytes(2, byteorder='big') + is_bid.to_bytes(1, byteorder='big')
    price_encrypt=public_key.encrypt(int.from_bytes(price_commit_middle, byteorder='big', signed=False))
    price_ciphertext = price_encrypt.ciphertext()
    price_exponent  = price_encrypt.exponent
    price_ciphertext_bytes = price_ciphertext.to_bytes((price_ciphertext.bit_length() + 7) // 8,byteorder='big')
    price_exponent_bytes = price_exponent.to_bytes((price_exponent.bit_length() + 7) // 8,byteorder='big')

    quantity_commit_middle = quantity.to_bytes(4, byteorder='big')# + quantity.to_bytes(2, byteorder='big') + is_bid.to_bytes(1, byteorder='big')
    quantity_encrypt=public_key.encrypt(int.from_bytes(quantity_commit_middle, byteorder='big', signed=False))
    quantity_ciphertext = quantity_encrypt.ciphertext()
    quantity_exponent  = quantity_encrypt.exponent
    quantity_ciphertext_bytes = quantity_ciphertext.to_bytes((quantity_ciphertext.bit_length() + 7) // 8,byteorder='big')
    quantity_exponent_bytes = quantity_exponent.to_bytes((quantity_exponent.bit_length() + 7) // 8,byteorder='big')

    print(len(price_ciphertext_bytes))
    print(len(price_exponent_bytes))
    print(len(quantity_ciphertext_bytes))
    print(len(quantity_exponent_bytes))
    commit_bytes = is_bid.to_bytes(1, byteorder='big') + quantity.to_bytes(4, byteorder='big') + \
        len(price_ciphertext_bytes).to_bytes(2, byteorder='big') + \
        len(price_exponent_bytes).to_bytes(2, byteorder='big')\
        + price_ciphertext_bytes+ price_exponent_bytes

    auctioneer_publickey_bytes = getAuctioneerKey()
    print(f"auctioneer_publickey_bytes is {auctioneer_publickey_bytes.hex()}")
    recover_key = RSA.import_key(auctioneer_publickey_bytes)
    pub_cipher_rsa = PKCS1_OAEP.new(recover_key)
    print(f"commit is {commit_bytes.hex()} \r\n,type is {type(commit_bytes)},type0 is {type(commit_bytes[0])} len is {len(commit_bytes)}")
    enc_commit_bytes = rsa_expend.encrypt_in_chunks(commit_bytes,pub_cipher_rsa,190)
    print(f"enc_commit_bytes type is {type(enc_commit_bytes)} len is {len(enc_commit_bytes)},is {enc_commit_bytes.hex()}")
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.SubmitCommit(commit_hash,enc_commit_bytes).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    txn_hash = web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)
    try:
        # 等待交易确认
        txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)
        
        # 检查交易状态
        if txn_receipt['status'] == 1:
            return 1
        else:
            return 0
    except :
        return 0

############secure_component#############################
def UpdateHomomorphicKey(account:LocalAccount,data):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }

    contruct_data = tokenContract.functions.UpdateHomomorphicKey(data).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)

############Auctioneer#############################
def UpdateAuctioneerKey(account:LocalAccount,data):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    contruct_data = tokenContract.functions.UpdateAuctioneerKey(data).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)

def getAuctioneerKey():
    return tokenContract.functions.getAuctioneerKey().call()

def get_participants():
    return tokenContract.functions.participants().call()

def get_commits_encryption():
    return tokenContract.functions.commits_encryption().call()

def FetchAllParticipants():
    return tokenContract.functions.FetchAllParticipants().call()

def FetchCommitsEncryption(index):
    return tokenContract.functions.FetchCommitsEncryption(index).call()

def UploadMarginalPriceFouce(account,price):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    contruct_data = tokenContract.functions.UploadMarginalPriceFouce(price).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)

def addBidBalance(account,target,token,electricity):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    contruct_data = tokenContract.functions.addBidBalance(target,token,electricity).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)

def addoOffBalance(account,target,token,electricity):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    contruct_data = tokenContract.functions.addoOffBalance(target,token,electricity).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction)
################ nft ####################################
def BidSubmit(account:LocalAccount,quantity,price):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.BidSubmit({'quantity':quantity, 'price':price}).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction) 

def offerSubmit(account:LocalAccount,quantity,price):
    transaction = {
        'nonce':web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.offerSubmit({'quantity':quantity, 'price':price}).build_transaction(transaction)
    signed_df_tx = account.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction) 

def settleDataContract(owner:LocalAccount):
    transaction = {
        'nonce':web3.eth.get_transaction_count(owner.address),
        'gas': 2000000,
        'maxFeePerGas': 2000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    
    contruct_data = tokenContract.functions.settleDataContract().build_transaction(transaction)
    signed_df_tx = owner.sign_transaction(contruct_data)
    web3.eth.send_raw_transaction(signed_df_tx.raw_transaction) 

def getFunctions():
    return tokenContract.all_functions()
