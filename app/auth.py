from passlib.context import CryptContext

# Argon2id: memory-hard and has no fixed byte-length limit on the password,
# unlike bcrypt.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)