import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONKEYBARROW_BOOKAPI = os.getenv("MBT_BOOKAPI_1")

def isbn13_to_isbn10(isbn13: str) -> str | None:
    """Convert ISBN-13 to ISBN-10 if possible."""
    if not isbn13.startswith("978"):
        return None
    digits = isbn13[3:-1]
    total = sum((10 - i) * int(x) for i, x in enumerate(digits, start=1))
    check = 11 - (total % 11)
    check_digit = "X" if check == 10 else "0" if check == 11 else str(check)
    return digits + check_digit

def fetch_google_books(isbn: str) -> dict | None:
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={MONKEYBARROW_BOOKAPI}"
    print(f"[Google Books] URL: {url}")
    try:
        resp = requests.get(url, timeout=5)
        print(f"[Google Books] resp: {resp}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("totalItems", 0) > 0:
                item = data["items"][0].get("volumeInfo", {})
                image_links = item.get("imageLinks", {})
                return {
                    "isbn": isbn,
                    "title": item.get("title", ""),
                    "author": ", ".join(item.get("authors", [])),
                    "categories": item.get("categories", []),
                    "description": item.get("description", ""),
                    "publisher": item.get("publisher", ""),
                    "publishedDate": item.get("publishedDate", ""),
                    "thumbnail": image_links.get("thumbnail", ""),
                }
    except requests.RequestException as e:
        print(f"[Google Books] Error: {e}")
    return None

def fetch_open_library(isbn: str) -> dict | None:
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    print(f"[Open Library] URL: {url}")
    try:
        resp = requests.get(url, timeout=5)
        print(f"[Google Books] resp: {resp}")
        if resp.status_code == 200:
            book_data = resp.json().get(f"ISBN:{isbn}")
            if book_data:
                return {
                    "isbn": isbn,
                    "title": book_data.get("title", ""),
                    "author": ", ".join([a.get("name", "") for a in book_data.get("authors", [])]),
                    "description": book_data.get("notes", ""),
                    "publisher": ", ".join([p.get("name", "") for p in book_data.get("publishers", [])]),
                    "publishedDate": book_data.get("publish_date", ""),
                }
    except requests.RequestException as e:
        print(f"[Open Library] Error: {e}")
    return None

def get_book_details(isbn: str) -> dict:
    # Try Google Books (ISBN-13)
    book = fetch_google_books(isbn)
    if book:
        return book

    # Try Open Library (ISBN-13)
    book = fetch_open_library(isbn)
    if book:
        return book

    # Retry with