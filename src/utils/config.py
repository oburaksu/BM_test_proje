# =============================================
# Uygulama Konfigürasyon Yönetimi
# =============================================
# Bu modül Pydantic Settings kullanarak uygulama ayarlarını yönetir.
# Ayarlar öncelik sırasıyla şu kaynaklardan okunur:
# 1. Ortam değişkenleri (environment variables) - en yüksek öncelik
# 2. .env dosyası - ortam değişkeni yoksa buradan okunur
# 3. Varsayılan değerler - hiçbir kaynak yoksa kullanılır
#
# Mimari Karar: Pydantic Settings kullanmamızın nedenleri:
# 1. Tip güvenliği: Ayarlar otomatik olarak doğru tipe dönüştürülür
# 2. Doğrulama: Eksik veya hatalı ayarlar uygulama başlamadan tespit edilir
# 3. Güvenlik: Gizli bilgiler kod içinde değil, .env dosyasında tutulur
# 4. 12-Factor App: Konfigürasyonu koddan ayırma prensibi

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Uygulama ayarlarını .env dosyasından veya ortam değişkenlerinden okur.

    Her alan (field) bir konfigürasyon değerini temsil eder.
    'Field(default=...)' ile varsayılan değerler belirlenir.
    Ortam değişkeni varsa varsayılan değerin yerine geçer.
    """

    # --- Veritabanı Ayarları ---
    # SQLite: Basit, dosya tabanlı veritabanı (geliştirme ortamı için ideal)
    # PostgreSQL: Üretim ortamında kullanılacak güçlü veritabanı
    DATABASE_URL: str = Field(
        default="sqlite:///./todo.db",
        description="Veritabanı bağlantı URL'si"
    )

    # --- Uygulama Bilgileri ---
    APP_NAME: str = Field(
        default="To-Do List Manager",
        description="Uygulamanın görünen adı"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Uygulama sürüm numarası (Semantic Versioning)"
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug modu (True=geliştirme, False=üretim)"
    )

    # --- Sunucu Ayarları ---
    HOST: str = Field(
        default="0.0.0.0",
        description="Sunucunun dinleyeceği IP adresi"
    )
    PORT: int = Field(
        default=8000,
        description="Sunucunun dinleyeceği port numarası"
    )

    # --- AWS / LocalStack Ayarları ---
    AWS_ACCESS_KEY_ID: str = Field(
        default="test",
        description="AWS Erişim Anahtarı (LocalStack için 'test' kullanılabilir)"
    )
    AWS_SECRET_ACCESS_KEY: str = Field(
        default="test",
        description="AWS Gizli Anahtar (LocalStack için 'test' kullanılabilir)"
    )
    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS Bölgesi"
    )
    AWS_ENDPOINT_URL: str | None = Field(
        default="http://localhost:4566",
        description="LocalStack Endpoint URL'si (AWS'ye gidilecekse None olmalı)"
    )
    S3_BUCKET_NAME: str = Field(
        default="todo-bucket",
        description="Görev dosyalarının veya exportların tutulacağı S3 Bucketi"
    )

    class Config:
        """Pydantic Settings konfigürasyonu."""
        # .env dosyasının yolunu belirtir
        env_file = ".env"
        # .env dosyasının karakter kodlaması
        env_file_encoding = "utf-8"
        # Büyük-küçük harf duyarsız ortam değişkeni eşlemesi
        case_sensitive = False


# ---- Tekil (Singleton) Settings Nesnesi ----
# Uygulama genelinde tek bir settings nesnesi kullanılır
# Bu sayede her modül aynı konfigürasyona erişir
settings = Settings()
