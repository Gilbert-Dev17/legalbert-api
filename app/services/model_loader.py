import os
import zipfile
import requests

# Use the File ID from your GDrive link
GDRIVE_FILE_ID = os.getenv("GDRIVE_FILE_ID")
BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/models")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")
MODEL_ZIP = os.path.join(BASE_DIR, "model.zip")

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def ensure_model_present():
    if os.path.exists(os.path.join(MODEL_DIR, "config.json")):
        print("Meow! ✅ LegalBERT is already loaded.")
        return MODEL_DIR

    print("Meow! ⬇️ Downloading LegalBERT from Google Drive...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Note: Use the /uc endpoint for direct download
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    # Step 1: Initial request to get the 'confirm' token
    response = session.get(URL, params={'id': GDRIVE_FILE_ID}, stream=True)

    # Step 2: Try to find the token in cookies OR in the response text itself
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break

    # Sometimes Google puts the token in the URL of the "Download Anyway" button
    if not token:
        # Check if we got the warning page and try to parse the token out
        content = response.text
        if "confirm=" in content:
            token = content.split("confirm=")[1].split("&")[0].split('"')[0]

    # Step 3: If we have a token, make the final request
    if token:
        print(f"Meow! Confirmation token found: {token[:5]}...")
        response = session.get(URL, params={'id': GDRIVE_FILE_ID, 'confirm': token}, stream=True)
    else:
        print("Meow! No token required or found. Proceeding with initial response.")

    # Step 4: Write the file
    with open(MODEL_ZIP, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

    # Step 5: Unzip with error handling
    try:
        with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        os.remove(MODEL_ZIP)
    except zipfile.BadZipFile:
        with open(MODEL_ZIP, "r", errors='ignore') as f:
            start_content = f.read(150)
        print(f"Error: Not a zip file. Content: {start_content}")
        raise Exception("Google Drive blocked the download. Is the file shared with 'Anyone with the link'?")

    print(f"Meow! ✅ Model ready at {MODEL_DIR}")
    return MODEL_DIR