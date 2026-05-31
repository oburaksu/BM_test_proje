# =============================================
# Entegrasyon Testleri (Veritabanı / Testcontainers)
# =============================================
# Gerçek bir veritabanı motoru üzerinde uygulamanın davranışını test eder.
# Testcontainers kullanarak izole edilmiş geçici bir PostgreSQL ayağa kaldırır.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.models.task import Task
from src.database.connection import Base


@pytest.fixture(scope="module")
def postgres_container():
    """
    Testcontainers ile geçici bir PostgreSQL konteyneri başlatır.
    Testler bittiğinde otomatik olarak kapatılır ve silinir.
    """
    try:
        # PostgreSQL 15 imajını kullan
        with PostgresContainer("postgres:15-alpine") as postgres:
            yield postgres
    except Exception as e:
        pytest.skip(f"Docker is not available or testcontainers failed: {e}")


@pytest.fixture(scope="module")
def pg_engine(postgres_container):
    """PostgreSQL konteynerine bağlanan bir SQLAlchemy engine oluşturur."""
    # Konteynerın sağladığı dinamik URL'yi al
    db_url = postgres_container.get_connection_url()
    
    engine = create_engine(db_url)
    # Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    yield engine
    # Tabloları sil (Konteyner zaten kapanacağı için çok şart değil ama iyi pratik)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def pg_session(pg_engine):
    """Her test için yeni bir PostgreSQL oturumu açar."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_postgres_task_creation(pg_session):
    """
    Gerçek PostgreSQL üzerinde Task oluşturma testi.
    ORM modellerinin PostgreSQL dialect'i ile uyumlu çalıştığını doğrular.
    """
    # Yeni görev oluştur
    new_task = Task(title="Postgres Entegrasyon Testi", description="Testcontainers çalışıyor mu?")
    pg_session.add(new_task)
    pg_session.commit()
    pg_session.refresh(new_task)

    # Veritabanından geri oku
    db_task = pg_session.query(Task).filter(Task.id == new_task.id).first()
    
    assert db_task is not None
    assert db_task.title == "Postgres Entegrasyon Testi"
    assert db_task.is_completed is False


def test_postgres_task_completion_update(pg_session):
    """
    PostgreSQL üzerinde güncelleme (Update) işleminin testi.
    """
    task = Task(title="Güncellenecek Görev")
    pg_session.add(task)
    pg_session.commit()
    
    # Güncelleme
    task.is_completed = True
    pg_session.commit()
    
    # Doğrulama
    db_task = pg_session.query(Task).filter(Task.id == task.id).first()
    assert db_task.is_completed is True


def test_postgres_task_deletion(pg_session):
    """
    PostgreSQL üzerinde silme (Delete) işleminin testi.
    """
    # Silinecek görevi ekle
    task = Task(title="Silinecek Postgres Görevi")
    pg_session.add(task)
    pg_session.commit()
    
    task_id = task.id
    
    # Görevi sil
    pg_session.delete(task)
    pg_session.commit()
    
    # Veritabanında olmadığını doğrula
    deleted_task = pg_session.query(Task).filter(Task.id == task_id).first()
    assert deleted_task is None
