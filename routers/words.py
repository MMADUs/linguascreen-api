from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from db import get_session
from models.user import User
from models.words import Words, WordsPayload, WordsResponse
from security.jwt import get_current_user

router = APIRouter(prefix="/words", tags=["words"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WordsResponse)
def create_words(
    req_body: WordsPayload,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Save a new words to dictionary"""
    # Create data with current user as owner
    data = Words(
        original=req_body.original,
        original_lang=req_body.original_lang,
        translation=req_body.translation,
        translation_lang=req_body.translation_lang,
        description=req_body.description,
        user_id=current_user.id,
    )

    # Add to database
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[WordsResponse])
def read_words(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all saved words based on the user session"""
    collections = db.exec(
        select(Words).where(Words.user_id == current_user.id).offset(skip).limit(limit)
    ).all()

    return collections


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=WordsResponse)
def read_words_by_id(
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific words by ID"""
    data = db.exec(
        select(Words).where(Words.id == id, Words.user_id == current_user.id)
    ).first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Words not found"
        )

    return data


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=WordsResponse)
def update_words(
    id: int,
    req_body: WordsPayload,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update words by ID"""
    data = db.exec(
        select(Words).where(Words.id == id, Words.user_id == current_user.id)
    ).first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Words not found"
        )

    # Update item attributes
    item_data = req_body.dict(exclude_unset=True)
    for key, value in item_data.items():
        setattr(data, key, value)

    # Ensure owner_id remains the same
    data.user_id = current_user.id

    # Save changes
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_words(
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete words by ID"""
    data = db.exec(
        select(Words).where(Words.id == id, Words.user_id == current_user.id)
    ).first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Words not found"
        )

    # Delete item
    db.delete(data)
    db.commit()

    return None
