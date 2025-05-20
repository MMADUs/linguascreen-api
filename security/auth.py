from passlib.context import CryptContext
from sqlmodel import Session, select

from models.user import User

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify hashed password match"""
    return hash_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash from plain password"""
    return hash_context.hash(password)


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by username"""
    return db.exec(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, id: int) -> User:
    """Get user by id"""
    return db.exec(select(User).where(User.id == id)).first()


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
