# =============================================
# FastAPI Ana Uygulama Dosyası
# =============================================
# Bu dosya uygulamanın giriş noktasıdır (entry point).
# Tüm bileşenleri bir araya getirir:
# 1. FastAPI uygulamasını oluşturur
# 2. Veritabanı tablolarını oluşturur
# 3. Router'ları (endpoint gruplarını) uygulamaya bağlar
# 4. /health endpoint'i ile uygulamanın sağlık durumunu raporlar
#
# Çalıştırma komutu:
#   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
#
# API Dokümantasyonu:
#   Swagger UI:  http://localhost:8000/docs
#   ReDoc:       http://localhost:8000/redoc

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from src.database.connection import engine, Base
from src.models.task import Task, Tag  # noqa: F401 - Tabloların oluşturulması için import gerekli
from src.routes.task_routes import router as task_router
from src.routes.tag_routes import router as tag_router
from src.utils.config import settings

# ---- Veritabanı Tablolarını Oluştur ----
# Base.metadata.create_all: Tanımlanan tüm modellere göre tabloları oluşturur
# Tablolar zaten varsa tekrar oluşturmaz (idempotent)
# Bu sayede uygulama her başladığında tablo kontrolü otomatik yapılır
Base.metadata.create_all(bind=engine)

# ---- FastAPI Uygulamasını Oluştur ----
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Bulut Mimarilerinde Test Mühendisliği dersi projesi. "
        "Görev oluşturma, listeleme, tamamlama ve etiketleme API'si."
    ),
    # Swagger UI'daki endpoint gruplarının açıklamaları
    openapi_tags=[
        {
            "name": "Sağlık Kontrolü (Health)",
            "description": "Uygulama sağlık durumu endpoint'i"
        },
        {
            "name": "Görevler (Tasks)",
            "description": "Görev CRUD operasyonları"
        },
        {
            "name": "Etiketler (Tags)",
            "description": "Etiket yönetimi"
        }
    ]
)

# ---- CORS Middleware ----
# CORS (Cross-Origin Resource Sharing): Farklı domain'lerden gelen istekleri kontrol eder
# Geliştirme ortamında tüm origin'lere izin veriyoruz (üretimde kısıtlanmalı)
# E2E testleri (Adım 7) için frontend'in API'ye erişmesi gerekecek
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Tüm domain'lere izin ver (dev ortamı)
    allow_credentials=True,    # Cookie göndermeye izin ver
    allow_methods=["*"],       # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],       # Tüm header'lara izin ver
)

# ---- Router'ları Uygulamaya Bağla ----
# include_router: Modüler olarak tanımlanan endpoint gruplarını ana uygulamaya ekler
app.include_router(task_router)
app.include_router(tag_router)

# ---- Monitoring (Adım 5) ----
# Prometheus FastAPI Instrumentator ile metrikleri dışa aktar
# Bu kod, gelen/giden istek sayısını, sürelerini ve hataları /metrics endpoint'inde sunar
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)


# ---- E2E Test İçin Arayüz (Adım 7) ----
# Uygulamanın /ui yolunda src/static dizinini sunmasını sağlıyoruz.
from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")


# ---- Health Check (Sağlık Kontrolü) Endpoint'i ----
@app.get(
    "/health",
    tags=["Sağlık Kontrolü (Health)"],
    summary="Uygulama sağlık kontrolü",
    description="CI/CD pipeline'ında smoke test olarak kullanılır."
)
def health_check():
    """
    Uygulamanın çalışıp çalışmadığını kontrol eden endpoint.

    Bu endpoint CI/CD pipeline'ında (Adım 9) smoke test olarak kullanılacak.
    Kubernetes'te (Adım 8) liveness/readiness probe olarak da kullanılabilir.

    Dönen bilgiler:
    - status: Uygulama durumu ("healthy")
    - app_name: Uygulama adı
    - version: Sürüm numarası
    - timestamp: Yanıt zamanı (UTC)
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ---- Kök (Root) Endpoint ----
@app.get(
    "/",
    tags=["Sağlık Kontrolü (Health)"],
    summary="API karşılama mesajı"
)
def root():
    """API'nin kök URL'sine yapılan isteklere karşılama mesajı döner."""
    return {
        "message": f"{settings.APP_NAME}'a hoş geldiniz!",
        "docs": "/docs",
        "health": "/health"
    }
