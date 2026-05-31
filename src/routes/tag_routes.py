# =============================================
# Tag (Etiket) API Endpoint'leri
# =============================================
# Etiketlerle ilgili REST API endpoint'lerini tanımlar.
#
# REST API Endpoint Özeti:
# GET    /api/tags          -> Tüm etiketleri listele
# POST   /api/tags          -> Yeni etiket oluştur
# DELETE /api/tags/{id}     -> Etiketi sil

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.task import TagCreate, TagResponse
from src.services.tag_service import TagService

# ---- Router Oluştur ----
router = APIRouter(
    prefix="/api/tags",
    tags=["Etiketler (Tags)"]
)


@router.get(
    "/",
    response_model=list[TagResponse],
    status_code=status.HTTP_200_OK,
    summary="Tüm etiketleri listele"
)
def get_all_tags(db: Session = Depends(get_db)):
    """Tüm etiketleri alfabetik sırada listeler."""
    return TagService.get_all_tags(db)


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni etiket oluştur"
)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """
    Yeni bir etiket oluşturur.
    Aynı isimde etiket varsa 400 hatası döner.
    """
    return TagService.create_tag(db, tag_data)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_200_OK,
    summary="Etiketi sil"
)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Bir etiketi kalıcı olarak siler."""
    return TagService.delete_tag(db, tag_id)
