# Sıcaklık İzleme ve Uyarı Sistemi

Bu Python projesi, CPU, GPU ve disk sıcaklıklarını gerçek zamanlı olarak izler. Kullanıcı tarafından belirlenen eşik sıcaklıklar aşıldığında uyarı verir ve geçmiş verileri grafiksel olarak gösterir.

## Özellikler
- PyQt5 arayüzü
- OpenHardwareMonitor kullanımı
- Anlık grafik çizimi
- SQLite veritabanı ile kayıt
- Alarm ve uyarı sistemi

## Kullanım
OpenHardwareMonitor açıkken aşağıdaki komutla çalıştırın:
```bash
python sicaklik_uygulamasi.py

## Gereksinimler
- Python 3.8+
- PyQt5
- matplotlib
- wmi