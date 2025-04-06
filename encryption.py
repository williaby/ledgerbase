import os
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

class Encryptor:
    def __init__(self):
        keys = current_app.config.get("LEDGERBASE_SECRET_KEYS", [])
        if not keys:
            raise ValueError("No encryption keys defined.")
        self.primary_cipher = Fernet(keys[0].encode())
        self.secondary_ciphers = [Fernet(k.encode()) for k in keys[1:]]

    def encrypt(self, value: str) -> str:
        return self.primary_cipher.encrypt(value.encode()).decode()

    def decrypt(self, token: str) -> str:
        try:
            return self.primary_cipher.decrypt(token.encode()).decode()
        except InvalidToken:
            for cipher in self.secondary_ciphers:
                try:
                    return cipher.decrypt(token.encode()).decode()
                except InvalidToken:
                    continue
        raise ValueError("Decryption failed with all known keys.")
