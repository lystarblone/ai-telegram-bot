from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
import os
from datetime import datetime
import json

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
        with self.Session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, username=username)
                session.add(user)
            else:
                user.username = username
            session.commit()

    def save_google_token(self, user_id: int, token: dict):
        with self.Session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.google_token = json.dumps(token)
                session.commit()

    def get_google_token(self, user_id: int):
        with self.Session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user and user.google_token:
                return json.loads(user.google_token)
            return None

    def save_document(self, user_id: int, file_name: str, content: str):
        with self.Session() as session:
            document = Document(user_id=user_id, file_name=file_name, content=content)
            session.add(document)
            session.commit()

    def get_documents(self, user_id: int):
        with self.Session() as session:
            return session.query(Document).filter_by(user_id=user_id).all()