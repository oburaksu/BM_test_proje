# Performans Testi Raporu (k6)

## Test Ortamı
- **Tarih:** YYYY-MM-DD
- **Araç:** k6 v0.x.x
- **Hedef URL:** `http://localhost:8000`
- **Veritabanı:** SQLite (Local) / PostgreSQL (Docker)

## Test Senaryosu
- **Aşama 1 (Ramp-up):** 10 saniye içinde 20 sanal kullanıcıya (Virtual Users - VUs) çıkıldı.
- **Aşama 2 (Yük):** 30 saniye boyunca 20 aktif kullanıcı ile sürekli istek atıldı.
- **Aşama 3 (Ramp-down):** 10 saniye içinde kullanıcı sayısı sıfıra düşürüldü.
- **İstek Başına Bekleme Süresi:** Her tam döngü arasında 1 saniye (Kullanıcı okuma simülasyonu).

## Hedefler (Thresholds)
- HTTP isteklerinin en az %95'i **500ms**'nin altında yanıtlanmalı. (`p(95) < 500ms`)
- Hata oranı (Failed requests) **%1**'in altında olmalı. (`rate < 0.01`)

## Test Sonuçları (Örnek Çıktı)

```text
  scenarios: (100.00%) 1 scenario, 20 max VUs, 1m20s max duration (incl. graceful stop)
           * default: Up to 20 looping VUs for 50s over 3 stages (gracefulRampDown: 30s)

    ✓ health status is 200
    ✓ create task is 201
    ✓ get tasks is 200

    checks.........................: 100.00% ✓ 1500      ✗ 0
    data_received..................: 1.2 MB  24 kB/s
    data_sent......................: 350 kB  7.0 kB/s
    http_req_blocked...............: avg=200µs  min=0s      med=0s      max=50ms    p(90)=0s      p(95)=1ms
    http_req_connecting............: avg=100µs  min=0s      med=0s      max=20ms    p(90)=0s      p(95)=0s
  ✓ http_req_duration..............: avg=15ms   min=2ms     med=10ms    max=150ms   p(90)=25ms    p(95)=35ms
      { expected_response:true }...: avg=15ms   min=2ms     med=10ms    max=150ms   p(90)=25ms    p(95)=35ms
  ✓ http_req_failed................: 0.00%   ✓ 0         ✗ 500
    http_req_receiving.............: avg=500µs  min=0s      med=0s      max=10ms    p(90)=1ms     p(95)=2ms
    http_req_sending...............: avg=100µs  min=0s      med=0s      max=5ms     p(90)=0s      p(95)=1ms
    http_req_tls_handshaking.......: avg=0s     min=0s      med=0s      max=0s      p(90)=0s      p(95)=0s
    http_req_waiting...............: avg=14ms   min=1ms     med=9ms     max=145ms   p(90)=23ms    p(95)=32ms
    http_reqs......................: 500     10/s
    iteration_duration.............: avg=1.01s  min=1s      med=1.01s   max=1.15s   p(90)=1.02s   p(95)=1.03s
    iterations.....................: 166     3.32/s
    vus............................: 20      min=0       max=20
    vus_max........................: 20      min=20      max=20
```

## Değerlendirme
- ✅ **Yanıt Süreleri (p95):** Hedef olan 500ms'nin çok altında kalınmıştır (Örn: 35ms). Performans son derece yeterlidir.
- ✅ **Hata Oranı:** Hiçbir istekte hata (5xx, 4xx) alınmamıştır (Hata oranı %0.00).
- ✅ **Sistem Sağlamlığı:** Uygulama ve veritabanı bağlantısı, test sırasında oluşan eşzamanlı yük altında darboğaza (bottleneck) girmemiştir.
