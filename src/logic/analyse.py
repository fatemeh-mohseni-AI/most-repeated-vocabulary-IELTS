from fastapi import UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.utils import (
    extract_text_from_pdf, clean_and_tokenize,
    extract_text_from_file_of_images, clear_database
)
from src.database.models import WordMetadata
from collections import Counter

import os


UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "src/books")
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# Step 1: Clear the database
async def analyze_files(db: Session = Depends(get_db)):
    clear_database(db)

    # Step 2: Process all PDF files
    files = os.listdir(UPLOAD_DIRECTORY)
    if not files:
        raise HTTPException(status_code=404, detail="No files found to analyze.")

    total_files_processed = 0

    for file_name in files:
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

        # Ensure the file is a PDF
        _, ext = os.path.splitext(file_path)
        if ext.lower() == ".pdf":
            process_file(file_path=file_path, db=db, file_name=file_name)
            total_files_processed += 1
            print(file_name)
        else:
            continue

    return {"status": "Analysis complete", "files_analyzed": total_files_processed}


# 1ST STEP -------------------------
def process_file(file_path: str, db: Session, file_name: str) -> Counter:
    try:
        text = extract_text_from_pdf(file_path)
        if len(text.strip()) == 0:
            print(f"file {file_path} is just images")
            text = extract_text_from_file_of_images(file_path)
        words = clean_and_tokenize(text)
        word_counter = Counter(words)
        save_word_data(db, word_counter, file_name)
        return word_counter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file {file_path}: {str(e)}")


def save_word_data(db: Session, word_counter: Counter, file_name: str, text: str = None):
    try:
        for word, count in word_counter.items():
            # sentences = find_sentences_with_word(text, word)
            word_data = WordMetadata(
                word=word,
                count=count,
                book=file_name,
                # sentences=" | ".join(sentences)  # Join sentences into a single string
            )
            db.add(word_data)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save data to database: {str(e)}")
