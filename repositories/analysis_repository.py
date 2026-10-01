from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, cast, Date
from models.analysis_model import AnalysisModel
from utils.logger import get_logger

logger = get_logger("repository")

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, record: AnalysisModel) -> AnalysisModel:
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            logger.info(f"Análise ID {record.id} gravada com sucesso.")
            return record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao salvar registro de análise: {str(e)}")
            raise e

    def list_all(
        self,
        search_query: Optional[str] = None,
        filter_date: Optional[date] = None
    ) -> List[AnalysisModel]:
        try:
            query = self.db.query(AnalysisModel)

            if filter_date:
                query = query.filter(cast(AnalysisModel.created_at, Date) == filter_date)

            if search_query:
                term = f"%{search_query}%"
                query = query.filter(AnalysisModel.descricao.ilike(term))

            return query.order_by(desc(AnalysisModel.created_at)).all()
        except Exception as e:
            logger.error(f"Erro ao buscar registros de análise: {str(e)}")
            return []

    def get_by_id(self, record_id: int) -> Optional[AnalysisModel]:
        return self.db.query(AnalysisModel).filter(AnalysisModel.id == record_id).first()

    def delete(self, record_id: int) -> bool:
        try:
            record = self.get_by_id(record_id)
            if record:
                self.db.delete(record)
                self.db.commit()
                logger.info(f"Registro ID {record_id} removido com sucesso.")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar registro ID {record_id}: {str(e)}")
            return False