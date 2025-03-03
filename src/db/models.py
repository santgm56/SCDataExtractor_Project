from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ScrapedData(Base):
    __tablename__ = "scraped_data" 

    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    tipo = Column(String(50), nullable=False)
    contenido = Column(String, nullable=False)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

