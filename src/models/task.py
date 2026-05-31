# =============================================
# Task (Görev) Veritabanı Modeli
# =============================================
# Bu modül SQLAlchemy ORM kullanarak 'tasks' tablosunu tanımlar.
# ORM (Object-Relational Mapping), veritabanı tablolarını Python sınıfları
# olarak temsil etmemizi sağlar. SQL yazmadan Python nesneleri ile
# veritabanı işlemleri yapabiliriz.
#
# Mimari Karar: İki entity (Task ve Tag) kullanıyoruz:
# - Task: Ana görev bilgilerini tutar
# - Tag: Görevlere etiket atamak için kullanılır (Many-to-Many ilişki)
# Bu yapı, projenin "1-2 entity, 4-6 REST endpoint" gereksinimini karşılar.

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

# ---- Çoka-Çok (Many-to-Many) İlişki Tablosu ----
# Task ve Tag arasındaki ilişkiyi kuran ara tablo
# Bir görevin birden fazla etiketi, bir etiketin birden fazla görevi olabilir
# Bu tablo doğrudan bir Python sınıfı olarak tanımlanmaz, SQLAlchemy onu otomatik yönetir
task_tags = Table(
    "task_tags",          # Tablo adı
    Base.metadata,        # SQLAlchemy metadata'sına bağla
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


class Tag(Base):
    """
    Etiket (Tag) modeli - Görevleri kategorize etmek için kullanılır.

    Örnek etiketler: "acil", "iş", "kişisel", "ödev" vb.
    Bir etiket birden fazla göreve atanabilir.
    """
    __tablename__ = "tags"  # Veritabanındaki tablo adı

    # Birincil anahtar: Her etiketin benzersiz kimliği
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Etiket adı: Benzersiz (unique) olmalı, tekrar edemez
    name = Column(String(50), unique=True, nullable=False, index=True)

    def __repr__(self) -> str:
        """Etiket nesnesinin okunabilir string gösterimi (debug için)."""
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Task(Base):
    """
    Görev (Task) modeli - To-Do uygulamasının ana veri yapısı.

    Her görev şu bilgileri içerir:
    - Başlık (title): Görevin kısa açıklaması
    - Açıklama (description): Görevin detaylı açıklaması (opsiyonel)
    - Tamamlanma durumu (is_completed): Görev yapıldı mı?
    - Oluşturulma tarihi (created_at): Görev ne zaman oluşturuldu?
    - Güncellenme tarihi (updated_at): Görev en son ne zaman güncellendi?
    - Etiketler (tags): Göreve atanan etiketler
    """
    __tablename__ = "tasks"  # Veritabanındaki tablo adı

    # ---- Sütun Tanımlamaları ----

    # Birincil anahtar: Her görevin benzersiz kimliği
    # autoincrement: Otomatik artan sayı (1, 2, 3, ...)
    # index: Hızlı arama için indeks oluşturur
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Görev başlığı: Zorunlu alan, en fazla 200 karakter
    title = Column(String(200), nullable=False)

    # Görev açıklaması: İsteğe bağlı alan, en fazla 1000 karakter
    description = Column(String(1000), nullable=True)

    # Tamamlanma durumu: Varsayılan olarak False (tamamlanmamış)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Oluşturulma tarihi: Görev oluşturulduğunda otomatik ayarlanır
    # UTC timezone kullanılır (sunucu konumundan bağımsız)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Güncellenme tarihi: Her güncelleme işleminde otomatik değişir
    # onupdate: SQLAlchemy her UPDATE sorgusunda bu değeri günceller
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # ---- İlişkiler (Relationships) ----
    # Task <-> Tag arasındaki çoka-çok ilişki
    # secondary: Ara tabloyu belirtir (task_tags)
    # back_populates yerine backref kullanılabilir ama back_populates daha açıktır
    # lazy="selectin": İlişkili verileri otomatik yükler (N+1 sorgu sorununu önler)
    tags = relationship("Tag", secondary=task_tags, lazy="selectin")

    def __repr__(self) -> str:
        """Görev nesnesinin okunabilir string gösterimi (debug için)."""
        status = "✓" if self.is_completed else "✗"
        return f"<Task(id={self.id}, title='{self.title}', completed={status})>"
