from app.models import Regra

REGRAS_PADRAO = [
    Regra(tipo_treino="corrida", temp_min=8, temp_max=32, precipitacao_max_mm=0.6, vento_max_kmh=35),
    Regra(tipo_treino="caminhada", temp_min=5, temp_max=36, precipitacao_max_mm=1.5, vento_max_kmh=45),
    Regra(tipo_treino="ciclismo", temp_min=8, temp_max=34, precipitacao_max_mm=0.4, vento_max_kmh=40),
    Regra(tipo_treino="funcional", temp_min=10, temp_max=33, precipitacao_max_mm=0.8, vento_max_kmh=30),
]


def criar_regras_padrao(db):
    if db.query(Regra).count() == 0:
        db.add_all(REGRAS_PADRAO)
        db.commit()


def avaliar_clima(regra, clima):
    temp = clima["temperatura_c"]
    chuva = clima["precipitacao_mm"]
    vento = clima["vento_kmh"]

    status = "apto"
    motivos = []

    if temp < regra.temp_min or temp > regra.temp_max:
        status = "cancelar"
        motivos.append(f"Temperatura de {temp}°C fora da faixa ({regra.temp_min} a {regra.temp_max}°C)")

    if chuva > regra.precipitacao_max_mm:
        status = "cancelar"
        motivos.append(f"Chuva de {chuva} mm (limite de {regra.precipitacao_max_mm} mm)")

    if vento > regra.vento_max_kmh:
        if status == "apto":
            status = "atencao"
        motivos.append(f"Vento de {vento} km/h (limite de {regra.vento_max_kmh} km/h)")

    if not motivos:
        motivos.append("Clima bom para treinar")

    return status, motivos
