import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

def obtener_df_calendario():
    # Tu código original exacto:
    headers = {'User-Agent': 'Mozilla/5.0'}

    url = "https://www.marca.com/motor/formula1/calendario.html"
    response = requests.get(url, headers=headers)
    response.encoding = 'ISO-8859-1'

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text(separator='\n', strip=True)

    # Dividimos en bloques
    blocks = re.split(r'(GP [^:\n]{2,40}:)', text_content)

    gps = []
    current_gp = None

    for part in blocks:
        part = part.strip()
        if re.match(r'GP [^:\n]{2,40}:', part):
            if current_gp:
                gps.append(current_gp)
            current_gp = {'GP': part.strip(':')}
        elif current_gp is not None:
            current_gp['raw'] = current_gp.get('raw', '') + '\n' + part

    if current_gp:
        gps.append(current_gp)

    data = []
    for gp in gps:
        raw = gp.get('raw', '')
        row = {'GP': gp['GP']}

        fechas_match = re.search(r'(\d{1,2}-\d{1,2}(?: de)? [A-Za-z]+(?: \d{4})?)', raw, re.I)
        row['Fechas'] = fechas_match.group(1).strip() if fechas_match else 'N/A'

        circuito_match = re.search(r'CIRCUITO:?\s*([^\n]+)', raw, re.I) or re.search(r'(Albert Park|Shanghai|Suzuka|Hard Rock|Gilles Villeneuve|Montecarlo)[^\n]*', raw, re.I)
        row['Circuito'] = circuito_match.group(1).strip() if circuito_match else 'N/A'

        long_match = re.search(r'LONGITUD:?\s*(\d+)\s*metros', raw, re.I)
        row['Longitud (m)'] = long_match.group(1) if long_match else 'N/A'

        curvas_match = re.search(r'CURVAS:?\s*(\d+)\s*\((\d+)\s*izda\s*[\|/]\s*(\d+)\s*dcha', raw, re.I)
        row['Curvas'] = f"{curvas_match.group(1)} ({curvas_match.group(2)} izda / {curvas_match.group(3)} dcha)" if curvas_match else 'N/A'

        raw_flat = raw.replace('\n', ' ')
        rec_match = re.search(r'R.?CORD:?\s*(.*?)\s*[-–—]?\s*\b(\d{1,2}:[\d\.]+)', raw_flat, re.I)

        if rec_match:
            piloto = rec_match.group(1).strip().rstrip('-').strip()
            piloto = piloto.replace('\xa0', ' ')
            piloto = piloto.replace('PÃ©rez', 'Pérez').replace('Prez', 'Pérez')
            piloto = re.sub(r'P[^a-zA-Z\s]*rez', 'Pérez', piloto, flags=re.I)
            piloto = re.sub(r'\s+', ' ', piloto).strip()
            tiempo = rec_match.group(2).strip()
            texto_post_tiempo = raw_flat[rec_match.end():rec_match.end()+25]
            anio_match = re.search(r'(\d{4})', texto_post_tiempo)
            if anio_match:
                row['Record vuelta'] = f"{piloto} - {tiempo} ({anio_match.group(1)})"
            else:
                row['Record vuelta'] = f"{piloto} - {tiempo}"
        else:
            row['Record vuelta'] = 'N/A'

        ganador_match = re.search(r'(?:GANADOR|Ganador)\s*(?:2025|anterior)?[:*\s]*([A-Za-záéíóúñ ]{4,})(?=\s*(?:Pole|POLE|Ir arriba|$))', raw, re.I | re.DOTALL)
        row['Ganador anterior'] = ganador_match.group(1).strip() if ganador_match else 'N/A'

        pole_match = re.search(r'(?:POLE|Pole)\s*(?:2025|anterior)?[:*\s]*([A-Za-záéíóúñ ]{4,})(?=\s*(?:Viernes|Horarios|Ir arriba|$))', raw, re.I | re.DOTALL)
        row['Pole anterior'] = pole_match.group(1).strip() if pole_match else 'N/A'

        podios = re.findall(r'(?:PRIMERO|SEGUNDO|TERCERO)\s*([A-Za-záéíóúñ ]+)', raw, re.I)
        if len(podios) >= 3:
            row['Podio reciente'] = f"1º {podios[0].strip()} | 2º {podios[1].strip()} | 3º {podios[2].strip()}"
        else:
            podios2 = re.findall(r'\*(?:PRIMERO|SEGUNDO|TERCERO)([A-Za-záéíóúñ ]+)', raw, re.I)
            if len(podios2) >= 3:
                row['Podio reciente'] = f"1º {podios2[0].strip()} | 2º {podios2[1].strip()} | 3º {podios2[2].strip()}"
            else:
                row['Podio reciente'] = 'N/A'

        raw_horarios = raw.replace('\n', ' ')
        patron_dias = r'(JUEVES|VIERNES|SÁBADO|bado|DOMINGO)\s+(\d{1,2})'
        iter_dias = list(re.finditer(patron_dias, raw_horarios, re.I))
        correcciones_dias = {'bado': 'Sábado', 'jueves': 'Jueves', 'viernes': 'Viernes', 'sábado': 'Sábado', 'domingo': 'Domingo'}
        horarios_completos = []
        dias_procesados = set()

        for i in range(len(iter_dias)):
            match_actual = iter_dias[i]
            dia_raw = match_actual.group(1).lower()
            num_dia = match_actual.group(2)
            nombre_dia = correcciones_dias.get(dia_raw, dia_raw.capitalize())
            if nombre_dia in dias_procesados:
                break
            dias_procesados.add(nombre_dia)
            inicio_texto = match_actual.end()
            fin_texto = iter_dias[i+1].start() if i + 1 < len(iter_dias) else len(raw_horarios)
            texto_dia = raw_horarios[inicio_texto:fin_texto]
            sesiones = re.findall(r'([A-Za-záéíóúñÁÉÍÓÚÑ\s\d]{1,40}):\s*(\d{2}:\d{2})', texto_dia)
            clean_s = []
            for s_nom, s_hora in sesiones:
                nom = s_nom.strip()
                nom = re.sub(r'^[\d:\s]+', '', nom).strip()
                nom_l = nom.lower()
                if len(nom) < 3 or ("carrera" in nom_l and nom_l != "carrera" and "sprint" not in nom_l):
                    if "libres" not in nom_l:
                        nom = "Clasificación"
                nom = nom.capitalize()
                nom = nom.replace("N sprint", "Clasif. Sprint").replace("N al sprint", "Clasif. Sprint").replace("N carrera", "Clasificación").replace("N", "Clasificación")
                if any(p in nom.lower() for p in ['libres', 'clasifica', 'carrera', 'sprint']):
                    clean_s.append(f"{nom}: {s_hora}")
            if clean_s:
                horarios_completos.append(f"- {nombre_dia} {num_dia} = " + " | ".join(clean_s))

        row['Horarios'] = ' \n\n '.join(horarios_completos) if horarios_completos else 'N/A'
        data.append(row)

    df = pd.DataFrame(data)
    df = df[df['GP'].str.contains('GP', na=False)].drop_duplicates(subset=['GP'])
    
    # Retornamos el resultado para el main.py
    return df