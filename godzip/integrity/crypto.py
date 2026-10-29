"""Military-Grade Authenticated Encryption (AES-256-GCM) with PBKDF2 Key Derivation."""

import os
import struct
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from ..common.exceptions import (
    ChecksumMismatchError,
    InvalidPasswordError,
    ArchiveEncryptedError,
)

MAGIC_AUTH_TOKEN = b"GODZIP_AES256_AUTH_TOKEN_V1"  # 28 bytes
PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16
NONCE_SIZE = 12
AUTH_HEADER_SIZE = SALT_SIZE + NONCE_SIZE + len(MAGIC_AUTH_TOKEN) + 16  # 72 bytes


class ArchiveCrypto:
    """Handles key derivation, password authentication, and AES-256-GCM block encryption."""

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 256-bit AES key from the password and salt using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return kdf.derive(password.encode("utf-8"))

    @classmethod
    def generate_auth_header(cls, password: str) -> Tuple[bytes, bytes]:
        """Generates (encryption_key, serialized_auth_header).
        
        Auth Header layout (72 bytes):
        - Salt: 16 bytes
        - Nonce: 12 bytes
        - Ciphertext of MAGIC_AUTH_TOKEN: 44 bytes (28 bytes plaintext + 16 bytes GCM tag)
        """
        salt = os.urandom(SALT_SIZE)
        key = cls.derive_key(password, salt)
        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(key)
        encrypted_token = aesgcm.encrypt(nonce, MAGIC_AUTH_TOKEN, associated_data=b"GODZIP_SALT_AUTH")
        
        header_payload = salt + nonce + encrypted_token
        return key, header_payload

    @classmethod
    def verify_auth_header(cls, password: str, header_payload: bytes) -> bytes:
        """Verifies password against auth header and returns the 256-bit key.
        
        Raises InvalidPasswordError if password is wrong or auth header is corrupted.
        """
        if len(header_payload) < AUTH_HEADER_SIZE:
            raise InvalidPasswordError("Corrupted encryption authentication header")
        
        salt = header_payload[:SALT_SIZE]
        nonce = header_payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        encrypted_token = header_payload[SALT_SIZE + NONCE_SIZE:AUTH_HEADER_SIZE]

        key = cls.derive_key(password, salt)
        aesgcm = AESGCM(key)
        try:
            decrypted = aesgcm.decrypt(nonce, encrypted_token, associated_data=b"GODZIP_SALT_AUTH")
            if decrypted != MAGIC_AUTH_TOKEN:
                raise InvalidPasswordError("Incorrect archive password")
        except Exception:
            raise InvalidPasswordError("Incorrect archive password")

        return key

    @staticmethod
    def encrypt_block(data: bytes, key: bytes, block_id: int) -> bytes:
        """Encrypts a payload block using AES-256-GCM with a fresh 12-byte nonce.
        
        Prepends the 12-byte nonce to the ciphertext (which includes the 16-byte GCM tag).
        """
        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(key)
        ad = struct.pack("<I", block_id)
        ciphertext = aesgcm.encrypt(nonce, data, associated_data=ad)
        return nonce + ciphertext

    @staticmethod
    def decrypt_block(encrypted_payload: bytes, key: bytes, block_id: int) -> bytes:
        """Decrypts an AES-256-GCM payload block, validating authenticity tag.
        
        Raises ChecksumMismatchError if tampered with or corrupted.
        """
        if len(encrypted_payload) < NONCE_SIZE + 16:
            raise ChecksumMismatchError("Encrypted block payload is truncated")
        
        nonce = encrypted_payload[:NONCE_SIZE]
        ciphertext = encrypted_payload[NONCE_SIZE:]
        aesgcm = AESGCM(key)
        ad = struct.pack("<I", block_id)
        try:
            return aesgcm.decrypt(nonce, ciphertext, associated_data=ad)
        except Exception:
            raise ChecksumMismatchError(f"Block {block_id} cryptographic authenticity check failed (tampered/corrupted)")
