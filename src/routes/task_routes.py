# =============================================
# Task (Görev) API Endpoint'leri
# =============================================
# Bu modül görevlerle ilgili tüm REST API endpoint'lerini tanımlar.
# FastAPI'nin APIRouter'ı kullanılır - bu sayede endpoint'ler modüler olarak
# ana uygulamaya (main.py) eklenir.
#
# REST API Endpoint Özeti:
# GET    /api/tasks          -> Tüm görevleri listele (filtreleme + sayfalama)
# GET    /api/tasks/{id}     -> Belirli bir görevi getir
# POST   /api/tasks          -> Yeni görev oluştur
# PUT    /api/tasks/{id}     -> Görevi güncelle
# DELETE /api/tasks/{id}     -> Görevi sil
# PATCH  /api/tasks/{id}/toggle -> Tamamlanma durumunu değiştir

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.services.task_service import TaskService

# ---- Router Oluştur ----
# prefix: Tüm endpoint'lere /api/tasks ön eki ekler
# tags: Swagger dokümantasyonunda gruplamak için
router = APIRouter(
    prefix="/api/tasks",
    tags=["Görevler (Tasks)"]
)


@router.get(
    "/",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Tüm görevleri listele",
    description="Görevleri filtreleme ve sayfalama ile listeler."
)
def get_all_tasks(
    skip: int = Query(default=0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(default=100, ge=1, le=500, description="Maks kayıt sayısı"),
    is_completed: Optional[bool] = Query(
        default=None,
        description="Tamamlanma durumuna göre filtrele"
    ),
    db: Session = Depends(get_db)  # Dependency Injection ile DB oturumu al
):
    """
    Tüm görevleri listeler.

    - **skip**: Sayfalama için atlanacak kayıt (varsayılan: 0)
    - **limit**: Getirilecek maksimum kayıt (varsayılan: 100)
    - **is_completed**: True/False ile filtreleme (opsiyonel)
    """
    return TaskService.get_all_tasks(db, skip=skip, limit=limit, is_completed=is_completed)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Belirli bir görevi getir"
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """ID'ye göre tek bir görev getirir. Bulunamazsa 404 döner."""
    return TaskService.get_task_by_id(db, task_id)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,  # 201: Başarıyla oluşturuldu
    summary="Yeni görev oluştur"
)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    Yeni bir görev oluşturur.

    - **title**: Görev başlığı (zorunlu)
    - **description**: Açıklama (opsiyonel)
    - **tag_ids**: Etiket ID'leri (opsiyonel)
    """
    return TaskService.create_task(db, task_data)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Görevi güncelle"
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Mevcut bir görevi günceller. Sadece gönderilen alanlar değişir."""
    return TaskService.update_task(db, task_id, task_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Görevi sil"
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Bir görevi kalıcı olarak siler."""
    return TaskService.delete_task(db, task_id)


@router.patch(
    "/{task_id}/toggle",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Tamamlanma durumunu değiştir"
)
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    """Görevin tamamlanma durumunu tersine çevirir (tamamlandı <-> tamamlanmadı)."""
    return TaskService.toggle_task_completion(db, task_id)


# --- S3 / LocalStack Entegrasyonu ---
@router.post(
    "/export-to-s3",
    summary="Tüm görevleri S3'e yedekle",
    description="Veritabanındaki tüm görevleri JSON formatında LocalStack (S3) üzerine yükler.",
    tags=["S3 Entegrasyonu"]
)
def export_tasks_to_s3(db: Session = Depends(get_db)):
    from src.utils.s3 import upload_json_to_s3
    from fastapi import HTTPException
    import datetime
    
    # 1. Tüm görevleri veritabanından çek
    tasks = TaskService.get_all_tasks(db)
    
    # 2. Pydantic şemalarına dönüştür (Serialization için)
    serialized_tasks = [TaskResponse.model_validate(t).model_dump() for t in tasks]
    
    # 3. Dosya ismini oluştur (örneğin: backup_2023-10-24T12-00-00.json)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"tasks_backup_{timestamp}.json"
    
    # 4. S3'e yükle
    s3_url = upload_json_to_s3(serialized_tasks, filename)
    
    if not s3_url:
        raise HTTPException(status_code=500, detail="S3 yükleme işlemi başarısız oldu. LocalStack çalışıyor mu?")
        
    return {
        "message": "Görevler başarıyla yedeklendi",
        "file_name": filename,
        "s3_url": s3_url,
        "total_tasks_exported": len(tasks)
    }
