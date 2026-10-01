from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from database.connection import Base

class AnalysisModel(Base):
    __tablename__ = "analises"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    descricao = Column(Text, nullable=False)
    objetos = Column(JSON, nullable=False)
    quantidade_pessoas = Column(Integer, default=0, nullable=False)
    rostos = Column(Integer, default=0, nullable=False)
    idade = Column(String(50), nullable=True, default="N/A")
    emocao = Column(String(50), nullable=True, default="N/A")
    cores = Column(JSON, nullable=False)
    luminosidade = Column(String(50), nullable=False)
    nitidez = Column(String(50), nullable=False)
    json_resultado = Column(JSON, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "image_path": self.image_path,
            "descricao": self.descricao,
            "objetos": self.objetos,
            "quantidade_pessoas": self.quantidade_pessoas,
            "rostos": self.rostos,
            "idade": self.idade,
            "emocao": self.emocao,
            "cores": self.cores,
            "luminosidade": self.luminosidade,
            "nitidez": self.nitidez,
            "json_resultado": self.json_resultado
        }