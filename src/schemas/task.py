# =============================================
# Pydantic Request/Response Şemaları
# =============================================
# Bu modül API'nin giriş (request) ve çıkış (response) veri yapılarını tanımlar.
# Pydantic şemaları şu görevleri üstlenir:
# 1. Gelen veriyi otomatik doğrular (validation)
# 2. Yanlış tip gönderildiğinde anlaşılır hata mesajları üretir
# 3. API dokümantasyonunu (Swagger/OpenAPI) otomatik oluşturur
# 4. Veritabanı modellerinden bağımsız bir veri katmanı sağlar
#
# Mimari Karar: ORM modeli ve Pydantic şeması neden ayrı?
# - Model (SQLAlchemy): Veritabanı tablosunu temsil eder
# - Şema (Pydantic): API'nin kabul ettiği/döndüğü veriyi temsil eder
# Bu ayırım sayesinde:
# - API'ye gönderilen veri otomatik doğrulanır
# - Veritabanında olan ama API'de gösterilmemesi gereken alanlar gizlenebilir
# - İstek ve yanıt için farklı şemalar kullanılabilir

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =============================================
# TAG (Etiket) Şemaları
# =============================================

class TagCreate(BaseModel):
    """
    Yeni etiket oluşturmak için istek şeması.

    Kullanım: POST /api/tags
    Gönderilecek JSON: {"name": "acil"}
    """
    # Etiket adı: 1-50 karakter arası, zorunlu alan
    name: str = Field(
        ...,  # ... = zorunlu alan (required)
        min_length=1,
        max_length=50,
        description="Etiket adı",
        examples=["acil"]  # Swagger dokümantasyonunda görünen örnek
    )


class TagResponse(BaseModel):
    """
    Etiket yanıt şeması - API'nin döndüğü etiket verisi.

    Bu şema hem tekil hem de liste yanıtlarında kullanılır.
    """
    id: int = Field(description="Etiketin benzersiz kimliği")
    name: str = Field(description="Etiket adı")

    class Config:
        # from_attributes = True: SQLAlchemy nesnesinden otomatik dönüşüm sağlar
        # Örnek: TagResponse.model_validate(db_tag) çalışır
        from_attributes = True


# =============================================
# TASK (Görev) Şemaları
# =============================================

class TaskCreate(BaseModel):
    """
    Yeni görev oluşturmak için istek şeması.

    Kullanım: POST /api/tasks
    Gönderilecek JSON:
    {
        "title": "Raporu tamamla",
        "description": "Final raporu yazılacak",
        "tag_ids": [1, 2]
    }
    """
    # Görev başlığı: 1-200 karakter arası, zorunlu
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Görev başlığı",
        examples=["Proje raporunu hazırla"]
    )

    # Görev açıklaması: İsteğe bağlı, en fazla 1000 karakter
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Görev açıklaması (opsiyonel)",
        examples=["Cloud mimarileri dersi için final raporu yazılacak"]
    )

    # Atanacak etiket ID'leri: İsteğe bağlı, varsayılan boş liste
    tag_ids: list[int] = Field(
        default=[],
        description="Göreve atanacak etiket ID'lerinin listesi",
        examples=[[1, 2]]
    )


class TaskUpdate(BaseModel):
    """
    Mevcut bir görevi güncellemek için istek şeması.

    Kullanım: PUT /api/tasks/{task_id}
    Tüm alanlar opsiyoneldir - sadece güncellemek istenen alanlar gönderilir.
    Bu pattern'e "Partial Update" denir.

    Gönderilecek JSON:
    {
        "title": "Güncellenmiş başlık",
        "is_completed": true
    }
    """
    # Tüm alanlar Optional (opsiyonel) - sadece gönderilen alanlar güncellenir
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Yeni görev başlığı"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Yeni görev açıklaması"
    )
    is_completed: Optional[bool] = Field(
        default=None,
        description="Görev tamamlandı mı?"
    )
    tag_ids: Optional[list[int]] = Field(
        default=None,
        description="Yeni etiket ID'leri listesi"
    )


class TaskResponse(BaseModel):
    """
    Görev yanıt şeması - API'nin döndüğü görev verisi.

    Bu şema veritabanındaki Task nesnesini API yanıtına dönüştürür.
    Tarih alanları ISO 8601 formatında döner.
    Etiketler TagResponse listesi olarak döner.
    """
    id: int = Field(description="Görevin benzersiz kimliği")
    title: str = Field(description="Görev başlığı")
    description: Optional[str] = Field(description="Görev açıklaması")
    is_completed: bool = Field(description="Tamamlanma durumu")
    created_at: datetime = Field(description="Oluşturulma tarihi (UTC)")
    updated_at: datetime = Field(description="Son güncellenme tarihi (UTC)")
    tags: list[TagResponse] = Field(
        default=[],
        description="Göreve atanmış etiketler"
    )

    class Config:
        # SQLAlchemy nesnesinden Pydantic modeline otomatik dönüşüm
        from_attributes = True
