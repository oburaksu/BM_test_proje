# =============================================
# Task (Gorev) Servis Katmani - Is Mantigi
# =============================================
# Bu modul veritabani CRUD (Create, Read, Update, Delete) islemlerini yonetir.
# Servis katmani, route (endpoint) katmani ile veritabani arasinda kopru gorevi gorur.
#
# Mimari Karar: Neden ayri bir servis katmani var?
# Route -> Service -> Database seklinde 3 katmanli mimari kullaniyoruz:
# 1. Route (Controller): HTTP isteklerini alir, servise yonlendirir
# 2. Service: Is mantigini calistirir, dogrulamalari yapar
# 3. Database: Veritabani islemlerini gerceklestirir

from sqlalchemy.orm import Session
from typing import Optional
from src.models.task import Task, Tag
from src.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException, status


class TaskService:
    """
    Gorev (Task) CRUD operasyonlarini yoneten servis sinifi.

    Her metod bir veritabani oturumu (session) alir ve islem yapar.
    Hata durumlarinda HTTPException firlatarak anlamli hata mesajlari doner.
    """

    @staticmethod
    def get_all_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_completed: Optional[bool] = None
    ) -> list[Task]:
        """
        Tum gorevleri listeler. Filtreleme ve sayfalama destekler.

        Args:
            db: Veritabani oturumu
            skip: Atlanacak kayit sayisi (sayfalama icin)
            limit: Getirilecek maksimum kayit sayisi
            is_completed: True ise sadece tamamlananlar, False ise tamamlanmayanlar

        Returns:
            Task listesi
        """
        # Temel sorguyu olustur
        query = db.query(Task)

        # Eger tamamlanma filtresi verilmisse uygula
        if is_completed is not None:
            query = query.filter(Task.is_completed == is_completed)

        # Olusturulma tarihine gore sirala (en yeni en ustte)
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Task:
        """
        Belirli bir gorevi ID'sine gore getirir.

        Args:
            db: Veritabani oturumu
            task_id: Gorevin benzersiz kimligi

        Returns:
            Bulunan Task nesnesi

        Raises:
            HTTPException(404): Gorev bulunamazsa
        """
        task = db.query(Task).filter(Task.id == task_id).first()

        # Gorev bulunamazsa 404 hatasi dondur
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID={task_id} olan gorev bulunamadi"
            )

        return task

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        """
        Yeni bir gorev olusturur.

        Args:
            db: Veritabani oturumu
            task_data: Gorev olusturma verileri (Pydantic semasi)

        Returns:
            Olusturulan Task nesnesi

        Raises:
            HTTPException(404): Belirtilen etiket ID'leri bulunamazsa
        """
        # Pydantic semasindan SQLAlchemy nesnesine donustur
        new_task = Task(
            title=task_data.title,
            description=task_data.description
        )

        # Eger etiket ID'leri verilmisse, etiketleri veritabanindan bul ve ata
        if task_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(task_data.tag_ids)).all()

            # Bulunan etiket sayisi ile istenen etiket sayisi eslesmeli
            if len(tags) != len(task_data.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(task_data.tag_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Su etiket ID'leri bulunamadi: {missing_ids}"
                )

            new_task.tags = tags

        # Veritabanina ekle, kaydet ve yeniden oku (ID atanmasi icin)
        db.add(new_task)        # Oturuma ekle
        db.commit()             # Degisiklikleri kaydet
        db.refresh(new_task)    # Otomatik uretilen alanlari (id, created_at) oku
        return new_task

    @staticmethod
    def update_task(db: Session, task_id: int, task_data: TaskUpdate) -> Task:
        """
        Mevcut bir gorevi gunceller (Partial Update).

        Sadece gonderilen alanlar guncellenir, digerleri ayni kalir.

        Args:
            db: Veritabani oturumu
            task_id: Guncellenecek gorevin ID'si
            task_data: Guncellenecek alanlar (Pydantic semasi)

        Returns:
            Guncellenmis Task nesnesi

        Raises:
            HTTPException(404): Gorev veya etiket bulunamazsa
        """
        # Once gorevi bul (yoksa 404 doner)
        task = TaskService.get_task_by_id(db, task_id)

        # model_dump: Pydantic nesnesini dict'e donusturur
        # exclude_unset=True: Sadece kullanicinin gonderdigi alanlari al
        update_data = task_data.model_dump(exclude_unset=True)

        # Etiket guncelleme varsa ozel olarak isle
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                if len(tags) != len(tag_ids):
                    found_ids = {tag.id for tag in tags}
                    missing_ids = set(tag_ids) - found_ids
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Su etiket ID'leri bulunamadi: {missing_ids}"
                    )
                task.tags = tags

        # Diger alanlari guncelle
        # setattr: Python'da bir nesnenin ozelligini dinamik olarak degistirir
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> dict:
        """
        Bir gorevi siler.

        Args:
            db: Veritabani oturumu
            task_id: Silinecek gorevin ID'si

        Returns:
            Silme onay mesaji

        Raises:
            HTTPException(404): Gorev bulunamazsa
        """
        # Once gorevi bul (yoksa 404 doner)
        task = TaskService.get_task_by_id(db, task_id)

        db.delete(task)    # Veritabanindan sil
        db.commit()        # Degisikligi kaydet

        return {"message": f"ID={task_id} olan gorev basariyla silindi"}

    @staticmethod
    def toggle_task_completion(db: Session, task_id: int) -> Task:
        """
        Bir gorevin tamamlanma durumunu tersine cevirir.

        Tamamlanmamis gorev -> Tamamlandi
        Tamamlanmis gorev -> Tamamlanmadi

        Args:
            db: Veritabani oturumu
            task_id: Gorevin ID'si

        Returns:
            Guncellenmis Task nesnesi
        """
        task = TaskService.get_task_by_id(db, task_id)

        # Boolean degeri tersine cevir
        task.is_completed = not task.is_completed

        db.commit()
        db.refresh(task)
        return task
