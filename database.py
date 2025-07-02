from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    google_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{config.DB_PATH}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, user_id: int, username: str):
        """Добавление или обновление пользователя."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if not user:
                    user = User(user_id=user_id, username=username)
                    session.add(user)
                else:
                    user.username = username
                session.commit()
                logger.info(f"Пользователь {username} (ID: {user_id}) добавлен/обновлен")
            except Exception as e:
                logger.error(f"Ошибка добавления пользователя {user_id}: {str(e)}")
                session.rollback()

    def save_google_token(self, user_id: int, token: str):
        """Сохранение токена Google."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if user:
                    user.google_token = token
                    session.commit()
                    logger.info(f"Токен Google сохранен для user_id: {user_id}")
            except Exception as e:
                logger.error(f"Ошибка сохранения токена для user_id {user_id}: {str(e)}")
                session.rollback()

    def get_google_token(self, user_id: int) -> dict | None:
        """Получение токена Google."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if user and user.google_token:
                    return json.loads(user.google_token)
                return None
            except Exception as e:
                logger.error(f"Ошибка получения токена для user_id {user_id}: {str(e)}")
                return None

    def save_document(self, user_id: int, file_name: str, content: str):
        """Сохранение документа в базе данных."""
        with self.Session() as session:
            try:
                document = Document(user_id=user_id, file_name=file_name, content=content)
                session.add(document)
                session.commit()
                logger.info(f"Документ {file_name} сохранен для user_id: {user_id}")
            except Exception as e:
                logger.error(f"Ошибка сохранения документа {file_name}: {str(e)}")
                session.rollback()

    def get_documents(self, user_id: int) -> list:
        """Получение всех документов пользователя."""
        with self.Session() as session:
            try:
                documents = session.query(Document).filter_by(user_id=user_id).all()
                logger.info(f"Получено {len(documents)} документов для user_id: {user_id}")
                return documents
            except Exception as e:
                logger.error(f"Ошибка получения документов для user_id {user_id}: {str(e)}")
                return []

    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Удаление документа по ID."""
        with self.Session() as session:
            try:
                document = session.query(Document).filter_by(id=document_id, user_id=user_id).first()
                if document:
                    session.delete(document)
                    session.commit()
                    logger.info(f"Документ ID {document_id} удален для user_id: {user_id}")
                    return True
                logger.warning(f"Документ ID {document_id} не найден для user_id: {user_id}")
                return False
            except Exception as e:
                logger.error(f"Ошибка удаления документа ID {document_id}: {str(e)}")
                session.rollback()
                return False