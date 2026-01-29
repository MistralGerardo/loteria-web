import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import date, timedelta
import re

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
URL = "https://www.jps.go.cr/resultados/nuevos-tiempos-reventados"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

HISTORICO = os.path.join(DATA_DIR, "tiempos_historico.csv")
SALIDA = os.path.join(DATA_DIR, "numeros_probables.csv")
LOG = os.path.join(DATA_DIR, "loteria_log.txt")

# -------------------------------------------------
# UTILIDADES
# -------------------------------------------------
def asegurar_directorio():
    os.makedirs(DATA_DIR, exist_ok=True)


def log(msg):
    asegurar_directorio()
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# -------------------------------------------------
# OBTENER 3 SORTEOS DEL DÍA (HTTP, sin Selenium)
# -------------------------------------------------
def obtener_resultados():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text(separator=" ").lower()

    resultados = {}

    patrones = {
        "mediodía": r"mediodía\s+(\d{1,2})",
        "tarde": r"tarde\s+(\d{1,2})",
        "noche": r"noche\s+(\d{1,2})"
    }

    for sorteo, patron in patrones.items():
        match = re.search(patron, texto)
        if match:
            resultados[sorteo] = int(match.group(1))

    return resultados


# -------------------------------------------------
# ACTUALIZAR HISTÓRICO (VENTANA 60 DÍAS)
# -------------------------------------------------
def actualizar_historico(resultados):
    asegurar_directorio()
    hoy = date.today()

    filas = []
    for sorteo, numero in resultados.items():
        filas.append({
            "fecha": hoy.isoformat(),
            "sorteo": sorteo,
            "numero": numero
        })

    nuevos = pd.DataFrame(filas)

    if os.path.exists(HISTORICO):
        df = pd.read_csv(HISTORICO)

        df["fecha"] = pd.to_datetime(df["fecha"])
        limite = pd.Timestamp(hoy - timedelta(days=60))
        df = df[df["fecha"] >= limite]

        claves = set(zip(df["fecha"].astype(str), df["sorteo"]))

        for _, fila in nuevos.iterrows():
            clave = (fila["fecha"], fila["sorteo"])
            if clave not in claves:
                df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
                log(f"Agregado: {fila['sorteo']} {fila['numero']}")
            else:
                log(f"Duplicado ignorado: {fila['sorteo']}")

    else:
        df = nuevos
        log("Histórico creado por primera vez")

    df.to_csv(HISTORICO, index=False)
    return df


# -------------------------------------------------
# GENERAR 15 NÚMEROS MÁS PROBABLES
# -------------------------------------------------
def generar_numeros(df):
    frec = df["numero"].value_counts().head(15)

    resultado = sorted(frec.index.tolist())

    pd.DataFrame({
        "numero": resultado,
        "frecuencia": [frec[n] for n in resultado]
    }).to_csv(SALIDA, index=False)

    log("15 números más probables:")
    log(" ".join(f"{n:02d}" for n in resultado))

    return resultado


# -------------------------------------------------
# FUNCIÓN PRINCIPAL (para Flask o ejecución manual)
# -------------------------------------------------
def ejecutar_loteria():
    log("===== EJECUCIÓN AUTOMATIZADA =====")

    resultados = obtener_resultados()
    if len(resultados) < 3:
        log("No se detectaron los 3 sorteos")
        return None

    log(f"Resultados del día: {resultados}")

    df = actualizar_historico(resultados)
    numeros = generar_numeros(df)

    return numeros
def obtener_sugerencias():
    return ejecutar_loteria()

