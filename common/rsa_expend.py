def encrypt_in_chunks(data, cipher, chunk_size):
    encrypted_data = bytes(0)
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        encrypted_chunk = cipher.encrypt(chunk)
        encrypted_data = encrypted_data+(encrypted_chunk)
    return encrypted_data

def decrypt_in_chunks(encrypted_data, cipher, chunk_size):
    decrypted_data = bytes(0)
    for i in range(0, len(encrypted_data), chunk_size):
        chunk = encrypted_data[i:i + chunk_size]
        decrypted_chunk = cipher.decrypt(chunk)
        decrypted_data = decrypted_data + (decrypted_chunk)
    return (decrypted_data)