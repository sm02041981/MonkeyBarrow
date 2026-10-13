"""
SM:18th Sept 2026 Updated: 18th September 2026
Backend for GCS uploader: interacts with Google Cloud Storage,
uploads images, and shares public URLs with Flutter/Dart frontend.
"""

from asyncio import Future
from fastapi import FastAPI, UploadFile, File, Form, APIRouter
from grpc import Future
import datetime
import os
from google.cloud import storage
from dotenv import load_dotenv
import uuid
import time
from datetime import timedelta

# Path to your service account JSON key
#SERVICE_ACCOUNT_PATH: path to your GCP service account JSON key.
#BUCKET_NAME: name of your GCS bucket where files will be stored.


load_dotenv()  # looks for .env in project root

key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
client = storage.Client.from_service_account_json(key_path)

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

bucket = client.bucket(BUCKET_NAME)


def upload_multiple_to_gcs(files: list, mb_isbn13: str, folder: str) -> list:
    
    """
    Upload multiple files to GCS and return public URLs.
    Args:
        files: List of tuples (file_obj, filename).
        folder: Folder prefix in GCS bucket.
    Returns:
        list[str]: Public URLs
    """
    urls = []
    #for file_obj, filename in files:
    for idx, (file_obj, filename) in enumerate(files, start=1):
        # Generate a unique filename to avoid collisions
        # unique_name = f"{uuid.uuid4()}-{filename}"
        unique_name = f"{mb_isbn13}{idx}{os.path.splitext(filename)[1]}"
        blob = bucket.blob(f"{folder}/{unique_name}")

        # Upload file
        # blob.upload_from_file(file_obj)
        blob.upload_from_file(file_obj, content_type="image/png")

        # Make file publicly accessible
        #blob.make_public()
        
        # Wait briefly to ensure object availability
        time.sleep(1)
        
        # Append permanent public URL
        urls.append(blob.public_url)
        print(f"[Google public urls] URLs: {urls}")    
    return urls
    
    
    
    
    """for file_obj, filename in files:
        blob = bucket.blob(f"inventory/{filename}")
        blob.upload_from_file(file_obj)

        # Generate a signed URL valid for 24 hours
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=24),
            method="GET"
        )
        urls.append(signed_url)

    return urls
    """