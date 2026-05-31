# =============================================
# Task Servisi Birim (Unit) Testleri
# =============================================
# Servis katmanının (iş mantığı) doğru çalışıp çalışmadığını test eder.
# Endpoint'lerden bağımsız olarak doğrudan servis fonksiyonları çağrılır.

import pytest
from fastapi import HTTPException
from src.services.task_service import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from tests.factories import TaskFactory, TagFactory


def test_get_all_tasks(db_session):
    """Tüm görevleri listeleme işlemi test edilir."""
    # Veritabanına factory ile 3 görev ekle
    TaskFactory._meta.sqlalchemy_session = db_session
    TaskFactory.create_batch(3)
    
    # Servisi çağır
    tasks = TaskService.get_all_tasks(db_session)
    
    # 3 görev döndüğünü doğrula
    assert len(tasks) == 3


def test_get_task_by_id_success(db_session):
    """Mevcut bir görevi ID'ye göre getirme işlemi test edilir."""
    TaskFactory._meta.sqlalchemy_session = db_session
    # Yeni bir görev oluştur
    task = TaskFactory.create(title="Test Görevi")
    
    # Servisten görevi iste
    fetched_task = TaskService.get_task_by_id(db_session, task.id)
    
    assert fetched_task.id == task.id
    assert fetched_task.title == "Test Görevi"


def test_get_task_by_id_not_found(db_session):
    """Olmayan bir ID istendiğinde 404 dönmesi test edilir."""
    # Exception fırlatması gerektiğini belirt
    with pytest.raises(HTTPException) as exc_info:
        TaskService.get_task_by_id(db_session, 999)
    
    assert exc_info.value.status_code == 404


def test_create_task(db_session):
    """Yeni görev oluşturma işlemi test edilir."""
    task_data = TaskCreate(
        title="Yeni API Tasarımı",
        description="REST API tasarımı yapılacak"
    )
    
    created_task = TaskService.create_task(db_session, task_data)
    
    assert created_task.id is not None
    assert created_task.title == "Yeni API Tasarımı"
    assert created_task.is_completed is False


def test_create_task_with_tags(db_session):
    """Etiketlerle birlikte yeni görev oluşturma işlemi test edilir."""
    # Önce etiketleri veritabanına ekle
    TagFactory._meta.sqlalchemy_session = db_session
    tag1 = TagFactory.create(name="frontend")
    tag2 = TagFactory.create(name="backend")
    
    task_data = TaskCreate(
        title="Fullstack Geliştirme",
        tag_ids=[tag1.id, tag2.id]
    )
    
    created_task = TaskService.create_task(db_session, task_data)
    
    assert len(created_task.tags) == 2
    assert created_task.tags[0].name in ["frontend", "backend"]


def test_update_task(db_session):
    """Görev güncelleme (Partial Update) işlemi test edilir."""
    TaskFactory._meta.sqlalchemy_session = db_session
    task = TaskFactory.create(title="Eski Başlık", is_completed=False)
    
    update_data = TaskUpdate(title="Yeni Başlık", is_completed=True)
    updated_task = TaskService.update_task(db_session, task.id, update_data)
    
    assert updated_task.title == "Yeni Başlık"
    assert updated_task.is_completed is True
    # Description güncellenmediği için None olması veya önceki değerinde kalması gerekir
    # Model oluşturulurken faker kullanıldığı için assertion title üzerine yapıldı


def test_delete_task(db_session):
    """Görev silme işlemi test edilir."""
    TaskFactory._meta.sqlalchemy_session = db_session
    task = TaskFactory.create()
    
    response = TaskService.delete_task(db_session, task.id)
    assert response["message"] == f"ID={task.id} olan gorev basariyla silindi"
    
    # Silindikten sonra tekrar bulmaya çalışırsak 404 almalıyız
    with pytest.raises(HTTPException):
        TaskService.get_task_by_id(db_session, task.id)


def test_toggle_task_completion(db_session):
    """Görevin tamamlanma durumunu değiştirme işlemi test edilir."""
    TaskFactory._meta.sqlalchemy_session = db_session
    task = TaskFactory.create(is_completed=False)
    
    # False'dan True'ya
    updated_task = TaskService.toggle_task_completion(db_session, task.id)
    assert updated_task.is_completed is True
    
    # True'dan False'a
    updated_task = TaskService.toggle_task_completion(db_session, task.id)
    assert updated_task.is_completed is False
