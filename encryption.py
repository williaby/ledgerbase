from typing import cast

from cryptography.fernet import Fernet, InvalidToken

from config_types import AppConfig
from flask import current_app

# Assuming AppConfig is a TypedDict or similar structure defined elsewhere


class Encryptor:
    # Add '-> None' return type hint for the __init__ method
    def __init__(self) -> None:
        """
        Initializes the Encryptor with encryption keys from the app config.

        Raises:
            ValueError: If no LEDGERBASE_SECRET_KEYS are found in the config
                        or if the keys list is empty.
        """
        # current_app.config is Werkzeug's EnvironHeaders by default, but
        # Flask populates it. Casting assumes config structure matches AppConfig.
        config = cast(AppConfig, current_app.config)

        # Use .get() with a default empty list for safety
        # Consider logging a warning if keys are missing
        # instead of raising error immediately
        # depending on whether encryption is optional.
        keys: list[str] = config.get("LEDGERBASE_SECRET_KEYS", [])
        if not keys:
            # Make error message more specific
            raise ValueError(
                "Configuration error: 'LEDGERBASE_SECRET_KEYS' "
                "must be a non-empty list in Flask config."
            )

        # Store the compiled Fernet instances
        # Ensure keys are bytes for Fernet
        self.primary_cipher: Fernet = Fernet(keys[0].encode("utf-8"))
        self.secondary_ciphers: list[Fernet] = [
            Fernet(k.encode("utf-8")) for k in keys[1:]
        ]

    def encrypt(self, value: str) -> str:
        """Encrypts a string value using the primary key."""
        # Ensure input string is encoded to bytes before encryption
        encrypted_bytes: bytes = self.primary_cipher.encrypt(value.encode("utf-8"))
        # Decode the resulting bytes back to string for storage/transmission
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, token: str) -> str:
        """
        Decrypts a token string using the primary key, falling back to secondary keys.

        Args:
            token: The encrypted string token.

        Returns:
            The original decrypted string.

        Raises:
            ValueError: If decryption fails with all known keys.
        """
        try:
            # Encode the token string to bytes for decryption
            decrypted_bytes: bytes = self.primary_cipher.decrypt(token.encode("utf-8"))
            # Decode the resulting bytes back to the original string
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            # Only proceed to secondary keys if primary fails with InvalidToken
            pass  # Explicitly show we are ignoring the primary failure here

        for cipher in self.secondary_ciphers:
            try:
                decrypted_bytes = cipher.decrypt(token.encode("utf-8"))
                return decrypted_bytes.decode("utf-8")
            except InvalidToken:
                # Continue to the next key if decryption fails
                continue

        # If all keys failed
        raise ValueError("Decryption failed: Invalid token or unknown encryption key.")
