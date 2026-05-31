# 🎬 Canlı Demo Başlangıç ve Çekim Rehberi

Bu belge, projeyi sıfırdan kurup, hocanızın istediği 7 dakikalık canlı demo akışını **hiçbir şey bilmeyen birinin bile kopyala-yapıştır yaparak** çekebilmesi için hazırlanmıştır.

Lütfen adımları atlamadan sırasıyla uygulayın.

---

## 🛠️ BÖLÜM 1: ÇEKİM ÖNCESİ (HAZIRLIK)
**DİKKAT:** Bu kısmı videoyu kaydetmeye **başlamadan önce** yapın. Her şeyin çalıştığından emin olacağız.

### Adım 1: Doğru Klasöre Gitmek
Tüm komutları `my-project` klasöründe çalıştırmalısınız. PowerShell veya Terminali açıp şunu yazın:
```bash
cd C:\Users\onurb\Desktop\bulut_mimarileri_proje\my-project
```

### Adım 2: Gerekli Ortamları Başlatma
Videoda hazır olması için Minikube ve Monitoring (Grafana) araçlarını arka planda başlatalım. Aşağıdaki komutları sırayla kopyalayıp yapıştırın (her birinin bitmesini bekleyin):

```bash
# 1. Minikube'ü başlat
minikube start

# 2. Minikube'ün Docker'ı görmesini sağla
minikube docker-env | Invoke-Expression

# 3. İmajı Minikube için derle
docker build -t todo-app:latest .

# 4. Uygulamayı Kubernetes'e gönder
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 5. İzleme (Grafana/Prometheus) araçlarını başlat
docker-compose up -d prometheus grafana
```

---

## 🎬 BÖLÜM 2: VİDEO ÇEKİMİNE BAŞLA (7 Dakikalık Akış)

**Artık ekran kaydını başlatabilirsiniz. Fare imlecinizle anlatmak istediğiniz yerleri işaret etmeyi unutmayın.**

### Sahne 1: PR Aç ve CI Tetikle (1 dk)
**Amaç:** Koda ufak bir değişiklik ekleyip, "Yeni bir özellik geliştiriyorum" mesajı vererek GitHub Actions testlerini başlatmak.

1. Terminalde şu komutları sırasıyla girin (Yeni bir geliştirme dalı/branch oluşturuyoruz):
   ```bash
   git checkout -b yeni-ozellik
   ```
2. Kodu değiştirdiğimizi simüle etmek için `README.md` dosyasının en altına görünmez bir boşluk veya not ekleyelim:
   ```bash
   echo " " >> README.md
   git add README.md
   git commit -m "Ufak bir güncelleme yapildi"
   git push -u origin yeni-ozellik
   ```
3. **Tarayıcıya Geçin:** GitHub deponuza (BM_test_proje) gidin.
4. Ekranda beliren yeşil **"Compare & pull request"** butonuna basın. Çıkan sayfada yeşil **"Create pull request"** butonuna basın.
5. Saniyeler içinde altta beliren "Checks" (Sarı dönen ikonlar) kısmını farenizle gösterin. *("Kodumu gönderdim, CI Pipeline'ım testleri otomatik başlattı" mesajını veriyorsunuz.)*

### Sahne 2: PR Merge ve CD Tetikle (1 dk)
**Amaç:** Testler geçtikten sonra kodu ana projeye katmak (Merge) ve dağıtımı başlatmak.

1. Aynı GitHub PR sayfasında testlerin yeşil (`✓`) olmasını bekleyin. (Eğer uzun sürerse videoyu duraklatabilirsiniz).
2. Her şey yeşil olduğunda, **"Merge pull request"** butonuna, ardından **"Confirm merge"** butonuna basın.
3. Üstteki **"Actions"** sekmesine tıklayın.
4. "Ana dala" giden yeni işlemin başladığını gösterin ve içine girip "3. Adım - Docker Build" işleminin başarıyla imaj oluşturduğunu (CD adımı) işaret edin.
5. Son olarak terminale dönüp tekrar ana dala (main) geçin:
   ```bash
   git checkout main
   git pull origin main
   ```

### Sahne 3: Minikube'de Uygulamanın Deploy Olmasını Göster (1 dk)
**Amaç:** Uygulamanın Kubernetes ortamında canlı olarak çalıştığını kanıtlamak.

1. Terminale geçip şunu yazın:
   ```bash
   kubectl get pods
   ```
2. Çıkan listedeki `todo-app-...` satırında yazan **"Running"** yazısını fare ile gösterin.
3. Tarayıcıyı açması için şu komutu girin:
   ```bash
   minikube service todo-app-service
   ```
4. Tarayıcıda açılan ve JSON yanıtı veren (`"message": "To-Do List Manager'a hoş geldiniz!"`) sayfayı hocanıza gösterin.

### Sahne 4: Grafana'da Metrikleri Göster (1 dk)
**Amaç:** Uygulamanın profesyonel olarak izlendiğini göstermek.

1. Tarayıcıda yeni bir sekme açın ve şu adrese gidin:
   ```text
   http://localhost:3000
   ```
2. Giriş ekranı gelirse Username: `admin`, Password: `admin` yazıp giriş yapın.
3. Sol menüdeki 4 kareli ikona (Dashboards) tıklayın, açılan menüden **"FastAPI Metrics"** (veya hazır olan paneli) seçin.
4. Ekranda görünen Error Rate, Total Requests, Latency gibi grafikleri farenizle işaret edin.

### Sahne 5: k6 ile Load (Yük) Testi Koş (1 dk)
**Amaç:** Sisteme aynı anda onlarca kişinin girdiğini simüle edip çökmediğini kanıtlamak.

1. Terminale geri dönün. (Eğer bilgisayarınızda k6 yüklü değilse, videodan önce PowerShell'e `winget install k6` yazarak tek tuşla kurabilirsiniz).
2. Şu komutu yapıştırın ve çalıştırın:
   ```bash
   k6 run perf/load-test.js
   ```
3. Ekranda saniyeler içinde renkli yazılar akacak. 
4. İşlem bittiğinde ekrana gelen sonuç tablosunda, **`http_req_duration`** satırını bulun.
5. O satırdaki **`p(95)`** değerini (örneğin p(95)=12.4ms) farenizle işaretleyerek gösterin.

### Sahne 6: E2E Testini Canlı Çalıştır (1.5 dk)
**Amaç:** Arayüzün hayalet bir kullanıcı tarafından otomatik test edilmesini izletmek.

1. Terminale şu komutu yazın ve Enter'a basın:
   ```bash
   pytest tests/e2e/test_ui.py --headed
   ```
2. Bunu yazdığınız anda bilgisayarınızda **otomatik olarak** bir web tarayıcısı açılacak.
3. Siz hiçbir şeye dokunmadan; o tarayıcı kendi kendine açılacak, uygulamaya görev ekleyecek ve kapanacak.
4. Kapanır kapanmaz terminalde en son çıkan yeşil renkli **`PASSED`** (veya `1 passed`) yazısını fare ile gösterin.

**🎉 Tebrikler! Video çekiminiz tamamlandı. Kaydı durdurabilirsiniz.**
