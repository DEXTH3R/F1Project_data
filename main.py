import pandas as pd
import datetime
from auth_google import conectar_google
import extraer_calendario
import extraer_pilotos
import extraer_constructores
from gspread_dataframe import set_with_dataframe
from gspread.exceptions import WorksheetNotFound

def registrar_log_en_excel(libro, modulo, mensaje):
    """Escribe el estado del bot en una pestaña llamada 'LOGS'"""
    try:
        try:
            hoja_log = libro.worksheet("LOGS")
        except WorksheetNotFound:
            hoja_log = libro.add_worksheet(title="LOGS", rows="100", cols="5")
        
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hoja_log.append_row([ahora, modulo, str(mensaje)])
    except Exception as e:
        print(f"No se pudo escribir en la hoja de LOGS: {e}")

def guardar_en_hoja(libro, nombre_pestaña, dataframe):
    if dataframe is None or dataframe.empty:
        msg = f"⚠️ La tabla '{nombre_pestaña}' está VACÍA."
        print(msg)
        registrar_log_en_excel(libro, nombre_pestaña, msg)
        return
    
    try:
        try:
            hoja = libro.worksheet(nombre_pestaña)
            hoja.clear()
        except WorksheetNotFound:
            hoja = libro.add_worksheet(title=nombre_pestaña, rows="100", cols="30")
        
        set_with_dataframe(hoja, dataframe, index=False)
        print(f"✅ Guardado con éxito en: '{nombre_pestaña}'")
        registrar_log_en_excel(libro, nombre_pestaña, "OK - Datos actualizados")
    except Exception as e:
        print(f"❌ Error al guardar {nombre_pestaña}: {e}")
        registrar_log_en_excel(libro, nombre_pestaña, f"ERROR: {e}")

def ejecutar_bot():
    print("🏎️ Iniciando F1 Data Bot Modular...")
    
    try:
        # 1. Conexión única
        gc = conectar_google()
        sh = gc.open("F1_Base_De_Datos_2026")
        
        # 2. Ejecutar extracciones (He quitado los comentarios para probar todo)
        print("--- Ejecutando Calendario ---")
        try:
            df_cal = extraer_calendario.obtener_df_calendario()
            guardar_en_hoja(sh, "Calendario_MARCA", df_cal)
        except Exception as e:
            registrar_log_en_excel(sh, "Módulo Calendario", e)

        print("--- Ejecutando Pilotos ---")
        try:
            df_pil = extraer_pilotos.run()
            guardar_en_hoja(sh, "Pilotos_ESPN", df_pil)
        except Exception as e:
            registrar_log_en_excel(sh, "Módulo Pilotos", e)

        print("--- Ejecutando Constructores ---")
        try:
            df_con = extraer_constructores.run()
            guardar_en_hoja(sh, "Constructores_ESPN", df_con)
        except Exception as e:
            registrar_log_en_excel(sh, "Módulo Constructores", e)

        print(f"\n🏁 Proceso completado. Revisa la pestaña 'LOGS' en tu Excel.")

    except Exception as e:
        print(f"💥 ERROR CRÍTICO EN EL MAIN: {e}")

if __name__ == "__main__":
    ejecutar_bot()