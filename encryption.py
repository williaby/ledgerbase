##: name = encryption.py
##: description = Flask utility for encrypting and decrypting sensitive data using Fernet # noqa: E501

##: category = security
##: usage = Import and use in Flask applications
##: behavior = Provides encryption and decryption of string values using keys from Flask config # noqa: E501

##: inputs = String values to encrypt/decrypt, Flask app config with LEDGERBASE_SECRET_KEYS # noqa: E501

##: outputs = Encrypted/decrypted string values
##: dependencies = Flask, cryptography.fernet
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

from typing import TypedDict, cast

from cryptography.fernet import Fernet, InvalidToken

from flask import current_app

"""Flask utility for encrypting and decrypting sensitive data.

This module provides a class for encrypting and decrypting string values
using Fernet symmetric encryption with keys stored in the Flask application
configuration. It supports key rotation by allowing multiple keys and
attempting decryption with each key in sequence.
"""


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
        config = cast("AppConfig", current_app.config)

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
