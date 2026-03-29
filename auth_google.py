import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def conectar_google():
    # Leer la llave secreta desde la variable de entorno de GitHub
    credenciales_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])

    # Definir los permisos (Drive y Sheets)
    scope = [
        "https://spreadsheets.google.com/feeds", 
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
    return gspread.authorize(creds)