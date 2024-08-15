from fastapi import FastAPI
from src.routes import urls
from .database.database import initialize_database

app = FastAPI()

# Initialize the database
initialize_database()

# Include routers
app.include_router(urls.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Word Analysis API"}
