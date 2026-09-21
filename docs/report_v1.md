# CloudFormation ile Test ve Prod Ortamlarının Otomatik Oluşturulması

## Giriş

DFCP V0 kapsamında Google News RSS kaynaklarından haber verilerini toplayan, bu verileri Amazon S3 üzerinde saklayan ve Amazon RDS MySQL veritabanına aktaran uçtan uca bir AWS mimarisi geliştirilmişti.

DFCP V1 aşamasında ise mevcut çalışan sistemin AWS Console üzerinden manuel olarak oluşturulması yerine, altyapının kod ile tanımlanması hedeflenmiştir. Bu amaçla AWS CloudFormation ve AWS SAM kullanılarak projeye ait kaynakların tek bir template üzerinden oluşturulabileceği bir yapı geliştirilmiştir.

Bu fazın temel amacı, test ve prod ortamlarının aynı `sam_template.yaml` dosyası kullanılarak ayrı CloudFormation stack'leri şeklinde oluşturulmasıdır. Template içerisinde ortam bilgileri parametre olarak alınmış ve kaynak isimleri test ve prod ortamlarına göre dinamik şekilde üretilmiştir.

Projede ayrıca Lambda fonksiyonlarının deployment paketleri ve Lambda Layer dosyaları ZIP formatında Amazon S3 üzerinde tutulmuş ve CloudFormation deployment sırasında bu paketleri kullanmıştır.

Bu yaklaşım sayesinde AWS altyapısının manuel olarak tekrar tekrar oluşturulması yerine, aynı mimarinin kod üzerinden tekrar üretilebilir hale getirilmesi amaçlanmıştır.
