from typing import TypedDict, cast

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


class AppConfig(TypedDict):
    """TypedDict for Flask app configuration."""

    LEDGERBASE_SECRET_KEYS: list[str]


class DecryptionError(ValueError):
    """Custom exception for decryption errors."""

    DEFAULT_MESSAGE = "Decryption failed: Invalid token or unknown encryption key."


class Encryptor:
    """Encrypts and decrypts string values using Fernet keys from app config."""

    CONFIG_ERROR_MSG = (
        "Configuration error: 'LEDGERBASE_SECRET_KEYS' must be a non-empty "
        "list in Flask config."
    )

    def __init__(self) -> None:
        """Initialize the Encryptor with encryption keys from the app config.

        Raises
        ------
        ValueError
            If no LEDGERBASE_SECRET_KEYS are found in the config or
            if the keys list is empty.

        """
        config = cast(AppConfig, current_app.config)

        keys: list[str] = config.get("LEDGERBASE_SECRET_KEYS", [])
        if not keys:
            raise ValueError(self.CONFIG_ERROR_MSG)

        self.primary_cipher: Fernet = Fernet(keys[0].encode("utf-8"))
        self.secondary_ciphers: list[Fernet] = [
            Fernet(k.encode("utf-8")) for k in keys[1:]
        ]

    def encrypt(self, value: str) -> str:
        """Encrypt a string value using the primary key.

        Parameters
        ----------
        value : str
            The string value to encrypt.

        Returns
        -------
        str
            The encrypted string.

        """
        encrypted_bytes: bytes = self.primary_cipher.encrypt(value.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, token: str) -> str:
        """Decrypt a token using the primary key, then fall back to secondary keys.

        Parameters
        ----------
        token : str
            The encrypted string token.

        Returns
        -------
        str
            The original decrypted string.

        Raises
        ------
        DecryptionError
            If decryption fails with all known keys.

        """
        for cipher in [self.primary_cipher, *self.secondary_ciphers]:
            try:
                decrypted_bytes = cipher.decrypt(token.encode("utf-8"))
                return decrypted_bytes.decode("utf-8")
            except InvalidToken:
                continue

        error_message = DecryptionError.DEFAULT_MESSAGE
        raise DecryptionError(error_message)
