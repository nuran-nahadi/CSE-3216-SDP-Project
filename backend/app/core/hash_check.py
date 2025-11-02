from passlib.context import CryptContext
import uuid

# Set up the CryptContext with bcrypt as the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the function to hash a password
def hash_password(password: str) -> str:
    # Hash the password using the pwd_context
    hashed_password = pwd_context.hash(password)
    return hashed_password

# Example usage
hashed = hash_password("r")
print(hashed)

gener_uuid = uuid.uuid4()
print(gener_uuid)