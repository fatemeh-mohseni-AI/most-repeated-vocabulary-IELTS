from fastapi import UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.models import WordMetadata
from fastapi.responses import StreamingResponse
from src.logic.analyse import analyze_files
from collections import Counter
from src.static.generate import generate_html_table
import pandas as pd
import aiofiles
import os
import io


UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "src/books")
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


async def upload_file_view(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

        # Asynchronously write the file to the upload directory
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        return {"filename": file.filename, "status": "Uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


async def list_files_view():
    try:
        files = os.listdir(UPLOAD_DIRECTORY)
        if not files:
            raise HTTPException(status_code=404, detail="No files found.")

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


async def most_repeated_words_view(limit: int = 10, db: Session = Depends(get_db)):
    try:
        words = db.query(WordMetadata).order_by(WordMetadata.count.desc()).limit(limit).all()

        if not words:
            raise HTTPException(status_code=404, detail="No words found.")

        html_content = generate_html_table(words)
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching most repeated words: {str(e)}")


async def least_repeated_words_view(limit: int = 10, db: Session = Depends(get_db)):
    try:
        words = db.query(WordMetadata).order_by(WordMetadata.count.asc()).limit(limit).all()

        if not words:
            raise HTTPException(status_code=404, detail="No words found.")

        html_content = generate_html_table(words)
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching least repeated words: {str(e)}")


async def analyze_files_view(db: Session = Depends(get_db)):
    response = await analyze_files(db=db)
    return response


async def download_words_view(db: Session = Depends(get_db)):
    try:
        # Query all records from the database
        words = db.query(WordMetadata).all()

        if not words:
            raise HTTPException(status_code=404, detail="No records found.")

        # Convert the result to a list of dictionaries (or whatever is appropriate for your data)
        words_dict = [word.to_dict() for word in words]

        # Convert to pandas DataFrame
        df = pd.DataFrame(words_dict)

        # Write DataFrame to an Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        output.seek(0)  # Go back to the beginning of the BytesIO object

        # Serve the Excel file as a downloadable response
        headers = {
            'Content-Disposition': 'attachment; filename="words.xlsx"'
        }
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                 headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting records: {str(e)}")


