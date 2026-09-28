import httpx
from fastapi import HTTPException

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
VARIAVEIS = "temperature_2m,precipitation,wind_speed_10m"


def buscar_clima(cidade, data_hora=None):
    resp = httpx.get(GEOCODING_URL, params={"name": cidade, "count": 1, "language": "pt"}, timeout=15)
    resultados = resp.json().get("results")
    if not resultados:
        raise HTTPException(404, f"Cidade não encontrada: {cidade}")
    local = resultados[0]

    params = {"latitude": local["latitude"], "longitude": local["longitude"], "timezone": "auto"}
    if data_hora:
        hora = data_hora.strftime("%Y-%m-%dT%H:00")
        params.update(hourly=VARIAVEIS, start_hour=hora, end_hour=hora)
    else:
        params["current"] = VARIAVEIS

    resp = httpx.get(FORECAST_URL, params=params, timeout=15)
    if resp.status_code == 400:
        raise HTTPException(400, "Sem previsão para essa data (o Open-Meteo cobre só os próximos 16 dias)")
    if resp.status_code != 200:
        raise HTTPException(502, "Erro ao consultar o Open-Meteo")

    if data_hora:
        dados = {chave: valores[0] for chave, valores in resp.json()["hourly"].items()}
    else:
        dados = resp.json()["current"]

    return {
        "cidade": f"{local['name']}, {local.get('country', '')}",
        "horario": dados["time"],
        "temperatura_c": dados["temperature_2m"],
        "precipitacao_mm": dados["precipitation"] or 0,
        "vento_kmh": dados["wind_speed_10m"],
    }
