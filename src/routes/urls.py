from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database.database import get_db
from .views import (
    upload_file_view, list_files_view,
    most_repeated_words_view, least_repeated_words_view,
    analyze_files_view, download_words_view
)

router = APIRouter()


# Route to upload a file
@router.post("/upload-file/")
async def upload_file_path(file: UploadFile = File(...)):
    response = await upload_file_view(file=file)
    return response


@router.get("/files/")
async def list_files_path():
    response = await list_files_view()
    return response


@router.get("/words/most-repeated/")
async def most_repeated_words_path(limit: int = 10, db: Session = Depends(get_db)):
    response = await most_repeated_words_view(limit=limit, db=db)
    return response


@router.get("/words/least-repeated/")
async def least_repeated_words_path(limit: int = 10, db: Session = Depends(get_db)):
    response = await least_repeated_words_view(limit=limit, db=db)
    return response


@router.get("/analyze-files/")
async def analyze_files_path(db: Session = Depends(get_db)):
    response = await analyze_files_view(db=db)
    return response


@router.get("/download/words/")
async def download_words_path(db: Session = Depends(get_db)):
    response = await download_words_view(db=db)
    return response

