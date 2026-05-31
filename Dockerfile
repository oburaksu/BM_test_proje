# =============================================
# Multi-Stage Dockerfile
# =============================================
# Bu Dockerfile, uygulamayı konteynerize etmek için çok aşamalı (multi-stage) build kullanır.
# Multi-stage yapısı, son imaj boyutunu küçültmek ve güvenliği artırmak için idealdir.

# ---- Stage 1: Builder (Derleyici) Aşama ----
# Bağımlılıkları derlemek ve indirmek için kullanılır.
FROM python:3.12-slim AS builder

WORKDIR /app

# Gerekli sistem kütüphanelerini kur (psycopg2 gibi paketlerin derlenmesi için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Sanal ortam (virtual environment) oluştur
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
# --no-cache-dir ile gereksiz önbellek dosyalarını sil
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ---- Stage 2: Runner (Çalıştırıcı) Aşama ----
# Yalnızca uygulamanın çalışması için gerekli dosyaları içerir.
FROM python:3.12-slim AS runner

# Ortam değişkenlerini ayarla
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Sistem kütüphanelerinden sadece çalışma zamanı (runtime) için gerekli olanları kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Builder aşamasından hazır sanal ortamı kopyala
COPY --from=builder /opt/venv /opt/venv

# Uygulama kodlarını kopyala
COPY src/ ./src/
# SQLite kullanılacaksa veritabanının yazılabilmesi için yetki
RUN chmod -R 777 /app

# Konteynerın dışa açacağı port
EXPOSE 8000

# Uygulamayı çalıştır
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
