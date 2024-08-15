import concurrent.futures
import re
import os
import pymupdf
from spellchecker import SpellChecker
from nltk.corpus import stopwords
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from src.database.models import WordMetadata
from fastapi import HTTPException
from typing import List, Set, Tuple

# Define global stop words list
STOPWORDS = set(stopwords.words('english')).union({'yes', 'no', 'a', 'b', 'c', 'd'})


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    doc = pymupdf.open(pdf_file)
    text = ""
    for page in doc[4:-4]:  # iterate the document pages
        text += " \n " + page.get_text()
    return text


# Function to clean and tokenize text, ignoring Chinese characters
def clean_and_tokenize(text):
    # Remove punctuation, special characters, and Chinese characters
    text = re.sub(r'[\u4e00-\u9fff]', '', text)  # Remove Chinese characters
    text = text.replace("\n", " ")
    text = re.sub(r'[^\w\s]', '', text)  # Removing Non-Alphanumeric Characters

    # Convert text to lowercase and split into words
    words = text.lower().split(" ")
    words = check_dictation(words)
    # Filter out stopwords and non-alphabetic words
    words = [word for word in words if word.isalpha() and word not in STOPWORDS]
    return words


# Function to find the sentences where a word occurs
def find_sentences_with_word(text, word):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [sentence for sentence in sentences if word in sentence.lower()]


def extract_text_from_file_of_images(file_path) -> str:

    _, ext = os.path.splitext(file_path)
    if ext == ".pdf":
        images_dir = pdf_to_image(file_path)
        text = image_extractor(images_dir)
        write_text_in_file(text=text, dir=images_dir)
        return text
    else:
        print("can not process yet")
        return ""


def pdf_to_image(file_path):
    IMAGEDIR = os.path.join(os.getcwd(), f"src/{file_path.split('/')[-1]}")

    if os.path.exists(IMAGEDIR):
        files = os.listdir(IMAGEDIR)
        for file in files:
            if ".txt" in str(file).lower():
                return IMAGEDIR
        os.remove(IMAGEDIR)

    os.makedirs(IMAGEDIR, exist_ok=True)
    # ----------------------------------
    doc = pymupdf.open(file_path)
    for page in doc[4:-4]:  # iterate the document pages
        # change page to an image
        pix = page.get_pixmap()
        pix.save(f"{IMAGEDIR}/image-{page.number}.png")

    return IMAGEDIR


def image_extractor(images_dir):
    import pytesseract
    from PIL import Image

    if if_already_extracted(images_dir):
        files = os.listdir(images_dir)

        # Search for a .txt file
        txt_file = [file for file in files if file.lower().endswith('.txt')]
        txt_file_path = os.path.join(images_dir, txt_file[0])

        # Read the content of the text file
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            return file.read()

    fullText = []

    images = os.listdir(images_dir)
    for image_name in images:
        image_path = os.path.join(images_dir, image_name)

        image = Image.open(image_path)

        # Perform OCR using PyTesseract
        text = pytesseract.image_to_string(image)
        fullText.append(text)
    return ' * '.join(fullText)


def write_text_in_file(text, dir):
    file_name = os.path.join(dir, "text.txt")
    with open(file_name, 'w') as f:
        f.write(text)


def if_already_extracted(images_dir):
    images = os.listdir(images_dir)
    for image_name in images:
        if image_name.lower().endswith('.txt'):
            return True
    return False

# ---------------------------------------------------------


def check_dictation(word_list: List[str]) -> List[str]:
    """
    Divide the word_list into chunks, process them in parallel, and combine the results.
    """
    num_processes = 20
    chunk_size = len(word_list) // num_processes
    chunks = [word_list[i:i + chunk_size] for i in range(0, len(word_list), chunk_size)]

    new_word_list = []
    garbage = set()  # Using a set to collect invalid words (to avoid duplicates)

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Submit each chunk to be processed in parallel
        futures = [executor.submit(process_words, chunk) for chunk in chunks]

        for future in concurrent.futures.as_completed(futures):
            result, invalid_words = future.result()
            new_word_list.extend(result)  # Add valid words to the list
            garbage.update(invalid_words)  # Merge invalid words sets

    print(garbage, "\ngarbage")

    return new_word_list


def process_words(word_list: List[str]) -> Tuple[List[str], Set[str]]:
    """
    Process a sublist of words, correct misspelled words, and return the corrected words.
    """
    word_repetition_checker = set()
    new_word_list = []
    garbage = set()
    spell = SpellChecker()

    for word in word_list:
        if word not in word_repetition_checker:
            corrected_word = spell.correction(word)
            if corrected_word:  # `corrected_word` being None or an empty string is handled here
                new_word_list.append(corrected_word)
                word_repetition_checker.add(corrected_word)
            else:
                garbage.add(word)

    return new_word_list, garbage


def clear_database(db: Session):
    try:
        db.query(WordMetadata).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")
