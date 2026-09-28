from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.erros import erro_validacao
from app.models import Regra
from app.open_meteo import buscar_clima
from app.schemas import AvaliarIn, AvaliarOut, Clima, RegraCreate, RegraOut, RegraUpdate
from app.service import avaliar_clima, criar_regras_padrao

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    criar_regras_padrao(db)

app = FastAPI(title="Regras climáticas para treinos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(RequestValidationError, erro_validacao)


def buscar_regra(db: Session, regra_id: int) -> Regra:
    regra = db.get(Regra, regra_id)
    if regra is None:
        raise HTTPException(404, "Regra não encontrada")
    return regra


def checar_temperaturas(temp_min, temp_max):
    if temp_min > temp_max:
        raise HTTPException(400, "temp_min não pode ser maior que temp_max")


PAGINA_INICIAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Regras climáticas para treinos</title>
  <style>
    body { font-family: sans-serif; max-width: 640px; margin: 60px auto; padding: 0 20px; color: #222; }
    a { color: #0a66c2; }
    li { margin-bottom: 6px; }
  </style>
</head>
<body>
  <h1>Regras climáticas para treinos</h1>
  <p>
    Consulta o clima no <a href="https://open-meteo.com/">Open-Meteo</a> e, de acordo com a regra
    de cada tipo de treino, diz se o treino está apto, pede atenção ou deve ser cancelado.
  </p>
  <ul>
    <li><a href="/docs">Documentação da API (Swagger)</a></li>
    <li><a href="/regras">Regras cadastradas</a></li>
    <li><a href="/clima?cidade=Recife">Exemplo: clima atual em Recife</a></li>
  </ul>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def pagina_inicial():
    return PAGINA_INICIAL


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/regras", response_model=list[RegraOut])
def listar_regras(db: Session = Depends(get_db)):
    return db.query(Regra).order_by(Regra.id).all()


@app.post("/regras", response_model=RegraOut, status_code=201)
def criar_regra(dados: RegraCreate, db: Session = Depends(get_db)):
    checar_temperaturas(dados.temp_min, dados.temp_max)
    if db.query(Regra).filter_by(tipo_treino=dados.tipo_treino).first():
        raise HTTPException(409, "Já existe uma regra para esse tipo de treino")
    regra = Regra(**dados.model_dump())
    db.add(regra)
    db.commit()
    db.refresh(regra)
    return regra


@app.put("/regras/{regra_id}", response_model=RegraOut)
def atualizar_regra(regra_id: int, dados: RegraUpdate, db: Session = Depends(get_db)):
    regra = buscar_regra(db, regra_id)
    novos = dados.model_dump(exclude_unset=True)
    checar_temperaturas(novos.get("temp_min", regra.temp_min), novos.get("temp_max", regra.temp_max))
    for campo, valor in novos.items():
        setattr(regra, campo, valor)
    db.commit()
    db.refresh(regra)
    return regra


@app.delete("/regras/{regra_id}", status_code=204)
def remover_regra(regra_id: int, db: Session = Depends(get_db)):
    db.delete(buscar_regra(db, regra_id))
    db.commit()


@app.get("/clima", response_model=Clima)
def clima(cidade: str, data_hora: datetime | None = None):
    return buscar_clima(cidade, data_hora)


@app.post("/avaliar", response_model=AvaliarOut)
def avaliar(dados: AvaliarIn, db: Session = Depends(get_db)):
    regra = db.query(Regra).filter_by(tipo_treino=dados.tipo_treino).first()
    if regra is None:
        raise HTTPException(404, "Não há regra cadastrada para esse tipo de treino")

    clima = buscar_clima(dados.cidade, dados.data_hora)
    status, motivos = avaliar_clima(regra, clima)
    return AvaliarOut(status=status, motivos=motivos, clima=clima)
