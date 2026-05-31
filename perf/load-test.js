import http from 'k6/http';
import { check, sleep } from 'k6';

// Test Konfigürasyonu
export const options = {
  // Yük testi aşamaları (Ramping VUs)
  stages: [
    { duration: '10s', target: 20 },  // 10 saniye içinde 20 kullanıcıya çık
    { duration: '30s', target: 20 },  // 30 saniye boyunca 20 kullanıcı ile devam et (Yük durumu)
    { duration: '10s', target: 0 },   // 10 saniye içinde 0 kullanıcıya in (Soğuma)
  ],
  // Performans hedefleri (Thresholds)
  thresholds: {
    // Tüm isteklerin %95'i 500ms'nin altında olmalı
    http_req_duration: ['p(95)<500'],
    // Hata oranı %1'in altında olmalı
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // 1. Health Check Testi
  let resHealth = http.get(`${BASE_URL}/health`);
  check(resHealth, {
    'health status is 200': (r) => r.status === 200,
  });

  // 2. Yeni Görev Oluşturma Testi
  const payload = JSON.stringify({
    title: 'k6 Yük Testi Görevi',
    description: 'Bu görev k6 performans testi tarafından otomatik oluşturulmuştur.'
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let resCreate = http.post(`${BASE_URL}/api/tasks/`, payload, params);
  check(resCreate, {
    'create task is 201': (r) => r.status === 201,
  });

  // 3. Görevleri Listeleme Testi
  let resGet = http.get(`${BASE_URL}/api/tasks/`);
  check(resGet, {
    'get tasks is 200': (r) => r.status === 200,
  });

  // Her iterasyon arası 1 saniye bekle (Gerçekçi kullanıcı simülasyonu)
  sleep(1);
}
