# =============================================
# Pytest Fixtures (Test Ortamı Ayarları)
# =============================================
# Bu modül tüm test dosyalarında ortak kullanılacak "fixture"ları tanımlar.
# Fixture'lar testler çalışmadan önce hazırlık (setup) ve testlerden sonra
# temizlik (teardown) işlemlerini yapar.

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Uygulama başlamadan önce çevre değişkenlerini test için ez
os.environ["DATABASE_URL"] = "sqlite:///./test_todo.db"
os.environ["DEBUG"] = "true"

from src.main import app
from src.database.connection import Base, get_db

# Test veritabanı bağlantısı
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_todo.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """
    Her test fonksiyonundan önce veritabanı tablolarını temizler ve yeniden oluşturur.
    Bu sayede testler birbirinden izole çalışır.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Her test fonksiyonu için yeni bir veritabanı oturumu oluşturur.
    Test bittiğinde oturumu kapatır.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient'ı döndürür.
    Gerçek veritabanı yerine test veritabanını kullanması için
    dependency injection override işlemini yapar.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Override'ı temizle
    app.dependency_overrides.clear()
