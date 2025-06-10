from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
# AES block size is 128 bits = 16 bytes
BLOCK_SIZE = 128

def generate_key_iv():
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)   # 128-bit IV
    return key, iv

def encrypt_aes(plaintext, key, iv):
    padder = padding.PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode()  # base64 encode to UTF-8 safe string

def decrypt_aes(b64_ciphertext, key, iv):
    ciphertext = base64.b64decode(b64_ciphertext.encode())  # decode base64 to bytes
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext.decode()

# Example usage
if __name__ == "__main__":
    key, iv = generate_key_iv()
    message = "Confidential Message"
    
    ciphertext = encrypt_aes(message, key, iv)
    print("Encrypted:", ciphertext.hex())

    decrypted = decrypt_aes(ciphertext, key, iv)
    print("Decrypted:", decrypted)
