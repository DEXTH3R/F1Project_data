from auth_google import conectar_google
import extraer_calendario
import extraer_pilotos
import extraer_constructores
from gspread_dataframe import set_with_dataframe
from gspread.exceptions import WorksheetNotFound

def guardar_en_hoja(libro, nombre_pestaña, dataframe):
    if dataframe is None or dataframe.empty:
        print(f"⚠️ La tabla '{nombre_pestaña}' está vacía. Saltando...")
        return
    try:
        hoja = libro.worksheet(nombre_pestaña)
        hoja.clear()
    except WorksheetNotFound:
        hoja = libro.add_worksheet(title=nombre_pestaña, rows="100", cols="30")
    set_with_dataframe(hoja, dataframe, index=False)
    print(f"✅ Guardado en: '{nombre_pestaña}'")

def ejecutar_bot():
    print("🏎️ Iniciando F1 Data Bot Modular...")
    
    # 1. Conexión única
    gc = conectar_google()
    sh = gc.open("F1_Base_De_Datos_2026")

    # 2. Ejecutar extracciones de forma independiente
    #df_cal = extraer_calendario.obtener_df_calendario()
    #df_pil = extraer_pilotos.run()
    df_con = extraer_constructores.run()

    # 3. Guardar resultados
    #guardar_en_hoja(sh, "Calendario_MARCA", df_cal)
    #guardar_en_hoja(sh, "Pilotos_ESPN", df_pil)
    guardar_en_hoja(sh, "Constructores_ESPN", df_con)

    print(f"\nProceso completado. URL: {sh.url}")

if __name__ == "__main__":
    ejecutar_bot()