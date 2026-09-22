# CloudFormation ile Test ve Prod Ortamlarının Otomatik Oluşturulması

## Giriş

DFCP V0 kapsamında Google News RSS kaynaklarından haber verilerini toplayan, bu verileri Amazon S3 üzerinde saklayan ve Amazon RDS MySQL veritabanına aktaran uçtan uca bir AWS mimarisi geliştirilmişti.

DFCP V1 aşamasında ise mevcut çalışan sistemin AWS Console üzerinden manuel olarak oluşturulması yerine, altyapının kod ile tanımlanması hedeflenmiştir. Bu amaçla AWS CloudFormation ve AWS SAM kullanılarak projeye ait kaynakların tek bir template üzerinden oluşturulabileceği bir yapı geliştirilmiştir.

Bu fazın temel amacı, test ve prod ortamlarının aynı `sam_template.yaml` dosyası kullanılarak ayrı CloudFormation stack'leri şeklinde oluşturulmasıdır. Template içerisinde ortam bilgileri parametre olarak alınmış ve kaynak isimleri test ve prod ortamlarına göre dinamik şekilde üretilmiştir.

Projede ayrıca Lambda fonksiyonlarının deployment paketleri ve Lambda Layer dosyaları ZIP formatında Amazon S3 üzerinde tutulmuş ve CloudFormation deployment sırasında bu paketleri kullanmıştır.

Bu yaklaşım sayesinde AWS altyapısının manuel olarak tekrar tekrar oluşturulması yerine, aynı mimarinin kod üzerinden tekrar üretilebilir hale getirilmesi amaçlanmıştır.

## Infrastructure as Code ve CloudFormation Yaklaşımı

Infrastructure as Code (IaC), sunucu, ağ, depolama ve benzeri altyapı kaynaklarının manuel olarak oluşturulması yerine kod ile tanımlanmasını sağlayan bir yaklaşımdır.

Bu projede IaC yaklaşımını uygulamak için `AWS CloudFormation` ve `AWS SAM` kullanılmıştır. Böylece önceki fazda AWS Console üzerinden manuel olarak oluşturulan kaynaklar, bu fazda bir template dosyası içerisinde tanımlanmıştır.

CloudFormation içerisinde bir **stack**, projeye ait AWS kaynaklarının birlikte oluşturulduğu ve yönetildiği yapıyı ifade eder. Örneğin bu projede S3 bucket, Lambda fonksiyonları, Lambda Layer'lar, EventBridge kuralları, VPC, subnet, security group ve VPC Endpoint gibi kaynaklar aynı stack içerisinde yönetilmektedir.

Projede ana altyapı dosyası olarak:

`data_fellow/architecture/sam_template.yaml`

kullanılmıştır. Test ve prod ortamları için farklı template dosyaları oluşturmak yerine tek bir parametrik template kullanılmıştır. `Environment` parametresi sayesinde aynı template hem test hem de prod ortamı için kullanılabilmektedir.

Bu yapı sayesinde iki ortamın kaynak isimleri birbirinden ayrılmış ve aynı altyapının farklı ortamlar için tekrar oluşturulabilmesi sağlanmıştır.

Ayrıca Lambda fonksiyonlarının kaynak kodları ve gerekli Lambda Layer dosyaları ZIP formatında Amazon S3 üzerinde tutulmuştur. CloudFormation deployment sırasında bu paketleri S3 üzerinden alarak ilgili Lambda ve Layer kaynaklarını oluşturmuştur.

Bu yaklaşım sayesinde AWS altyapısı tekrar üretilebilir, versiyonlanabilir ve daha az manuel işlem gerektiren bir yapıya dönüştürülmüştür.

## Initial Template ve Deployment Bucket

Ana CloudFormation stack'ini oluşturmadan önce Lambda deployment paketlerinin ve Lambda Layer dosyalarının tutulacağı bir S3 bucket'a ihtiyaç duyuldu.

Bu nedenle ilk aşamada `initial_sam_template.yaml` dosyası oluşturuldu. Bu template yalnızca deployment sırasında gerekli olan başlangıç kaynağını, yani S3 bucket'ı oluşturmak için kullanıldı.

initial_sam_template.yaml içerisinde ortam bilgisi parametrik olarak tanımlandı:

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues:
      - test
      - prod
```

Deployment bucket adı ise ortam, AWS hesap numarası ve region bilgisine göre dinamik olarak oluşturuldu:

```yaml
Resources:
  DeploymentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub: "dfcp-v1-${Environment}-deployment-${AWS::AccountId}-${AWS::Region}"
```

Bu yapı sayesinde test ve prod ortamları için ayrı deployment bucket'ları oluşturulabildi.

```text
dfcp-v1-test-deployment-...
dfcp-v1-prod-deployment-...
```

Lambda fonksiyonlarının ZIP paketleri ve Lambda Layer dosyaları bu bucket'lar içerisinde ayrı klasörlerde tutuldu:

```text
deployment-bucket/
├── lambda/
│   ├── lambda-deploy.zip
│   └── rds-writer-deploy.zip
└── layer/
    ├── rss-layer.zip
    └── mysql-layer.zip
```

Ana sam_template.yaml dosyası daha sonra bu S3 bucket içerisinde bulunan deployment paketlerini kullanarak Lambda ve Lambda Layer kaynaklarını oluşturdu. Bu yaklaşım sayesinde deployment paketleri ile altyapı tanımları birbirinden ayrılmış ve ana stack oluşturulmadan önce ihtiyaç duyulan kaynakların hazır hale gelmesi sağlanmıştır.

## Ana SAM Template ile AWS Kaynaklarının Oluşturulması

Initial stack ile deployment bucket oluşturulduktan ve gerekli ZIP paketleri S3 üzerine yüklendikten sonra, projenin asıl altyapısı `sam_template.yaml` dosyası içerisinde tanımlandı.

Bu template içerisinde test ve prod ortamlarında kullanılacak AWS kaynakları parametrik olarak oluşturuldu.

Başlıca kaynaklar:

- Amazon S3
- AWS Lambda
- Lambda Layer
- Amazon EventBridge
- Amazon VPC
- Private Subnet
- Route Table
- Security Group
- S3 Gateway VPC Endpoint
- Lambda Permission
- Amazon RDS MySQL

Template içerisinde `AWS SAM` kullanıldığı için özellikle Lambda ve Layer tanımları daha sade bir yapıda oluşturuldu.

Örneğin crawler Lambda şu şekilde tanımlandı:

```yaml
CrawlerFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName:
      Fn::Sub: "dfcp-v1-${Environment}-crawler"
    Runtime: python3.12
    Handler: src.lambda_function.lambda_handler
    Timeout: 30

    CodeUri:
      Bucket:
        Ref: DeploymentBucketName
      Key: lambda/lambda-deploy.zip

    Layers:
      - Ref: RssLayer
```
Burada Lambda kaynak kodu doğrudan local dosyadan değil, daha önce oluşturulan deployment bucket içerisindeki ZIP paketinden alınmaktadır.

Crawler'ın kullandığı RSS bağımlılıkları ise ayrı bir Lambda Layer olarak tanımlandı:

```yaml
RssLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    LayerName:
      Fn::Sub: "dfcp-v1-${Environment}-rss-layer"
    ContentUri:
      Bucket:
        Ref: DeploymentBucketName
      Key: layer/rss-layer.zip
    CompatibleRuntimes:
      - python3.12
```

Aynı yaklaşım RDS Writer Lambda ve MySQL bağlantısı için kullanılan mysql-layer.zip paketi için de uygulandı.

Kaynak isimlerinde Fn::Sub kullanılarak ortam bilgisi dinamik olarak eklendi:

```text
dfcp-v1-test-crawler
dfcp-v1-prod-crawler

dfcp-v1-test-rds-writer
dfcp-v1-prod-rds-writer
```
Böylece aynı template kullanılarak test ve prod ortamlarında birbirinden ayrı AWS kaynaklarının oluşturulması sağlandı.

## EventBridge ile Saatlik Otomatik Çalıştırma

Crawler Lambda fonksiyonunun manuel olarak çalıştırılmasına gerek kalmaması için `Amazon EventBridge` kullanıldı.

Crawler Lambda içerisinde bir schedule tanımı yapılarak fonksiyonun her saat otomatik olarak tetiklenmesi sağlandı.

```yaml
Events:
  HourlySchedule:
    Type: Schedule
    Properties:
      Schedule: rate(1 hour)
      Description: Run crawler every hour
      Enabled: true
```
Bu yapı sayesinde crawler fonksiyonu kullanıcı müdahalesi olmadan belirli aralıklarla çalışmakta ve Google News RSS kaynaklarından güncel haber verilerini toplamaktadır. Toplanan veriler kategori bazında JSON formatına dönüştürülerek Amazon S3 üzerinde saklanmaktadır.

 ## S3 Üzerinde Haber Verilerinin Saklanması

Crawler Lambda tarafından toplanan haber verileri, CloudFormation tarafından oluşturulan ayrı bir S3 bucket içerisinde saklandı .Crawler Lambda'nın bu bucket üzerine veri yazabilmesi için gerekli S3 izinleri SAM policy tanımları üzerinden verildi.

```yaml
Policies:
  - S3WritePolicy:
      BucketName:
        Ref: NewsDataBucket
```

Ayrıca bucket adı Lambda'ya environment variable olarak aktarıldı:

```yaml
Environment:
  Variables:
    S3_BUCKET:
      Ref: NewsDataBucket
```

Bu sayede Python kodu test veya prod ortamına göre farklı bir bucket adı bilmek zorunda kalmadan, CloudFormation tarafından sağlanan değeri kullanabilmektedir.

## RDS Writer Lamba ve S3 Event Entegrasyonu

Amazon S3 üzerine yeni bir haber dosyası yazıldığında, ikinci Lambda fonksiyonu olan RDS Writer'ın otomatik olarak tetiklenmesi sağlandı. Bu amaçla S3 üzerinde `ObjectCreated` eventi tanımlandı.

RDS Writer Lambda'nın görevi:

 - S3 event içerisinden bucket ve object key bilgilerini almak
 - JSON dosyasını Amazon S3 üzerinden okumak
 - Haber kayıtlarını ayrıştırmak
 - MySQL veritabanına kaydetmek

RDS Writer'ın private VPC içerisinde çalışması nedeniyle Amazon S3 erişimi için S3 Gateway VPC Endpoint kullanıldı.

Bu yapı sayesinde NAT Gateway kullanılmadan private subnet içerisindeki Lambda fonksiyonunun Amazon S3'e erişmesi sağlandı.

## VPC ve Network Yapısının CloudFormation ile Oluşturulması

RDS Writer Lambda ve MySQL veritabanı arasındaki bağlantının private network üzerinden sağlanabilmesi için gerekli VPC altyapısı da `sam_template.yaml` içerisinde tanımlandı.

Oluşturulan temel network kaynakları:

 - VPC
 - İki private subnet
 - Private route table
 - RDS Writer Security Group
 - RDS Security Group
 - S3 Gateway VPC Endpoint

İki farklı Availability Zone içerisinde private subnet oluşturularak RDS için gerekli network yapısı hazırlandı.

```text
VPC
├── Private Subnet 1
├── Private Subnet 2
├── RDS Writer Lambda
└── RDS MySQL
```

RDS Security Group üzerinde yalnızca RDS Writer Lambda'nın security group'undan gelen `TCP 3306` bağlantılarına izin verildi. Bu sayede MySQL portu internete açık hale getirilmeden Lambda ile veritabanı arasındaki iletişim sağlandı.

## Bağımlılık Yönetimi ve Circular Dependency Problemi

CloudFormation ile altyapı oluşturulurken bazı AWS kaynaklarının birbirine bağımlı olması nedeniyle kaynakların oluşturulma sırası önem kazanmaktadır. Bu projede özellikle Amazon S3 ile RDS Writer Lambda arasındaki event bağlantısı oluşturulurken bir `Circular Dependency` problemi ile karşılaşıldı. İlk yaklaşımda S3 event'i doğrudan RDS Writer Lambda'nın SAM tanımı içerisinde oluşturulmuştu. Ancak bu durumda aşağıdaki kaynaklar birbirine karşılıklı olarak bağımlı hale geldi:

```text
NewsDataBucket
      ↓
RDS Writer Lambda
      ↓
Lambda Permission
      ↓
NewsDataBucket
```

S3 bucket'ın Lambda fonksiyonunu tetikleyebilmesi için Lambda permission kaynağına ihtiyaç vardı. Buna karşılık Lambda permission içerisinde de ilgili S3 bucket ARN bilgisi kullanılıyordu. Bu karşılıklı bağımlılık CloudFormation tarafından: `Circular dependency between resources` hatası ile sonuçlandı.

Problemi çözmek için S3 trigger tanımı RDS Writer Lambda'nın Events bölümünden çıkarıldı ve Lambda'nın S3 tarafından çağrılmasına izin veren kaynak ayrıca tanımlandı.

```yaml
RdsWriterS3InvokePermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName:
      Fn::GetAtt:
        - RdsWriterFunction
        - Arn
    Action: lambda:InvokeFunction
    Principal: s3.amazonaws.com
    SourceAccount:
      Ref: AWS::AccountId
    SourceArn:
      Fn::Sub: "arn:${AWS::Partition}:s3:::dfcp-v1-${Environment}-news-${AWS::AccountId}-${AWS::Region}"
```
Daha sonra S3 bucket üzerinde Lambda notification ayrıca tanımlandı:

```yaml
NewsDataBucket:
  Type: AWS::S3::Bucket
  DependsOn:
    - RdsWriterS3InvokePermission
  Properties:
    BucketName:
      Fn::Sub: "dfcp-v1-${Environment}-news-${AWS::AccountId}-${AWS::Region}"

    NotificationConfiguration:
      LambdaConfigurations:
        - Event: s3:ObjectCreated:*
          Function:
            Fn::GetAtt:
              - RdsWriterFunction
              - Arn
```
Burada kullanılan `DependsOn`, S3 bucket oluşturulmadan önce Lambda invoke permission kaynağının hazır olmasını sağladı. Ayrıca RDS Writer Lambda'nın S3 üzerindeki dosyaları okuyabilmesi için gerekli IAM policy içerisinde bucket ARN'i doğrudan resource referansı ile oluşturmak yerine Fn::Sub kullanılarak üretildi. Bu yaklaşım ile CloudFormation'ın kaynaklar arasında oluşturduğu gereksiz bağımlılık azaltıldı ve circular dependency problemi giderildi. Sonuç olarak S3 üzerine yeni bir dosya yazıldığında RDS Writer Lambda'nın otomatik olarak tetiklenmesini sağlayan yapı CloudFormation üzerinden başarılı şekilde oluşturulabildi.
