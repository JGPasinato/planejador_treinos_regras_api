from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Regra(Base):
    __tablename__ = "regras_clima"

    id = Column(Integer, primary_key=True)
    tipo_treino = Column(String(40), nullable=False, unique=True)
    temp_min = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    precipitacao_max_mm = Column(Float, nullable=False)
    vento_max_kmh = Column(Float, nullable=False)
