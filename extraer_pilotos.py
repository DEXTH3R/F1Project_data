import pandas as pd
import requests
import re
from io import StringIO

def limpiar_nombre(texto):
    texto = str(texto)
    texto = re.sub(r'^\d+', '', texto).strip()
    mitad = len(texto) // 2
    if texto[:mitad] == texto[mitad:]:
        return texto[:mitad]
    return texto

def run():
    url = "https://espndeportes.espn.com/deporte-motor/f1/posiciones"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        respuesta = requests.get(url, headers=headers, timeout=15)
        dfs = pd.read_html(StringIO(respuesta.text))
        df_nombres = dfs[0].dropna(how='all').reset_index(drop=True)
        df_puntos = dfs[1].dropna(how='all').reset_index(drop=True)
        
        df_final = pd.concat([df_nombres, df_puntos], axis=1)
        col_nombre = df_final.columns[0]
        df_final[col_nombre] = df_final[col_nombre].apply(limpiar_nombre)
        df_final.rename(columns={col_nombre: 'Piloto'}, inplace=True)
        
        return df_final
    except Exception as e:
        print(f"❌ Error en Módulo Pilotos: {e}")
        return pd.DataFrame()