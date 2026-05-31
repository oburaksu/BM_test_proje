# 📝 To-Do List Manager

Bulut Mimarilerinde Test Mühendisliği dersi dönem projesi.  
Görev oluşturma, listeleme, tamamlama ve etiketleme REST API uygulaması.

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Veritabanı | SQLite (geliştirme) / PostgreSQL (üretim) |
| ORM | SQLAlchemy 2.0 |
| Doğrulama | Pydantic v2 |
| Sunucu | Uvicorn (ASGI) |

## 📂 Proje Yapısı

```
my-project/
├── src/
│   ├── main.py           # FastAPI app ve /health endpoint
│   ├── routes/           # API endpoint'leri
│   ├── models/           # SQLAlchemy veritabanı modelleri
│   ├── schemas/          # Pydantic request/response şemaları
│   ├── services/         # İş mantığı katmanı
│   ├── database/         # Veritabanı bağlantısı
│   └── utils/            # Konfigürasyon yönetimi
├── tests/                # Test dosyaları (Adım 2)
├── requirements.txt      # Python bağımlılıkları
├── .env.example          # Örnek çevre değişkenleri
└── README.md
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.11+
- pip

### Adım 1: Sanal ortam oluştur ve etkinleştir

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Adım 2: Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### Adım 3: Çevre değişkenlerini ayarla

```bash
copy .env.example .env
```

### Adım 4: Uygulamayı çalıştır

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### API Dokümantasyonu

Uygulama çalıştıktan sonra:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

### Adım 5: Kubernetes (Minikube) Üzerinde Çalıştırma

Eğer Minikube yüklüyse, uygulamayı Kubernetes üzerinde de koşturabilirsiniz:

```bash
# Minikube başlatın
minikube start

# Docker imajını Minikube ortamında derleyin (Windows PowerShell)
minikube docker-env | Invoke-Expression
docker build -t todo-app:latest .

# Kubernetes objelerini oluşturun
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Tarayıcıda uygulamayı açın
minikube service todo-app-service
```

### Adım 6: CI/CD Süreci (GitHub Actions)
Projeyi GitHub'a push yaptığınızda, `.github/workflows/ci.yml` devreye girerek sırasıyla şu testleri koşar:
1. Linting (Flake8)
2. Birim/E2E Testleri (Pytest)
3. Docker Build Kontrolü
4. Deploy (Mock Deployment)
5. Sağlık Taraması (Smoke Test)


## 📡 API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/health` | Sağlık kontrolü (smoke test) |
| GET | `/api/tasks/` | Tüm görevleri listele |
| GET | `/api/tasks/{id}` | Belirli bir görevi getir |
| POST | `/api/tasks/` | Yeni görev oluştur |
| PUT | `/api/tasks/{id}` | Görevi güncelle |
| DELETE | `/api/tasks/{id}` | Görevi sil |
| PATCH | `/api/tasks/{id}/toggle` | Tamamlanma durumunu değiştir |
| GET | `/api/tags/` | Tüm etiketleri listele |
| POST | `/api/tags/` | Yeni etiket oluştur |
| DELETE | `/api/tags/{id}` | Etiketi sil |

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
