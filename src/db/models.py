from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ScrapingSession(Base):
    """Sesión de scraping para agrupar extracciones"""
    __tablename__ = "scraping_sessions"
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    total_items = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    scraped_items = relationship(
        "ScrapedData", 
        back_populates="session",
        cascade="all, delete-orphan"
    )


class ScrapedData(Base):
    """Datos base para todos los tipos de scraping"""
    __tablename__ = "scraped_data"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    
    # Campo para almacenar datos genéricos en JSON
    contenido = Column(JSON)
    
    # Auditoría
    fecha_extraccion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relación con sesión
    session_id = Column(Integer, ForeignKey('scraping_sessions.id', ondelete='SET NULL'))
    session = relationship("ScrapingSession", back_populates="scraped_items")
    
    # Polimorfismo
    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'generic'
    }
    
    __table_args__ = (
        Index('idx_url_tipo', 'url', 'tipo', unique=True),
        Index('idx_tipo_fecha', 'tipo', 'fecha_extraccion'),
    )


class ProductoEcommerce(ScrapedData):
    """Modelo para productos de e-commerce - SOLO campos scrapeados"""
    __tablename__ = "productos_ecommerce"
    
    id = Column(Integer, ForeignKey('scraped_data.id'), primary_key=True)
    
    # ✅ De "title" → "nombre"
    nombre = Column(String(500), nullable=False, index=True)
    
    # ✅ De "image" → "imagen_url"
    imagen_url = Column(String(500))
    
    # ✅ Precios como Float (convertir desde "$129.900")
    precio_original = Column(Float)
    precio = Column(Float)  # price_sell
    
    # ✅ De "discount" → "descuento" (mantener como String: "27%")
    descuento = Column(String(20))
    
    # ✅ De "rating" Dict → guardar completo en JSON
    rating_metadata = Column(JSON)  # {"rating": "N/A", "rating_count": "Sin calificaciones"}
    
    # ✅ De "description" → "descripcion" (JSON para mantener estructura de listas)
    descripcion = Column(JSON)
    
    __mapper_args__ = {
        'polymorphic_identity': 'e-commerce'
    }
    
    __table_args__ = (
        Index('idx_nombre', 'nombre'),
        Index('idx_precio', 'precio'),
    )

