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

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    # 1. First request to trigger the warning
    response = session.get(URL, params={'id': GDRIVE_FILE_ID}, stream=True)

    # 2. Extract the token from cookies
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break

    # 3. If token exists, request again with it; otherwise use the first response
    if token:
        params = {'id': GDRIVE_FILE_ID, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    # 4. Save the actual content
    with open(MODEL_ZIP, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk: f.write(chunk)

    # 5. Unzip
    try:
        with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        os.remove(MODEL_ZIP)
    except zipfile.BadZipFile:
        # If it fails, print the content to see what Google sent us
        with open(MODEL_ZIP, "r") as f:
            print(f"Error: Downloaded file is not a zip. Content starts with: {f.read(100)}")
        raise Exception("Failed to download a valid zip from Google Drive. Check file permissions!")

    print(f"Meow! ✅ Model ready at {MODEL_DIR}")
    return MODEL_DIR