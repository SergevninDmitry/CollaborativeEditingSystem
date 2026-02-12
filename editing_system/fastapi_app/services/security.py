from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _pre_hash(password: str) -> str:
    """
    First step: convert any length password to fixed 64 hex symbols.
    This removes bcrypt 72-byte limitation.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    print(">>> HASH_PASSWORD CALLED")
    print("INPUT:", password)

    prepared = _pre_hash(password)

    print("PREPARED:", prepared)
    print("LENGTH:", len(prepared))

    return pwd_context.hash(prepared)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prepared = _pre_hash(plain_password)
    return pwd_context.verify(prepared, hashed_password)
