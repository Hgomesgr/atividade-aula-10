import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from services.cv_analysis_service import CVAnalysisService
from repositories.analysis_repository import AnalysisRepository
from models.analysis_model import AnalysisModel
from config.settings import UPLOAD_FOLDER
from utils.logger import get_logger

logger = get_logger("vision_controller")

class VisionController:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.repository = AnalysisRepository(db_session)
        self.cv_service = CVAnalysisService()

    def process_and_save(self, image_bytes: bytes) -> AnalysisModel:
        """
        Recebe os bytes da foto, processa via OpenCV, salva no disco e insere no banco.
        """
        try:
            # 1. Processar com OpenCV
            analysis_data = self.cv_service.analyze_image(image_bytes)

            # 2. Salvar Imagem localmente
            filename = f"cap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            # 3. Mapear Modelo ORM
            model = AnalysisModel(
                image_path=file_path,
                descricao=analysis_data["descricao"],
                objetos=analysis_data["objetos"],
                quantidade_pessoas=analysis_data["quantidade_pessoas"],
                rostos=analysis_data["rostos"],
                idade=analysis_data["idade"],
                emocao=analysis_data["emocao"],
                cores=analysis_data["cores"],
                luminosidade=analysis_data["luminosidade"],
                nitidez=analysis_data["nitidez"],
                json_resultado=analysis_data
            )

            # 4. Salvar via Repositório
            saved_record = self.repository.save(model)
            return saved_record

        except Exception as e:
            logger.error(f"Erro no pipeline do controller: {str(e)}")
            raise e

    def fetch_history(self, search_query: Optional[str] = None, filter_date: Optional[Any] = None) -> List[AnalysisModel]:
        return self.repository.list_all(search_query=search_query, filter_date=filter_date)

    def delete_analysis(self, record_id: int) -> bool:
        record = self.repository.get_by_id(record_id)
        if record and os.path.exists(record.image_path):
            try:
                os.remove(record.image_path)
            except Exception as e:
                logger.warning(f"Incapaz de remover arquivo físico da imagem {record.image_path}: {str(e)}")
        
        return self.repository.delete(record_id)