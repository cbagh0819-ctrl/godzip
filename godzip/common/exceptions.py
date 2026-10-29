"""Exception hierarchy for GODZIP."""

class GodZipException(Exception):
    """Base exception for all GODZIP errors."""
    pass

class CorruptArchiveError(GodZipException):
    """Raised when an archive has an invalid header, checksum mismatch, or truncated payload."""
    pass

class UnsupportedVersionError(GodZipException):
    """Raised when encountering an unsupported format version."""
    pass

class UnsafePathError(GodZipException):
    """Raised when an archive member contains a path traversal or invalid path payload."""
    pass

class ChecksumMismatchError(GodZipException):
    """Raised when cryptographic digest verification fails."""
    pass

class InvalidPasswordError(GodZipException):
    """Raised when an incorrect password is provided for an encrypted archive."""
    pass

class ArchiveEncryptedError(GodZipException):
    """Raised when an encrypted archive is opened without providing a password."""
    pass

class DecompressionBombError(GodZipException):
    """Raised when a compressed block claims an expansion factor exceeding safety limits."""
    pass

class CodecNotFoundError(GodZipException):
    """Raised when encountering an unknown or unregistered codec ID."""
    pass

class JobCancelledError(GodZipException):
    """Raised when an active job is cancelled by the user."""
    pass
