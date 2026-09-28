from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoTreino = Literal["corrida", "caminhada", "ciclismo", "funcional"]


class RegraCreate(BaseModel):
    tipo_treino: TipoTreino
    temp_min: float
    temp_max: float
    precipitacao_max_mm: float = Field(ge=0)
    vento_max_kmh: float = Field(ge=0)


class RegraUpdate(BaseModel):
    temp_min: float | None = None
    temp_max: float | None = None
    precipitacao_max_mm: float | None = Field(None, ge=0)
    vento_max_kmh: float | None = Field(None, ge=0)


class RegraOut(RegraCreate):
    id: int

    model_config = {"from_attributes": True}


class AvaliarIn(BaseModel):
    tipo_treino: TipoTreino
    cidade: str
    data_hora: datetime | None = None


class Clima(BaseModel):
    cidade: str
    horario: str
    temperatura_c: float
    precipitacao_mm: float
    vento_kmh: float


class AvaliarOut(BaseModel):
    status: str
    motivos: list[str]
    clima: Clima
