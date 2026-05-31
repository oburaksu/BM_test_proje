# =============================================
# Tag (Etiket) Servis Katmanı
# =============================================
# Etiketlerin CRUD işlemlerini yönetir.

from sqlalchemy.orm import Session
from src.models.task import Tag
from src.schemas.task import TagCreate
from fastapi import HTTPException, status


class TagService:
    """Etiket CRUD operasyonlarını yöneten servis sınıfı."""

    @staticmethod
    def get_all_tags(db: Session) -> list[Tag]:
        """Tüm etiketleri listeler."""
        return db.query(Tag).order_by(Tag.name).all()

    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> Tag:
        """
        Yeni etiket oluşturur.
        Aynı isimde etiket varsa 400 hatası döner.
        """
        # Aynı isimde etiket var mı kontrol et
        existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{tag_data.name}' isimli etiket zaten mevcut"
            )

        new_tag = Tag(name=tag_data.name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag

    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> dict:
        """Bir etiketi siler."""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID={tag_id} olan etiket bulunamadı"
            )
        db.delete(tag)
        db.commit()
        return {"message": f"'{tag.name}' etiketi başarıyla silindi"}
