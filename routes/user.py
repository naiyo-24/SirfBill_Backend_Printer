from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
import os
import aiofiles

from schemas.user import UserCreate, UserUpdate, User as UserSchema, UserAddress
from crud import user as crud_user
from models.database import get_db

from typing import List, Optional

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("", response_model=List[UserSchema])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Admin/CRM Action: Fetch a list of customers, optionally filtered by search term (name or phone) and tenant.
    """
    from models.user import User
    query = db.query(User).filter(User.role == "USER")
    
    if tenant_id:
        query = query.filter(User.tenant_id == tenant_id)
        
    if search:
        query = query.filter((User.name.ilike(f"%{search}%")) | (User.phone.ilike(f"%{search}%")))
        
    return query.offset(skip).limit(limit).all()


@router.post("/create", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if a user with this phone number already exists
    if user.phone:
        db_user = crud_user.get_user_by_phone(db, phone=user.phone, tenant_id=user.tenant_id)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with phone {user.phone} already exists ({db_user.name}). Please use the search bar."
            )
        
    return crud_user.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return db_user

@router.patch("/{user_id}", response_model=UserSchema)
def update_user(user_id: UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Check if phone is being updated and if it's already taken
    if user_update.phone and user_update.phone != db_user.phone:
        existing_phone = crud_user.get_user_by_phone(db, phone=user_update.phone, tenant_id=db_user.tenant_id)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Phone number already in use"
            )

    return crud_user.update_user(db=db, db_user=db_user, user_update=user_update)

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    user_id: UUID, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Patient Action: Upload a profile picture.
    Saves locally and updates the user's avatar_url.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    upload_dir = "./uploads/profiles"
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = file.filename or "avatar.jpg"
    if "." in filename:
        file_extension = filename.split(".")[-1].lower()
    else:
        file_extension = "jpg"
        
    file_path = f"{upload_dir}/user_{user_id}.{file_extension}"
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    import time
    public_url = f"/uploads/profiles/user_{user_id}.{file_extension}?v={int(time.time())}"
    
    user_update = UserUpdate(avatar_url=public_url)
    return crud_user.update_user(db=db, db_user=db_user, user_update=user_update)


@router.get("/{user_id}/upcoming-appointment")
def get_upcoming_appointment(user_id: UUID, db: Session = Depends(get_db)):
    """
    Patient Action: Fetch the next upcoming appointment for the home screen.
    """
    from models.appointment import Appointment
    from models.enums import BookingStatus
    from datetime import date
    
    appointment = (
        db.query(Appointment)
        .filter(Appointment.user_id == user_id)
        .filter(Appointment.status.in_([BookingStatus.PENDING_CONFIRMATION, BookingStatus.CONFIRMED]))
        .filter(Appointment.preferred_date >= date.today())
        .order_by(Appointment.preferred_date.asc())
        .first()
    )
    
    if not appointment:
        return None
        
    return {
        "id": str(appointment.id),
        "date": appointment.preferred_date.isoformat(),
        "time": appointment.form_details.get("time", "10:00 AM") if appointment.form_details else "10:00 AM",
        "doctor": {
            "name": appointment.doctor.name if appointment.doctor else "Assigned Doctor",
            "image_url": appointment.doctor.image_url if appointment.doctor else None,
        }
    }

@router.get("/{user_id}/appointments")
def get_user_appointments(user_id: UUID, db: Session = Depends(get_db)):
    """
    Patient Action: Fetch all appointments for a user.
    """
    from crud.appointment import get_appointments_by_user
    
    appointments = get_appointments_by_user(db, user_id=user_id)
    
    result = []
    for appt in appointments:
        doc = appt.doctor
        doc_name = "Assigned Doctor"
        doc_image = None
        doc_specialty = "General Physician"
        if doc:
            if isinstance(doc, dict):
                doc_name = doc.get('name', doc_name)
                doc_image = doc.get('image_url', doc_image)
                doc_specialty = doc.get('specialty', doc_specialty)
            else:
                doc_name = getattr(doc, 'name', doc_name)
                doc_image = getattr(doc, 'image_url', doc_image)
                doc_specialty = getattr(doc, 'specialty', doc_specialty)
                
        result.append({
            "id": str(appt.id),
            "date": appt.preferred_date.isoformat() if appt.preferred_date else None,
            "time": appt.form_details.get("time", "10:00 AM") if appt.form_details else "10:00 AM",
            "status": appt.status,
            "prescription_url": appt.prescription_url,
            "doctor": {
                "name": doc_name,
                "image_url": doc_image,
                "specialty": doc_specialty
            },
            "form_details": appt.form_details
        })
    return result

import uuid

@router.post("/{user_id}/address", response_model=UserSchema)
def add_user_address(
    user_id: UUID,
    address: UserAddress,
    db: Session = Depends(get_db)
):
    """
    Patient Action: Add a new delivery address.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    addresses = db_user.saved_addresses
    if not isinstance(addresses, list):
        addresses = []
        
    addr_dict = address.model_dump()
    addr_dict["id"] = str(uuid.uuid4())
    
    if addr_dict.get("is_default"):
        for a in addresses:
            a["is_default"] = False
            
    addresses.append(addr_dict)
    
    from sqlalchemy.orm.attributes import flag_modified
    db_user.saved_addresses = addresses
    flag_modified(db_user, "saved_addresses")
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}/address/{address_id}", response_model=UserSchema)
def update_user_address(
    user_id: UUID,
    address_id: str,
    address: UserAddress,
    db: Session = Depends(get_db)
):
    """
    Patient Action: Update a delivery address.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    addresses = db_user.saved_addresses
    if not isinstance(addresses, list):
        addresses = []
        
    found = False
    for a in addresses:
        if a.get("id") == address_id:
            addr_dict = address.model_dump()
            addr_dict["id"] = address_id
            if addr_dict.get("is_default"):
                for other in addresses:
                    other["is_default"] = False
            a.update(addr_dict)
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Address not found")
        
    from sqlalchemy.orm.attributes import flag_modified
    db_user.saved_addresses = addresses
    flag_modified(db_user, "saved_addresses")
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}/address/{address_id}", response_model=UserSchema)
def delete_user_address(
    user_id: UUID,
    address_id: str,
    db: Session = Depends(get_db)
):
    """
    Patient Action: Delete a delivery address.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    addresses = db_user.saved_addresses
    if not isinstance(addresses, list):
        addresses = []
        
    initial_len = len(addresses)
    addresses = [a for a in addresses if a.get("id") != address_id]
    
    if len(addresses) == initial_len:
        raise HTTPException(status_code=404, detail="Address not found")
        
    from sqlalchemy.orm.attributes import flag_modified
    db_user.saved_addresses = addresses
    flag_modified(db_user, "saved_addresses")
    db.commit()
    db.refresh(db_user)
    return db_user

from sqlalchemy.exc import IntegrityError
@router.delete("/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    try:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete customer because they have bills or appointments attached. Please mark them as Inactive instead."
        )
