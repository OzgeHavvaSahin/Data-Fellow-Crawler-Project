# AWS Üzerinde Otomatik Google News Verisi Toplama Projesi

## Giriş

Bu projede Google News sitesindeki farklı haber kategorilerinden verileri otomatik olarak toplayan, bu verileri düzenleyen ve AWS servisleri üzerinde  saklayan bir sistem geliştirilmiştir. Bu projenin amacı cloud computing, AWS servislerinin kullanımı, ilişkisel veritabanı ve veri depolama konularını gerçek bir senaryo üzerinden uygulamalı olarak deneyimlemektir. Sistem saatlik olarak çalışmakta ve Google News RSS kaynaklarından haber verilerini toplamaktadır. Toplanan veriler önce JSON formatında Amazon S3 üzerine kaydedilmekte, ardından S3 üzerinde yeni bir dosya oluştuğunda ikinci bir Lambda fonksiyonu tetiklenerek veriler Amazon RDS MySQL veritabanına aktarılmaktadır. Bu proje sonunda tamamen otomatik çalışan bir veri toplama ve depolama pipeline'ı oluşturulmuştur. 

## Cloud Computing Nedir?

Cloud computing, sunucu, depolama, veritabanı ve ağ gibi bilişim kaynaklarının internet üzerinden servis olarak kullanılmasını sağlayan bir yaklaşımdır.

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

