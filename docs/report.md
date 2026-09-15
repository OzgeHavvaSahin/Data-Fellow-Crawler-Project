# AWS Üzerinde Otomatik Google News Verisi Toplama Projesi

## 1. Giriş

Bu projede Google News sitesindeki farklı haber kategorilerinden verileri otomatik olarak toplayan, bu verileri düzenleyen ve AWS servisleri üzerinde  saklayan bir sistem geliştirilmiştir. Bu projenin amacı web sracping, cloud computing, AWS servisleri kullanma, ilişkisel veritabanı ve veri depolama konularını gerçek bir senoryo üzerinden uygulamalı olarak deneyimlemektir. Sistem saatlik olarak çalışmakta ve Google News RSS kaynaklarından haber verilerini toplamaktadır. Toplanan veriler önce JSON formatında Amazon S3 üzerine kaydedilmekte, ardından S3 üzerinde yeni bir dosya oluştuğunda ikinci bir Lambda fonksiyonu tetiklenerek veriler Amazon RDS MySQL veritabanına aktarılmaktadır. Bu proje sonunda tamamen otomatik çalışan bir veri toplama ve depolama pipeline'ı oluşturulmuştur. 

## 2. Web Scraping Nedir?

Web scraping, internet sitelerinde yer alan verilerin yazılım aracılığıyla otomatik olarak toplanması işlemidir. Normalde kullanıcıların tarayıcı üzerinden görüntülediği içerikler belirli kurallar doğrultusunda programatik olarak okunur, ayrıştırılır ve ihtiyaç duyulan alanlar seçilerek yapılandırılmış veriye dönüştürülür.

## 3. Cloud Computing Nedir?

Cloud computing, sunucu, depolama, veritabanı ve ağ gibi bilişim kaynaklarının internet üzerinden servis olarak kullanılmasını sağlayan bir yaklaşımdır.

## 4.Local Crawler Nasıl Geliştirildi?

Cloud ortamına geçmeden önce ilk olarak haber verilerini local ortamda toplayabilen bir crawler geliştirildi. Buradaki amaç, veri kaynağından haberlerin doğru şekilde alınabildiğini ve ihtiyaç duyulan alanların ayrıştırılabildiğini doğrulamaktı.

İlk aşamada HTTP istekleri göndermek için `requests` kütüphanesi kullanıldı. Google News sayfasından alınan HTML içeriğinin ayrıştırılması için ise `BeautifulSoup` tercih edildi.

Örnek bir HTTP isteği şu şekilde gerçekleştirildi:

```python
import requests

response = requests.get(
    url,
    timeout=10,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

response.raise_for_status()
```
Burada requests.get() fonksiyonu ile hedef URL'ye bir HTTP isteği gönderilmektedir. timeout=10 parametresi, bağlantının çok uzun süre beklemesini önlemek için kullanılmıştır. User-Agent başlığı ise isteğin bir tarayıcıdan geliyormuş gibi görünmesini sağlar.

İstek başarılı olduktan sonra elde edilen HTML içeriği BeautifulSoup ile ayrıştırıldı:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")
```
