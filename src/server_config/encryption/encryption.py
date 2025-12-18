from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from base64 import urlsafe_b64encode

from src.server_config.config import Config
from  os import urandom
import sys
## 2 tier key system 
## 1 tier is for verification purpose only
## 2 is for encryption and decryption
## Note do not store 2nd as file it will live as a local variable 
## 

class Encryption:
    def generate_salt(self):
        salt = os.urandom(16) # note salt are binary, so would have to convert to hex to store, and to binary when read
        return salt

    def generate_kdf(self,salt):
        if salt is None : return None, False
        return PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100_000,
                backend=default_backend()
            ),True

    def generate_hkdf(self,info):
        return HKDF(
            algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=info,
                backend=default_backend()
        )
    def generate_service_key(self,key,info):
        hkdf = self.generate_hkdf(info)
        return hkdf.derive(key)

    def derive_combination_key(self,key1,key2,info):
        combined = key1+key2
        hkdf = self.generate_hkdf(info)
        return hkdf.derive(combined)
    def generate_key(self,kdf,password):
    
        if kdf is None or password is None: 
            return None, False
        key = kdf.derive(password.encode())
        return key, True
    
    def generate_iv (self):
        iv = urandom(16)
        return iv

       
    def encrypt(self,value,key):
        print(value)
        try:
            if isinstance(value,str):
                value = value.encode()
            print(value)
            iv = self.generate_iv()
            padder = padding.PKCS7(128).padder()# padding to 128 bit block (convert 16 bytes block)
            padder_data = padder.update(value)+padder.finalize() # padding value to 16 bytes block
            cipher = Cipher (algorithms.AES(key),modes.CBC(iv),backend=default_backend()) #options of cipher
            encryptor = cipher.encryptor()#Prepares the cipher for encryption.
            ciphertext = encryptor.update(padder_data)+encryptor.finalize() #encrypt and add the remainder
            return ciphertext.hex(),iv
        except Exception as e :
            raise RuntimeError(f"Encryption failed: {e}")

    def decrypt(self,iv,encrypted,key):
   

        try:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt first
            decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()

            # Then unpad
            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
            return decrypted.decode()
        except Exception as e :
            if "Invalid padding" in str(e):
                print("Wrong password❌")
                sys.exit(1)  # or sys.exit(1) or raise a custom error
            else:
                # unexpected: log full details then show a short message
                import logging
                logging.exception("Unexpected decryption error")
                print("Something went wrong during decryption.")
                sys.exit(1)


