# =============================================
# AWS S3 (LocalStack) İletişim Modülü
# =============================================
# Bu modül boto3 kütüphanesini kullanarak AWS S3 ile haberleşir.
# Adım 3 (Konteyner ve AWS) kapsamında LocalStack üzerinde çalışacak şekilde yapılandırılmıştır.

import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from src.utils.config import settings

# --- Boto3 S3 İstemcisi Başlatma ---
# AWS_ENDPOINT_URL doluysa (ki .env'de http://localhost:4566 olacak),
# tüm AWS istekleri LocalStack'e yönlendirilir.
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
    endpoint_url=settings.AWS_ENDPOINT_URL
)

def ensure_bucket_exists():
    """
    Uygulama başlatılırken veya ilk istek geldiğinde, 
    belirtilen S3 bucket'ının LocalStack üzerinde var olduğundan emin olur.
    Eğer yoksa bucket'ı oluşturur.
    """
    try:
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError as e:
        # 404 hatası dönerse bucket yok demektir
        if e.response["Error"]["Code"] == "404":
            print(f"[{settings.S3_BUCKET_NAME}] bucket'ı bulunamadı. Oluşturuluyor...")
            s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
        else:
            # Başka bir hata (örneğin auth) varsa fırlat
            raise

def upload_json_to_s3(data: Dict[str, Any] | list, file_name: str) -> Optional[str]:
    """
    Verilen Python verisini (dict/list) JSON formatına çevirir ve S3'e yükler.
    
    Args:
        data: JSON olarak kaydedilecek veri.
        file_name: S3'e kaydedilecek dosya adı (örnek: "tasks_export.json")
        
    Returns:
        Yüklenen dosyanın S3 adresi veya başarısız olursa None
    """
    ensure_bucket_exists()
    
    # Veriyi JSON string'e çevir (tarihler vs için str dönüşümü yapılır)
    json_data = json.dumps(data, ensure_ascii=False, default=str)
    
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_name,
            Body=json_data.encode("utf-8"),
            ContentType="application/json"
        )
        # S3 adresini oluştur
        # LocalStack S3 formatı: http://<endpoint>/<bucket>/<key>
        endpoint = settings.AWS_ENDPOINT_URL or f"https://s3.{settings.AWS_REGION}.amazonaws.com"
        file_url = f"{endpoint}/{settings.S3_BUCKET_NAME}/{file_name}"
        return file_url
    except ClientError as e:
        print(f"S3'e yükleme sırasında hata oluştu: {e}")
        return None
