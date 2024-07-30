import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError, UnknownApiNameOrVersion
import requests
from urllib.parse import quote

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']

def get_credentials():
    logger.debug("Entering get_credentials function")
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            logger.info("Starting new authentication flow")
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"Please visit this URL to authorize the application: {auth_url}")
            code = input("Enter the authorization code: ")
            
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            logger.debug("Credentials saved to token.json")
    
    return creds

def upload_to_google_photos(file_path):
    logger.debug(f"Attempting to upload file: {file_path}")
    creds = get_credentials()
    try:
        service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    except UnknownApiNameOrVersion:
        logger.warning("Failed to build service with default settings, trying alternative method")
        service = build('photoslibrary', 'v1', credentials=creds,
                        discoveryServiceUrl='https://photoslibrary.googleapis.com/$discovery/rest?version=v1')

    try:
        file_name = os.path.basename(file_path)
        
        # URLエンコードされたファイル名を作成
        encoded_file_name = quote(file_name)
        
        # Step 1: アップロードトークンの取得
        upload_endpoint = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-type': 'application/octet-stream',
            'X-Goog-Upload-Protocol': 'raw',
            'X-Goog-Upload-File-Name': encoded_file_name
        }

        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        response = requests.post(upload_endpoint, headers=headers, data=file_data)
        response.raise_for_status()  # エラーがあれば例外を発生させる
        upload_token = response.content.decode('utf-8')

        # Step 2: メディアアイテムの作成
        request_body = {
            'newMediaItems': [{
                'description': f'Uploaded by Digital Imaging Cloud: {file_name}',
                'simpleMediaItem': {
                    'uploadToken': upload_token
                }
            }]
        }

        response = service.mediaItems().batchCreate(body=request_body).execute()
        logger.info(f"Uploaded {file_name} to Google Photos")
        return response
    except HttpError as error:
        logger.error(f"An HTTP error occurred: {error}")
    except requests.exceptions.RequestException as error:
        logger.error(f"A request error occurred: {error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    
    return None

if __name__ == "__main__":
    # テスト用のコード
    test_file_path = "path/to/your/test/image.jpg"
    result = upload_to_google_photos(test_file_path)
    if result:
        print("Upload successful")
    else:
        print("Upload failed")
