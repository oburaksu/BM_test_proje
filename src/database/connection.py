# =============================================
# Veritabanı Bağlantısı ve Session Yönetimi
# =============================================
# Bu modül SQLAlchemy kullanarak veritabanı bağlantısını kurar.
# - Engine: Veritabanı motorunu oluşturur (SQLite veya PostgreSQL)
# - SessionLocal: Her istek için yeni bir veritabanı oturumu açar
# - Base: Tüm ORM modellerinin miras alacağı temel sınıf
# - get_db: FastAPI dependency injection ile her endpoint'e DB oturumu sağlar
#
# Mimari Karar: SQLAlchemy'nin "Session" yapısını kullanıyoruz çünkü:
# 1. Her HTTP isteği kendi izole veritabanı oturumuna sahip olur
# 2. İstek bittiğinde oturum otomatik kapatılır (bellek sızıntısı önlenir)
# 3. Dependency Injection sayesinde testlerde kolayca mock'lanabilir

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.utils.config import settings

# ---- Veritabanı Motoru (Engine) ----
# create_engine: SQLAlchemy'nin veritabanına bağlanmak için kullandığı motor
# connect_args: SQLite için thread güvenliği ayarı (FastAPI çoklu thread kullanır)
# SQLite kullanıldığında check_same_thread=False gereklidir çünkü
# FastAPI farklı thread'lerden aynı bağlantıyı kullanabilir
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite için zorunlu
    )
else:
    # PostgreSQL veya diğer veritabanları için ek ayar gerekmez
    engine = create_engine(settings.DATABASE_URL)

# ---- Oturum Fabrikası (Session Factory) ----
# sessionmaker: Her çağrıda yeni bir veritabanı oturumu oluşturan fabrika
# autocommit=False: Değişiklikleri otomatik kaydetme, biz kontrol edeceğiz
# autoflush=False: SQL sorgularını otomatik göndermemesi için
# bind=engine: Bu oturumların hangi veritabanı motorunu kullanacağını belirtir
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---- Temel Model Sınıfı ----
# declarative_base: Tüm SQLAlchemy modellerinin miras alacağı temel sınıf
# Bu sayede Python sınıfları otomatik olarak veritabanı tablolarına dönüşür
Base = declarative_base()


def get_db():
    """
    FastAPI Dependency Injection için veritabanı oturumu sağlayıcı.

    Bu fonksiyon bir 'generator' (üreteç) fonksiyondur:
    1. Yeni bir veritabanı oturumu (session) oluşturur
    2. Bu oturumu endpoint fonksiyonuna 'yield' ile verir
    3. İstek tamamlandığında (başarılı veya hatalı) oturumu kapatır

    Kullanım (endpoint'te):
        @router.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            ...

    Bu pattern sayesinde:
    - Her HTTP isteği kendi bağımsız DB oturumuna sahip olur
    - Oturum yaşam döngüsü otomatik yönetilir
    - Bellek sızıntıları önlenir
    """
    db = SessionLocal()
    try:
        yield db  # Oturumu endpoint'e ver
    finally:
        db.close()  # İstek bitince oturumu kapat (hata olsa bile)
