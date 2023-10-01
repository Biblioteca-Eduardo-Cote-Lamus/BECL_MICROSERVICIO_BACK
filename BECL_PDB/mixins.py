import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleAPIMixin:
    __SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self) -> None:
        self.service = None

    def init_service(self, service: str):
        self.service = build(service, "v3", credentials=self.__getCredentials())

    def __getCredentials(self):
        # Si modifica este scopes, borra el archivo token.json
        creds = None
        # El archivo token.json almacena los tokens de acceso y actualización del usuario, y es
        # creado automáticamente cuando el flujo de autorización se completa por primera vez
        # tiempo.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.__SCOPES)
        # Si no hay credenciales (válidas) disponibles, permita que el usuario inicie sesión.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.__SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def upload_doc(self):
        pass

    def get_list_events(self, start, end):
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def insert_event(self, calendar_body):
        try:
            # self.init_service('calendar')
            self.service.events().insert(calendarId="primary", body=calendar_body).execute()
            return True
        except Exception as e:
            raise e
        

    def update_event(self):
        pass


"""

try:
    hour = datetime.utcnow().strftime("%H-%M-%S")
    file_metadata = {
        "name": f"{hour}-{name_docx}",
        "parents": [
            os.getenv("FOLDER_ID_A") if option == "A" else os.getenv("FOLDER_ID_S")
        ],
    }
    path = (
        f"BECL_PDB/doc/doc_auditorio/{name_docx}.docx"
        if option == "A"
        else f"BECL_PDB/doc/doc_semillero/{name_docx}.docx"
    )
    media = MediaFileUpload(
        path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    self.__service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    self.__service.close()
    return "Se subio el archivo de manera correcta."
except Exception as err:
            raise err
"""
