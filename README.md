<h1 align="center"> Sıcaklık İzleme ve Uyarı Sistemi</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/gui-PyQt5-green?style=flat-square" alt="PyQt5">
  <img src="https://img.shields.io/badge/database-SQLite-lightgrey?style=flat-square" alt="SQLite">
</p>

---

##  Proje Hakkında

Bu Python tabanlı masaüstü uygulama, CPU, GPU ve disk sıcaklıklarını gerçek zamanlı olarak izler.  
Kullanıcının belirlediği eşik sıcaklıklar aşıldığında alarm sesi çalar ve uyarı mesajı gösterilir.  
Ayrıca geçmiş veriler veritabanına kaydedilir ve tarih aralığına göre grafiksel olarak görüntülenebilir.

---

##  Özellikler

-  PyQt5 ile kullanıcı dostu arayüz
-  OpenHardwareMonitor ile anlık donanım sıcaklık okuma
-  Eşik aşımlarında sesli uyarı ve mesaj kutusu
-  SQLite ile geçmiş verileri kaydetme
-  Tarihe göre grafik çizimi (matplotlib)

---

##  Kurulum ve Gereksinimler

### 1. Python Gereksinimi
Uygulama Python 3.8+ ile test edilmiştir.  
Python yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirip kurabilirsiniz.

### 2. Gerekli Python Kütüphaneleri

Terminal veya CMD üzerinden aşağıdaki komutu çalıştırarak gerekli kütüphaneleri yükleyin:

pip install pyqt5 matplotlib wmi

### 3. OpenHardwareMonitor Kurulumu (Windows için)
Donanım sıcaklıklarını okuyabilmek için aşağıdaki adımları izleyin:

- https://openhardwaremonitor.org/downloads/
- ZIP dosyasını çıkarın
- OpenHardwareMonitor.exe dosyasını çalıştırın
- Uygulama açık kaldığı sürece Python uygulaması sensörlere erişebilir

### 4. Uygulamayı Başlatma
python sicaklik_uygulamasi.py 

- python terminalinde çalıştırın

---

## Veritabanı Yapısı

| Alan Adı       | Tür     | Açıklama                  |
| -------------- | ------- | ------------------------- |
| id             | INTEGER | Otomatik artan ID         |
| tarih          | TEXT    | Ölçüm tarihi (yyyy-MM-dd) |
| saat           | TEXT    | Ölçüm saati (HH\:mm\:ss)  |
| cpu\_sicaklik  | REAL    | CPU sıcaklığı (°C)        |
| gpu\_sicaklik  | REAL    | GPU sıcaklığı (°C)        |
| disk\_sicaklik | REAL    | Disk sıcaklığı (°C)       |

### Platform Uyarısı
- Bu uygulama sadece Windows işletim sistemi üzerinde çalışmaktadır.
- Linux/macOS desteği yoktur.
