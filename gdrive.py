# * import libraries
import io, os.path, PyPDF2
from pathlib import Path
from decouple import config

# * Google
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials


class Gdrive:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        creds = os.path.join(BASE_DIR, 'credentials.json')

        credentials = Credentials.from_service_account_file(creds, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(config("GOOGLE_ACCOUNT"))
        self.drive = build('drive', 'v3', credentials=delegated_credentials)
        self.pdf_files = []

    def getFiles(self, folder_path='/')->list:
        """
        List all files in the folder

        Args:
            folder_path (str): Folder path in Google Drive

        Returns:
            list: List of files with details
        """

        # Retrieves the folder ID from the path
        folder_id = None
        if folder_path == '/':
            folder_id = 'root'
        else:
            query = f"name = '{folder_path.split('/')[-1]}'"
            results = self.drive.files().list(q=query, spaces='drive').execute()
            items = results.get('files', [])
            if items:
                folder_id = items[0]['id']

        if not folder_id:
            raise Exception(f"Dossier non trouvé: {folder_path}")

        # Lists the files in the folder
        query = f"'{folder_id}' in parents"
        results = self.drive.files().list(
            q=query,
            fields="files(id, name, mimeType, size, modifiedTime)"
        ).execute()

        return results.get('files', [])


    def getContentFileById(self, file_id: str) -> str:
        """
        Retrieves the contents and details of a PDF file from Google Drive using its ID.

        Args:
            file_id (str): PDF file ID in Google Drive

        Returns:
            str: Contents of the PDF file
        """

        try:
            # Download the contents of the PDF file
            request = self.drive.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            # Convert content bytes to str
            text = self.convertByteToStr(fh.getvalue())

            return text.replace('\n', ' ')

        except Exception as e:
            raise Exception(f"Erreur lors de la récupération du fichier PDF avec l'ID {file_id}: {e}")


    def convertByteToStr(self, pdf_content:bytes)->str:
        """
        Converts text from byte to text

        Args:
            pdf_content (str): Content of the PDF file in bytes

        Returns:
            str: Content of the PDF file in str
        """

        pdf_file = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + " "

        return text


    def getPDFFiles(self, path: str) -> list:
        '''
        Recursively retrieve all PDF files from a parent folder

        :param path: parent path
        :return: list of dict (PDF file info)
        '''
        files = self.getFiles(path)

        for file in files:
            if file['mimeType'] == 'application/pdf':
                self.pdf_files.append({
                    'page_content': self.getContentFileById(file['id']),
                    'metadata': {
                        'id': file['id'],
                        'name': file['name'],
                        'modifiedTime': file['modifiedTime'],
                    }
                })
            elif file['mimeType'] == 'application/vnd.google-apps.folder':
                new_path = f'{path}/{file["name"]}'
                self.getPDFFiles(new_path)

        return self.pdf_files