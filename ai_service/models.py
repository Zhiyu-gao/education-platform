# coding: utf-8
from sqlalchemy import Column, DateTime, Float, Integer, String
from database import Base


class RagDataset(Base):
    __tablename__ = 'rag_dataset'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_path = Column(String(255))
    upload_time = Column(DateTime)
    file_size = Column(Float(asdecimal=True))
    is_deleted = Column(String(255))
