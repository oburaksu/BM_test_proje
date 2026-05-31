# =============================================
# API Endpoint Birim (Unit) Testleri
# =============================================
# FastAPI'nin TestClient nesnesini kullanarak HTTP isteklerini simüle eder.
# Endpoint'lerin doğru HTTP statü kodları ve JSON formatları dönüp dönmediğini test eder.

def test_health_check(client):
    """Health check endpoint'i test edilir."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_all_tasks_empty(client):
    """Veritabanı boşken tasks endpoint'i test edilir."""
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_endpoint(client):
    """POST /api/tasks endpoint'i test edilir."""
    payload = {
        "title": "API Test Görevi",
        "description": "Postman veya TestClient ile deneme"
    }
    response = client.post("/api/tasks/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Test Görevi"
    assert data["is_completed"] is False
    assert "id" in data


def test_create_task_validation_error(client):
    """Eksik veya hatalı veri gönderildiğinde 422 alınması test edilir."""
    # title zorunluydu, göndermiyoruz
    payload = {"description": "Başlıksız görev"}
    response = client.post("/api/tasks/", json=payload)
    
    assert response.status_code == 422  # Unprocessable Entity (Pydantic ValidationError)


def test_get_task_endpoint(client):
    """Mevcut bir görevi API'den okuma testi."""
    # Önce bir görev oluştur
    create_resp = client.post("/api/tasks/", json={"title": "Okunacak Görev"})
    task_id = create_resp.json()["id"]
    
    # Şimdi GET isteği at
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Okunacak Görev"


def test_update_task_endpoint(client):
    """Görev güncelleme API testi."""
    create_resp = client.post("/api/tasks/", json={"title": "Eski Başlık"})
    task_id = create_resp.json()["id"]
    
    update_payload = {"title": "Yeni Başlık", "is_completed": True}
    response = client.put(f"/api/tasks/{task_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Yeni Başlık"
    assert data["is_completed"] is True


def test_delete_task_endpoint(client):
    """Görev silme API testi."""
    create_resp = client.post("/api/tasks/", json={"title": "Silinecek Görev"})
    task_id = create_resp.json()["id"]
    
    # Silme isteği
    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 200
    
    # Tekrar bulmaya çalış
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404
