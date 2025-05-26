import os
from settings import ENCRYPTION_KEY
from cryptography.fernet import Fernet

"""
    This Class is used to encrypt and decrypt data in separate files. 
    In IoT devices, the key should be stored in a secure way, e.g. in a TPM or HSM.
"""

# https://cryptography.io/en/latest/fernet/

class EncryptionManager:
    MQTT_DATA_FILE = 'mqtt_settings.enc'

    def __init__(self):
        # Load the encryption key
        self.key = self._load_key_from_env()
        self.cipher_suite = Fernet(self.key)

    def _load_key_from_env(self):
        key_env = ENCRYPTION_KEY
        
        if key_env:
            try:
                key = key_env.encode() # Convert string to bytes
                Fernet(key)
                return key
            except (TypeError, ValueError):
                raise ValueError("Invalid encryption key format. Ensure it is a valid Fernet key.")
        else:
            raise ValueError("Encryption key not found in environment variables. Please set the ENCRYPTION_KEY variable.")

    def encrypt_data(self, data):
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        try:
            return self.cipher_suite.decrypt(encrypted_data).decode()
        except Exception as e:
            raise e

    def save_data(self, data, type):
        if type == "mqtt":
            file_path = self.MQTT_DATA_FILE
        else:
            raise ValueError("Unknown data type. Expected 'mqtt' or 'orion'.")

        # Write data to the corresponding file
        with open(file_path, 'wb') as file:
            file.write(data)

    def load_data(self, type):
        if type == "mqtt":
            file_path = self.MQTT_DATA_FILE
        else:
            raise ValueError("Unknown data type. Expected 'mqtt' or 'orion'.")

        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'rb') as file:
            return file.read()
