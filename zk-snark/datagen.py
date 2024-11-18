import hashlib

def get_field_hex(x):
    return hex(x)[2:].zfill(32)
def gen_commit(price,quantity,is_bid):
    hex_str= get_field_hex(price)+get_field_hex(quantity)+get_field_hex(is_bid)+get_field_hex(0)
    print(hex_str)
    return int(hex_str,16)
def hex_address_to_u128_array(hex_address):
    # 去掉前缀 '0x'（如果有）
    hex_address = hex_address[2:] if hex_address.startswith("0x") else hex_address
    
    # 确保地址长度为 40 位，不足时左侧补零
    hex_address = hex_address.zfill(64)
    
    # 将地址按 8 个字符分割，每组代表 32 位，转换为 u32（十进制）
    u128_array = [int(hex_address[i:i+32], 16) for i in range(0, 64, 32)]
    
    return u128_array

def hash(data):
    data = data.to_bytes(64, byteorder='big')

    return hex_address_to_u128_array(hashlib.sha256(data).hexdigest())

bid = [(1,100),(3,10),(4,100),(5,10),(0,0)]
offer = [(1,100),(2,15),(2,15),(10,2),(0,0)]


result = []
marginal_price = 2


print(hash(3))
print(hash(10))
[315183849169039769787337783070380158893, 194579621010258067005997479343992009370]
[261673453623746781313652579402536373323, 140016560968775928873505512069829327042]
result.append(marginal_price)
for i in range(len(bid)):
    a = hash(i)
    result.extend(a)
    for e in bid[i]:
        result.append(e)

for i in range(len(offer)):
    a = hash(5+i)
    result.extend(a)
    
    for e in offer[i]:
        result.append(e)

for i in range(len(bid)):
    a = hash(i)
    result.extend(a)
    if(bid[i][0]==0):
        result.extend([0,0])
    else:
        c = gen_commit(bid[i][0],bid[i][1],1)
        c_hash = hash(c)
        print(hex(c),c_hash)
        result.extend(c_hash)
    
for i in range(len(offer)):
    a = hash(5+i)
    result.extend(a)
    if(offer[i][0]==0):
        result.extend([0,0])
    else:
        c = gen_commit(offer[i][0],offer[i][1],0)
        c_hash = hash(c)
        result.extend(c_hash)

print(len(result))
for e in result:
    print(e, end=" ")