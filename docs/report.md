# AWS Üzerinde Otomatik Google News Verisi Toplama Projesi

## Giriş

Bu projede Google News sitesindeki farklı haber kategorilerinden verileri otomatik olarak toplayan, bu verileri düzenleyen ve AWS servisleri üzerinde  saklayan bir sistem geliştirilmiştir. Bu projenin amacı cloud computing, AWS servislerinin kullanımı, ilişkisel veritabanı ve veri depolama konularını gerçek bir senaryo üzerinden uygulamalı olarak deneyimlemektir. Sistem saatlik olarak çalışmakta ve Google News RSS kaynaklarından haber verilerini toplamaktadır. Toplanan veriler önce JSON formatında Amazon S3 üzerine kaydedilmekte, ardından S3 üzerinde yeni bir dosya oluştuğunda ikinci bir Lambda fonksiyonu tetiklenerek veriler Amazon RDS MySQL veritabanına aktarılmaktadır. Bu proje sonunda tamamen otomatik çalışan bir veri toplama ve depolama pipeline'ı oluşturulmuştur. 

## Veri Toplama Yaklaşımının Belirlenmesi

Projenin ilk aşamasında Google News üzerindeki haber verilerinin klasik HTML tabanlı web scraping yöntemiyle toplanması denendi. Bu yöntemde `requests` ile web sayfasına istek gönderiliyor ve `BeautifulSoup` kullanılarak HTML içerisindeki haber bağlantıları ve başlıkları ayrıştırılıyordu. Local ortamda bu yöntem çalışmasına rağmen, uygulama AWS Lambda üzerinde çalıştırıldığında Google News haber sayfası yerine consent sayfası döndürmeye başladı. Farklı `User-Agent`, dil ve session ayarları denenmesine rağmen bu davranış çözülemedi. Bu nedenle projede HTML scraping yaklaşımı bırakılarak Google News RSS kaynaklarının kullanılmasına karar verildi. RSS yapısı haberleri XML formatında sunduğu için başlık, kaynak, yayın tarihi ve bağlantı gibi bilgilere daha düzenli ve güvenilir şekilde erişmek mümkün oldu. Bundan sonraki veri toplama süreci RSS feed'lerinin alınması ve XML verisinin parse edilmesi üzerine kuruldu.

## RSS Üzerinden Haber Verilerinin Toplanması

HTML tabanlı scraping yaklaşımında yaşanan problem sonrasında veri kaynağı olarak Google News RSS feed'leri kullanılmaya başlandı. RSS, web sitelerinin içeriklerini yapılandırılmış XML formatında sunmasını sağlayan bir yöntemdir. Google News RSS yapısı sayesinde haber başlığı, haber kaynağı, yayın tarihi ve haber bağlantısı gibi bilgilere HTML sayfasını doğrudan parse etmeden erişmek mümkün oldu.

Projede RSS verilerini almak için `requests`, XML içeriğini parse etmek için ise Python'ın standart kütüphanelerinden biri olan `xml.etree.ElementTree` kullanıldı.

Öncelikle ilgili kategoriye ait RSS adresine HTTP isteği gönderildi:

```python
import requests
import xml.etree.ElementTree as ET

def fetch_news(category: str):
    url = URLS[category]

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
    )

    response.raise_for_status()

    return ET.fromstring(response.content)
```
Burada `URLS[category]` ile işlenecek kategoriye ait RSS adresi alınmaktadır.
`requests.get()` fonksiyonu ile Google News RSS kaynağına HTTP isteği gönderilir. 

İstek başarılı olduğunda dönen veri XML formatındadır. Bu veri:,

```python
ET.fromstring(response.content)
```
kullanılarak parse edilir ve Python içerisinde işlenebilir bir XML ağacına dönüştürülür.

### RSS İçerisinden Haberlerin Ayrıştırılması

Google News RSS yapısında her haber `<item>` etiketi altında yer almaktadır. Bu nedenle RSS içerisindeki haberler bulunarak gerekli alanlar ayrıştırıldı.

Her haber için şu bilgiler oluşturuldu:

- `category`: Haber kategorisi
- `rank`: Haberin mevcut sırası
- `title`: Haber başlığı
- `source`: Haber kaynağı
- `published_at`: Yayın tarihi
- `url`: Haber bağlantısı
- `description`: Haber açıklaması

Google News RSS içerisindeki `description` alanı doğrudan kısa bir haber özeti sunmadığı için bu alan projede şimdilik `None` olarak bırakıldı.

Haberlerin sıralamasını tutmak için `enumerate(items, start=1)` kullanıldı. Böylece RSS içerisindeki ilk haber `rank = 1`, ikinci haber `rank = 2` şeklinde numaralandırıldı.

Local testler sonucunda farklı kategorilerdeki haberlerin başarıyla çekildiği ve verilerin beklenen yapıda oluşturulduğu doğrulandı.Bu aşamadan sonra local ortamda çalışan crawler'ın AWS üzerinde otomatik olarak çalıştırılması ve verilerin cloud ortamında saklanması aşamasına geçildi.

## Cloud Computing Nedir?

Cloud computing, sunucu, depolama, veritabanı ve ağ gibi bilişim kaynaklarının internet üzerinden servis olarak kullanılmasını sağlayan bir yaklaşımdır.

## AWS Nedir ve Neden Kullanıldı?

AWS (Amazon Web Services), uygulamaların sunucu, depolama, veritabanı, ağ ve benzeri kaynaklara internet üzerinden erişmesini sağlayan bir cloud platformudur.

Bu projede AWS; crawler'ın otomatik çalıştırılması, verilerin S3 üzerinde saklanması, RDS MySQL veritabanına aktarılması ve servisler arasındaki bağlantının kurulması için kullanılmıştır.

## Projede Kullanılan AWS Servisleri

Bu projede aşağıdaki AWS servisleri kullanılmıştır:

### AWS Lambda
Sunucu yönetmeden kod çalıştırmayı sağlayan serverless bir servistir. Projede crawler ve RDS writer olmak üzere iki farklı Lambda function kullanılmıştır.

### Amazon S3
Dosya tabanlı veri depolama servisidir. Crawler tarafından oluşturulan JSON dosyaları burada saklanmıştır.

### Amazon RDS for MySQL
İlişkisel veritabanı servisidir. Haber verileri `news_articles` tablosunda tutulmuştur.

### Amazon EventBridge Scheduler
Crawler Lambda'nın saatlik olarak otomatik çalıştırılması için kullanılmıştır.

### Amazon VPC
RDS Writer Lambda ile RDS arasında private network bağlantısı sağlamak için kullanılmıştır.

### S3 Gateway VPC Endpoint
VPC içerisindeki RDS Writer Lambda'nın NAT Gateway kullanmadan S3'e erişebilmesini sağlamıştır.

### IAM
AWS servisleri arasındaki erişim yetkilerini yönetmek için kullanılmıştır.

### CloudWatch
Lambda loglarını ve hata mesajlarını takip etmek için kullanılmıştır.

## AWS Mimarisinin Oluşturulması

Projede veri toplama ve veritabanına aktarma işlemleri iki ayrı Lambda function üzerinden gerçekleştirilmiştir.

![AWS Architecture](./diagrams/Aws.png)

- `EventBridge Scheduler`, `Crawler Lambda` fonksiyonunu saatlik olarak tetikler. 
- Crawler Lambda, Google News RSS kaynaklarından haberleri toplar ve JSON formatında Amazon S3'e kaydeder. 
- Amazon S3 üzerinde yeni bir JSON dosyası oluştuğunda `S3 ObjectCreated Event`, `RDS Writer Lambda` fonksiyonunu tetikler.
- Bu Lambda VPC içerisinde çalışır ve S3 üzerindeki veriyi okuyarak Amazon RDS MySQL veritabanına aktarır.
- VPC içerisindeki Lambda'nın Amazon S3'e NAT Gateway olmadan erişebilmesi için `S3 Gateway VPC Endpoint` kullanılmıştır.

## Crawler Lambda ve Amazon S3 Entegrasyonu

İlk olarak crawler kodunu çalıştıracak bir AWS Lambda function oluşturuldu.

Bu Lambda'nın temel görevi:

- Google News RSS kaynaklarına bağlanmak
- Haber verilerini almak
- Verileri parse etmek
- Haberleri JSON formatında hazırlamak
- Amazon S3 üzerine kaydetmek

Local ortamda geliştirilen crawler kodu Lambda üzerinde çalışacak şekilde düzenlendi.

Ana Lambda handler fonksiyonu şu yapıda oluşturuldu:

```python
from src.scraper import fetch_news, extract_links
from src.storage import save_to_s3
from src.config import URLS

def lambda_handler(event, context):
    results = []

    for category in URLS:
        if category == "base":
            continue

        root = fetch_news(category)
        news_items = extract_links(root, category)

        s3_key = save_to_s3(
            news_items,
            category
        )

        results.append({
            "category": category,
            "count": len(news_items),
            "s3_key": s3_key
        })

    return {
        "statusCode": 200,
        "results": results
    }
```
Bu fonksiyon içerisinde kategori listesi dolaşılır ve her kategori için sırasıyla RSS verisi çekilir, haberler ayrıştırılır ve elde edilen veriler Amazon S3'e kaydedilir.

Crawler kodunda requests gibi Python'ın standart kütüphanesinde bulunmayan paketler kullanıldığı için bu dependency'lerin Lambda ortamında ayrıca bulunması gerekti. Bu nedenle gerekli Python paketleri bir `Lambda Layer` içerisinde hazırlandı.
Crawler Lambda için kullanılan temel dış dependency  `requests ` paketidir.
Python'ın standart kütüphanesinde bulunan xml.etree.ElementTree, json ve benzeri modüllerin ayrıca eklenmesine gerek kalmadı.

Crawler Lambda'nın manuel olarak çalıştırılmasına gerek kalmaması için `Amazon EventBridge Scheduler` kullanıldı. Scheduler üzerinde `rate(1 hour)` kuralı tanımlanarak crawler Lambda'nın her saat otomatik olarak tetiklenmesi sağlandı. Bu yapı sayesinde sistem belirli bir kullanıcı müdahalesi olmadan periyodik olarak çalışmakta ve her saat güncel Google News verilerini toplamaktadır.

Lambda'nın Function Overview ekranı


### Amazon S3 Üzerine Veri Kaydetme
