from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from db import get_session

from models.user import User
from models.sentences import Sentences
from models.words import Words

from security.jwt import get_current_user

router = APIRouter(prefix="/sentence", tags=["saved sentences"])


@router.get("/", status_code=status.HTTP_200_OK)
def read_words(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get all saved sentences based on the user session"""
    # get sentences
    collections = db.exec(
        select(Sentences).where(Sentences.user_id == user.id).offset(skip).limit(limit)
    ).all()
    # return response
    return {
        "message": "successful sentences retrieval",
        "result": collections,
    }


@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_words_by_id(
    id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get a specific sentence by ID"""
    # get sentence by id
    sentence = db.exec(
        select(Sentences)
        .options(selectinload(Sentences.words))
        .where(Sentences.id == id, Sentences.user_id == user.id)
    ).first()
    # check if exist
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found"
        )
    # structure response
    result = {
        "id": sentence.id,
        "original": sentence.original,
        "original_lang": sentence.original_lang,
        "translation": sentence.translation,
        "translation_lang": sentence.translation_lang,
        "explanation": sentence.explanation,
        "user_id": sentence.user_id,
        "words": [
            {
                "id": word.id,
                "word": word.word,
                "desc": word.desc,
                "sentences_id": word.sentences_id,
            }
            for word in sentence.words
        ],
    }
    # return response
    return {
        "message": "successful sentence retrieval",
        "result": result,
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_words(
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete words by ID"""
    # get sentence by id
    sentence = db.exec(
        select(Sentences).where(
            Sentences.id == id, Sentences.user_id == current_user.id
        )
    ).first()
    # check if exist
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sentences not found"
        )
    # select all related words
    words_to_delete = db.exec(
        select(Words).where(Words.sentences_id == sentence.id)
    ).all()
    # delete the words
    for word in words_to_delete:
        db.delete(word)
    # delete sentence
    db.delete(sentence)
    db.commit()
    # return nothing
    return None
