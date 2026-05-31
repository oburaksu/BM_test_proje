# 📊 Proje Gelişim Takip Dosyası

## Adım 1: API & Veritabanı Kurulumu

### Amaç
FastAPI ile modüler bir REST API oluşturmak, SQLite veritabanı bağlantısını kurmak ve Task/Tag entity'leri için CRUD endpoint'lerini yazmak.

### Eklenen Dosyalar
- `requirements.txt` - Python bağımlılıkları
- `.env` / `.env.example` - Çevre değişkenleri
- `src/__init__.py` - Kaynak kod paketi
- `src/main.py` - FastAPI ana uygulaması ve /health endpoint
- `src/database/__init__.py` - Veritabanı paketi
- `src/database/connection.py` - SQLAlchemy bağlantı yönetimi
- `src/models/__init__.py` - Model paketi
- `src/models/task.py` - Task ve Tag SQLAlchemy modelleri
- `src/schemas/__init__.py` - Şema paketi
- `src/schemas/task.py` - Pydantic request/response şemaları
- `src/services/__init__.py` - Servis paketi
- `src/services/task_service.py` - Task CRUD iş mantığı
- `src/services/tag_service.py` - Tag CRUD iş mantığı
- `src/routes/__init__.py` - Route paketi
- `src/routes/task_routes.py` - Task API endpoint'leri
- `src/routes/tag_routes.py` - Tag API endpoint'leri
- `src/utils/__init__.py` - Utils paketi
- `src/utils/config.py` - Pydantic Settings konfigürasyonu
- `README.md` - Proje dokümantasyonu
- `LICENSE` - MIT lisansı

### Yazılan Özellikler
- **2 Entity:** Task (görev) ve Tag (etiket) - Many-to-Many ilişki
- **10 REST Endpoint:** 
  - GET /health (smoke test)
  - GET / (karşılama)
  - Task: GET list, GET by ID, POST create, PUT update, DELETE, PATCH toggle
  - Tag: GET list, POST create, DELETE
- **Modüler Mimari:** routes → services → database 3 katmanlı yapı
- **Konfigürasyon:** .env dosyasından ortam değişkeni okuma
- **CORS:** Frontend erişimi için middleware
- **Swagger/OpenAPI:** Otomatik API dokümantasyonu

### Kullanılan Teknolojiler
- Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn, SQLite

### Çalıştırılan Terminal Komutları
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Karşılaşılan Sorunlar ve Çözümleri
- (İlk kurulum - sorun yok)

## Adım 2: Testler (Birim ve Entegrasyon)

### Amaç
Pytest, Factory Boy, Faker ve Testcontainers kullanarak projenin servis ve API katmanları için Unit ve Integration testleri yazmak, en az %70 kod kapsamına (coverage) ulaşmak.

### Eklenen Dosyalar
- `pytest.ini` - Pytest konfigürasyon ve ayar dosyası
- `tests/conftest.py` - Ortak pytest fixture'ları (Veritabanı izolasyonu, TestClient)
- `tests/factories.py` - Factory Boy ve Faker tabanlı test verisi üreticileri
- `tests/unit/test_task_service.py` - Task servis katmanı birim testleri
- `tests/unit/test_task_routes.py` - Task API endpoint'leri birim testleri
- `tests/integration/test_db.py` - Testcontainers ile PostgreSQL entegrasyon testleri

### Yazılan Özellikler
- **Birim Testler (Unit):** Toplam 15 test (Servis ve API)
- **Entegrasyon Testler:** PostgreSQL konteyneri ayağa kaldırılarak ORM uyumluluk testi
- **Test Kapsamı (Coverage):** Uygulama genelinde %83 kod kapsamı sağlandı.
- **Fixture ve İzolasyon:** Her test öncesi ve sonrası veritabanı tablolarının yeniden oluşturularak testlerin izole çalışması sağlandı.

### Kullanılan Teknolojiler
- pytest, pytest-cov, httpx (TestClient için), factory-boy, faker, testcontainers, psycopg2-binary

### Çalıştırılan Terminal Komutları
```bash
# Test bağımlılıklarını yükle
pip install -r requirements.txt

# Testleri ve Coverage'ı çalıştır
pytest
```

### Karşılaşılan Sorunlar ve Çözümleri
- **Veritabanı İzolasyonu:** Testler arası durum (state) sızıntısı yaşandı. Çözüm olarak `conftest.py` içindeki `setup_test_db` fixture scope'u `function` yapıldı ve her testte tablolar `drop_all` / `create_all` ile sıfırlandı.
- **Testcontainers Docker Hatası:** Windows ortamında Docker deamon'a erişilemediğinde testlerin çökmemesi için `test_db.py` içinde `try-except` bloğu eklendi ve Docker yoksa testin atlanması (`pytest.skip`) sağlandı.
- **Encoding Uyuşmazlığı:** Servis mesajındaki Türkçe karakterler ile test dosyasındaki karakterlerin uyuşmaması (ö, ş, ı, vb.) düzeltildi.

## Adım 3: Konteyner & AWS

### Amaç
Uygulamayı Multi-stage Dockerfile ile konteynerize etmek, docker-compose.yml ile orkestrasyonu sağlamak ve AWS simülasyonu olarak LocalStack (S3) entegrasyonu yapmak.

### Eklenen Dosyalar
- `Dockerfile` - Multi-stage imaj derleme dosyası (builder ve runner aşamaları)
- `docker-compose.yml` - FastAPI, LocalStack ve PostgreSQL servislerini içeren orkestrasyon dosyası
- `.dockerignore` - Docker build context'ini temiz tutmak için yoksayılan dosyalar
- `src/utils/s3.py` - Boto3 ile AWS/LocalStack S3 iletişimini yöneten util modülü

### Yazılan Özellikler
- **Konteynerizasyon:** Uygulamanın çalışması için gerekli tüm ortam (Python, bağımlılıklar, kod) Docker imajı içine paketlendi.
- **Multi-Stage Build:** İmaj boyutu ve güvenliği optimize edildi (derleme araçları final imajda yok).
- **LocalStack Entegrasyonu:** Gerçek bir AWS hesabı kullanmadan yerelde S3 servisi simüle edildi.
- **S3 Yedekleme Endpoint'i:** `POST /api/tasks/export-to-s3` endpoint'i eklenerek görevlerin JSON formatında S3 (LocalStack) bucket'ına yedeklenmesi sağlandı.

### Kullanılan Teknolojiler
- Docker, Docker Compose, LocalStack, Boto3

### Çalıştırılan Terminal Komutları
```bash
# Gerekli kütüphanenin kurulumu
pip install boto3

# Uygulamanın Docker ile ayağa kaldırılması
docker-compose up -d --build
```

## Adım 4: API Testleri (Postman ve Newman)

### Amaç
Projenin API endpoint'lerini test etmek için bir Postman Collection oluşturmak ve otomasyon süreçleri (CI/CD) için Newman aracı ile bu testleri terminal üzerinden koşulabilir hale getirmek.

### Eklenen Dosyalar
- `postman/collection.json` - 6 temel API isteği ve bu isteklere ait Javascript testlerini (Assertions) barındıran Postman dosyası
- `postman/env.json` - `base_url` gibi değişkenleri barındıran ortam (environment) dosyası
- `package.json` - npm bağımlılıklarını ve Newman test komutunu (`test:api`) tanımlayan dosya

### Yazılan Özellikler
- **Koleksiyon Tasarımı:** Health Check, Görev Oluşturma, Getirme, Güncelleme, Durum Değiştirme (Toggle) ve Silme işlemlerini test eden sırayla (flow) çalışan 6 farklı istek (request) yazıldı.
- **Dinamik Veri Akışı:** POST isteğinde oluşturulan görevin ID'si otomatik olarak ortam değişkenlerine kaydedilerek (`pm.environment.set("task_id", jsonData.id);`) sonraki isteklerde `{{task_id}}` şeklinde dinamik olarak kullanılması sağlandı.
- **Otomasyon Komutu:** `npm run test:api` komutu ile testlerin manuel müdahale olmadan konsolda koşulması sağlandı. 11 adet "Assertion" başarılı şekilde doğrulandı.

### Kullanılan Teknolojiler
- Postman (JSON formatında Collection ve Environment), Newman, npm (Node Package Manager)

### Çalıştırılan Terminal Komutları
```powershell
# Bağımlılıkları (newman) kur ve testleri terminalde çalıştır
npm install
npm run test:api
```

## Adım 5: İzleme (Monitoring)

### Amaç
Uygulamanın sağlık durumunu, HTTP isteklerini, hata oranlarını ve yanıt sürelerini gözlemleyebilmek için Prometheus metrikleri dışa açmak ve bu metrikleri Grafana üzerinden görselleştirmek.

### Eklenen Dosyalar
- `monitoring/prometheus.yml` - Prometheus sunucusunun FastAPI'dan metrikleri alması (scrape) için konfigürasyon.
- `monitoring/grafana/provisioning/datasources/datasource.yml` - Grafana'ya Prometheus'u otomatik veri kaynağı (datasource) olarak ekleyen dosya.
- `monitoring/grafana/provisioning/dashboards/...` - Grafana açılır açılmaz "To-Do List API Dashboard"un yüklü gelmesini sağlayan konfigürasyon ve JSON dashboard dosyası.

### Yazılan Özellikler
- **FastAPI Instrumentation:** `prometheus-fastapi-instrumentator` kütüphanesi kullanılarak API'ın `/metrics` endpoint'inde Prometheus formatında anlık metrikler yayınlaması sağlandı.
- **Docker Servisleri:** `docker-compose.yml` içerisine `prometheus` ve `grafana` servisleri eklendi.
- **Hazır Dashboard:** Toplam istekleri, saniyedeki istek oranını (rate) ve hataları gösteren "To-Do List API Dashboard" tasarlandı.

### Kullanılan Teknolojiler
- Prometheus, Grafana, prometheus-fastapi-instrumentator

### Çalıştırılan Terminal Komutları
```bash
# Kütüphane kurulumu
pip install prometheus-fastapi-instrumentator

# Tüm servisleri (API, Postgres, Localstack, Prometheus, Grafana) yeniden ayağa kaldır
docker-compose up -d --build
```

## Adım 6: Performans Testleri (k6)

### Amaç
Geliştirilen API'ın eşzamanlı yoğun istekler (yük) altındaki performansını ölçmek, belirlenen hedeflerin (thresholds) altında yanıt verip vermediğini doğrulamak.

### Eklenen Dosyalar
- `perf/load-test.js` - k6 performans test senaryosu.
- `perf/report.md` - Performans test sonuçlarının p95 değerleriyle birlikte analiz edildiği rapor şablonu.

### Yazılan Özellikler
- **Gerçekçi Yük Senaryosu:** Sisteme aniden yüklenmek yerine; 10s içinde 20 kullanıcıya çıkma, 30s boyunca bu yükü koruma ve 10s içinde yükü sıfırlama şeklinde (Ramping VUs) aşamalı bir test yazıldı.
- **Hedefler (Thresholds):** Sistemin başarılı sayılabilmesi için isteklerin %95'inin (`p(95)`) 500ms altında yanıtlanması ve hata oranının %1'den az olması şartları test koduna eklendi.
- **Entegre Endpoint Kontrolleri:** Tek bir API değil; sırayla `/health`, `POST /api/tasks/` ve `GET /api/tasks/` endpointlerine eşzamanlı istekler atılarak uçtan uca senaryo tasarlandı.

### Kullanılan Teknolojiler
- k6 (Açık kaynak performans test aracı), Javascript

### Çalıştırılan Terminal Komutları
```powershell
# Eğer sisteminizde k6 yüklü ise testleri çalıştırmak için:
k6 run perf/load-test.js
```

## Adım 7: E2E (End-to-End) Testleri

### Amaç
Son kullanıcının bir web tarayıcısı üzerinden uygulamayı nasıl kullanacağını simüle ederek (kutuya yazı yazma, butona tıklama vb.) sistemin uçtan uca çalıştığını otomatize etmek.

### Eklenen Dosyalar
- `src/static/index.html` - Testin üzerinde koşacağı, API'ye bağlanan basit bir önyüz (frontend).
- `tests/e2e/test_ui.py` - Playwright kullanılarak yazılmış tarayıcı test senaryoları.

### Yazılan Özellikler
- **Basit Arayüz:** Vanilla HTML/JS kullanılarak görevleri listeleyen, yeni görev ekleyen, silebilen ve durumunu güncelleyen bir arayüz geliştirildi ve `/ui` path'ine eklendi.
- **Playwright Testleri:** `test_add_task_e2e`, `test_toggle_task_e2e` ve `test_delete_task_e2e` fonksiyonlarıyla sırasıyla bir kullanıcının arayüze girip metin girmesi, butona basması ve sayfanın DOM elemanlarının doğru güncellendiği doğrulandı.

### Kullanılan Teknolojiler
- Playwright, pytest, HTML/CSS/JS

### Çalıştırılan Terminal Komutları
```powershell
# Playwright bağımlılıklarını kur
pip install pytest-playwright
playwright install chromium

# E2E Testleri çalıştır (headless modda)
pytest tests/e2e/test_ui.py -v
```

## Adım 8: Kubernetes (Minikube)

### Amaç
Minikube üzerinde uygulamayı ayağa kaldırabilmek için gerekli olan Kubernetes manifest dosyalarını (Deployment, Service ve ConfigMap) oluşturmak.

### Eklenen Dosyalar
- `k8s/configmap.yaml` - Uygulamanın ortam değişkenlerini (environment variables) tutan konfigürasyon dosyası.
- `k8s/deployment.yaml` - Uygulamanın hangi imajdan oluşturulacağını, kaç kopya (replica) çalışacağını ve sağlık kontrollerini (Liveness/Readiness probes) tanımlayan dosya.
- `k8s/service.yaml` - Pod'lara dışarıdan (tarayıcıdan) erişebilmek için NodePort tipinde oluşturulan ağ servisi dosyası.

### Yazılan Özellikler
- **ConfigMap Entegrasyonu:** Uygulamanın `.env` ile aldığı ayarlar Kubernetes ortamında ConfigMap üzerinden (envFrom) verildi.
- **Sağlık Kontrolleri (Probes):** Daha önce yazdığımız `/health` endpoint'i kullanılarak konteynerin liveness ve readiness durumları Kubernetes'e bildirildi.
- **Yerel İmaj Kullanımı:** Minikube üzerinde yerel olarak build edilen imajı kullanmak için `imagePullPolicy: IfNotPresent` ayarı kullanıldı.
- **NodePort Servisi:** Minikube IP'si üzerinden doğrudan web arayüzüne ve API'a erişebilmek için 30000 portu dışa açıldı.

### Kullanılan Teknolojiler
- Kubernetes (Minikube), YAML

### Çalıştırılan Terminal Komutları
```powershell
# 1. Minikube'ü başlatın
minikube start

# 2. Minikube'ün Docker daemon'ına bağlanın (Docker imajını Minikube içine build etmek için)
minikube docker-env | Invoke-Expression

# 3. İmajı build edin
docker build -t todo-app:latest .

# 4. Kubernetes objelerini oluşturun
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 5. Pod'ların çalışmasını bekleyin
kubectl get pods

# 6. Uygulamaya tarayıcıdan erişmek için servisin URL'ini alın
minikube service todo-app-service
```

## Adım 9: CI/CD Pipeline (GitHub Actions)

### Amaç
Projedeki tüm kod kalite, test ve dağıtım (deployment) süreçlerini otomatikleştirerek sürekli entegrasyon ve sürekli teslimat (CI/CD) hattını kurmak.

### Eklenen Dosyalar
- `.github/workflows/ci.yml` - GitHub Actions tarafından çalıştırılacak olan pipeline yapılandırma dosyası.

### Yazılan Özellikler
Pipeline 5 temel aşamadan (step) oluşmaktadır:
1. **Linting (Kod Kalitesi):** `flake8` aracı kullanılarak Python kodunda yazım (syntax) hataları olup olmadığı kontrol edilir.
2. **Pytest (Testler):** Daha önce yazdığımız (Adım 2 ve Adım 7) birim, entegrasyon ve uçtan uca testlerin otomatik olarak çalıştırılması sağlanır.
3. **Docker Build:** Uygulamanın Docker imajının sorunsuz bir şekilde oluşturulup oluşturulmadığı (`docker build`) teyit edilir.
4. **Deploy (Dağıtım Simülasyonu):** Oluşturulan imaj, arka planda bir container olarak ayağa kaldırılarak uygulamanın çalışabilir olduğu doğrulanır.
5. **Smoke Test:** Ayakta olan uygulamanın `/health` endpoint'ine cURL ile istek atılıp `200 OK` dönüp dönmediği kontrol edilir.

### Kullanılan Teknolojiler
- GitHub Actions, YAML, Flake8, cURL, Bash

### Çalıştırılan Terminal Komutları
(Yerel ortamda çalıştırılmaz, GitHub'a kod push/pull request yapıldığında otomatik tetiklenir)

