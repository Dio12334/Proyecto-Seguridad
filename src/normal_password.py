from Crypto.Cipher import AES

def AES_Encrypt(password, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(password.encode())
    return cipher.nonce, ciphertext, tag #returns nonce, cyphertext and tag

def AES_Decrypt(e_password, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce) 
    try:
        plaintext = cipher.decrypt_and_verify(e_password, tag)
        return plaintext.decode('utf-8')
    except (ValueError, KeyError):
        print("Incorrect Decryption")