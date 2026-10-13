from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from models.user import User
from schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str, tenant_id: Optional[UUID] = None) -> Optional[User]:
    query = db.query(User).filter(User.phone == phone)
    if tenant_id:
        query = query.filter(User.tenant_id == tenant_id)
    return query.first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, context_tenant_id: Optional[UUID] = None) -> User:
    user_data = user.model_dump()
    if context_tenant_id:
        user_data["tenant_id"] = context_tenant_id
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User) -> User:
    db.delete(db_user)
    db.commit()
    return db_user
