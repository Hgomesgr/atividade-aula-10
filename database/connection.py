from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL
from utils.logger import get_logger

logger = get_logger("database")

Base = declarative_base()

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.critical(f"Falha ao configurar engine de banco de dados: {str(e)}")
    raise e

def init_db():
    """Cria as tabelas no banco caso ainda não existam."""
    try:
        import models.analysis_model  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados validadas/criadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar tabelas no banco: {str(e)}")
        raise e

def get_db():
    """Gerenciador de Contexto para sessões SQLAlchemy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()