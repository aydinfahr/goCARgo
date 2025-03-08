from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ SQLite Veritabanı Bağlantısı (Varsayılan)
DATABASE_URL = "sqlite:///./gocargo.db"  # SQLite dosyanızın adı

# ✅ PostgreSQL veya MySQL Kullanıyorsanız Burayı Güncelleyin:
# PostgreSQL için:
# DATABASE_URL = "postgresql://username:password@localhost:5432/gocargo"
# MySQL için:
# DATABASE_URL = "mysql+pymysql://username:password@localhost/gocargo"

# ✅ SQLAlchemy Motorunu Başlat (SQLite için özel parametre eklendi)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ✅ ORM için Session (Oturum) Yöneticisi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ SQLAlchemy ORM Base Modeli
Base = declarative_base()

# ✅ Veritabanı Bağlantısını Sağlayan Fonksiyon (FastAPI'de Kullanılacak)
def get_db():
    """
    Returns a database session. Automatically closes when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
