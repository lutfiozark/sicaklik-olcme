import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QDialog, QDateEdit, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer, QThread, Qt, QDate
from sicaklik_arayuzu import Ui_label_gpu_sicakligi
from sicaklik_oku import openhardwaremonitor_calisiyor_mu, sicakliklari_al, grafiği_ciz, veritabani_olustur, sicaklik_verilerini_kaydet, verileri_al
import wmi
import time
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
import winsound

def exception_hook(exctype, value, tb):
    print("İşlenmemiş bir hata oluştu:")
    traceback.print_exception(exctype, value, tb)

sys.excepthook = exception_hook

class SicaklikUygulamasi(QMainWindow, Ui_label_gpu_sicakligi):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Pencerenin her zaman önde kalmasını sağla
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Eşik değerlerini uygulama başlangıcında oku
        self.cpu_esik = self.spinBox_cpu_esik.value()
        self.gpu_esik = self.spinBox_gpu_esik.value()
        self.disk_esik = self.spinBox_disk_esik.value()

        self.pushButton.clicked.connect(self.baslat_timer)
        self.pushButton_gecmis_veriler.clicked.connect(self.gecmis_verileri_goster)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sicakliklari_guncelle)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.donguyu_kontrol_et)
        self.dongu_calisiyor = False

        # Grafik için başlangıç ayarları
        self.zaman_verileri = []
        self.cpu_sicakliklari = []
        self.gpu_sicakliklari = []
        self.disk_sicakliklari = []
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.graphicsView_sicaklik)
        layout.addWidget(self.canvas)

        # Geçmiş veriler grafiği için başlangıç ayarları
        self.gecmis_zaman_verileri = []
        self.gecmis_cpu_sicakliklari = []
        self.gecmis_gpu_sicakliklari = []
        self.gecmis_disk_sicakliklari = []
        self.gecmis_figure = plt.figure()
        self.gecmis_canvas = FigureCanvas(self.gecmis_figure)
        layout = QVBoxLayout(self.graphicsView_gecmis)
        layout.addWidget(self.gecmis_canvas)

        # Alarm çalıyor mu?
        self.alarm_calisiyor = False

        # Tarih düzenleme widget'larını sınıf özelliklerine dönüştürün
        self.baslangic_tarihi_edit = None
        self.bitis_tarihi_edit = None

        veritabani_olustur()  # Uygulama başlangıcında veritabanını oluştur

    def openhardwaremonitor_calisiyor_mu(self):
        """OpenHardwareMonitor'ün çalışıp çalışmadığını kontrol eder."""
        try:
            w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
            w.Sensor()  # Herhangi bir sorgu çalıştır
            return True
        except wmi.x_wmi:
            return False

    def sicakliklari_al(self):
        """Sistem sıcaklık bilgilerini toplar."""
        if self.openhardwaremonitor_calisiyor_mu():
            w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
            temperature_sensors = w.Sensor()
            sicakliklar = {}
            for sensor in temperature_sensors:
                if sensor.SensorType == 'Temperature':
                    if 'cpu' in sensor.Name.lower():
                        sicakliklar['cpu'] = sensor.Value
                    elif 'gpu' in sensor.Name.lower():
                        sicakliklar['gpu'] = sensor.Value
                    elif 'hdd' in sensor.Name.lower() or 'ssd' in sensor.Name.lower():
                        sicakliklar['disk'] = sensor.Value
            return sicakliklar
        else:
            return None

    def sicakliklari_goster(self, sicakliklar):
        """Sıcaklık bilgilerini arayüzde gösterir."""
        if sicakliklar:
            if 'cpu' in sicakliklar:
                self.lineedit_cpu_sicakligi.setText(f"{sicakliklar['cpu']:.1f} °C")
            else:
                self.lineedit_cpu_sicakligi.setText("CPU Sıcaklığı Bulunamadı")
            if 'gpu' in sicakliklar:
                self.lineedit_gpu_sicakligi.setText(f"{sicakliklar['gpu']:.1f} °C")
            else:
                self.lineedit_gpu_sicakligi.setText("GPU Sıcaklığı Bulunamadı")
            if 'disk' in sicakliklar:
                self.lineedit_disk_sicakligi.setText(f"{sicakliklar['disk']:.1f} °C")
            else:
                self.lineedit_disk_sicakligi.setText("Disk Sıcaklığı Bulunamadı")
        else:
            print("Sıcaklık sensörlerinden veri alınamadı.")

    def baslat_timer(self):
        if not self.dongu_calisiyor:
            self.dongu_calisiyor = True
            self.pushButton.setText("Durdur")
            self.timer.start(5000)  # 5 saniyede bir güncelle
            self.check_timer.start(1000)  # 1 saniyede bir OpenHardwareMonitor'u kontrol et
        else:
            self.dongu_calisiyor = False
            self.pushButton.setText("Başlat")
            self.timer.stop()
            self.check_timer.stop()

    def donguyu_kontrol_et(self):
        """OpenHardwareMonitor'u kontrol eder. 
           Bulunamazsa, hata mesajı gösterir ve döngüyü durdurur, ancak uygulamayı kapatmaz.
        """
        if not self.openhardwaremonitor_calisiyor_mu():
            print("OpenHardwareMonitor bulunamadı. Sıcaklık ölçümü durduruldu.")
            self.dongu_calisiyor = False
            self.pushButton.setText("Başlat")
            self.timer.stop()
            self.check_timer.stop()
            QMessageBox.warning(self, "Hata", "OpenHardwareMonitor bulunamadı. Lütfen programı çalıştırın.")

    def sicakliklari_guncelle(self):
        """Sıcaklıkları günceller, grafiği çizer, uyarıları kontrol eder ve veritabanına kaydeder."""
        try:
            if self.openhardwaremonitor_calisiyor_mu():
                sicakliklar = self.sicakliklari_al()
                if sicakliklar:
                    self.sicakliklari_goster(sicakliklar)

                    # Grafik verilerini güncelle
                    self.zaman_verileri.append(time.time())
                    self.cpu_sicakliklari.append(sicakliklar.get('cpu', None))
                    self.gpu_sicakliklari.append(sicakliklar.get('gpu', None))
                    self.disk_sicakliklari.append(sicakliklar.get('disk', None))

                    # Grafiği çiz
                    grafiği_ciz(self.figure, self.canvas, self.zaman_verileri, 
                               self.cpu_sicakliklari, self.gpu_sicakliklari, self.disk_sicakliklari)
                    self.canvas.flush_events()  # matplotlib olaylarını PyQt5'e aktar

                    # Uyarı kontrolü
                    self.uyari_kontrol(sicakliklar)

                    # Veritabanına kaydet
                    now = datetime.now()
                    tarih = now.strftime("%Y-%m-%d")
                    saat = now.strftime("%H:%M:%S")
                    sicaklik_verilerini_kaydet(tarih, saat, 
                                            sicakliklar.get('cpu'), 
                                            sicakliklar.get('gpu'), 
                                            sicakliklar.get('disk')) 
            else:
                self.donguyu_kontrol_et()  # OpenHardwareMonitor kontrolünü tekrarla
        except Exception as e:
            print(f"Hata oluştu: {e}")
            traceback.print_exc()

    def uyari_kontrol(self, sicakliklar):
        """Eşik değer aşıldığında alarm çalar ve mesaj kutusu gösterir."""
        try:
            if 'cpu' in sicakliklar and sicakliklar['cpu'] >= self.cpu_esik:
                self.uyari_mesaji_goster("CPU sıcaklığı", sicakliklar['cpu'], self.cpu_esik)
            if 'gpu' in sicakliklar and sicakliklar['gpu'] >= self.gpu_esik:
                self.uyari_mesaji_goster("GPU sıcaklığı", sicakliklar['gpu'], self.gpu_esik)
            if 'disk' in sicakliklar and sicakliklar['disk'] >= self.disk_esik:
                self.uyari_mesaji_goster("Disk sıcaklığı", sicakliklar['disk'], self.disk_esik)

        except Exception as e:
            print(f"Hata oluştu: {e}")
            traceback.print_exc()

    def uyari_mesaji_goster(self, donanim, sicaklik, esik):
        """Kritik hata mesajını gösterir ve eş zamanlı olarak alarm çalar."""
        self.alarm_calisiyor = True  # Alarm çalmaya başlıyor

        # Alarmı ayrı bir iş parçacığında çalıştır
        self.alarm_thread = QThread()
        self.alarm_thread.run = self.alarm_cal  # İş parçacığı fonksiyonunu ayarla
        self.alarm_thread.start()

        # Mesaj kutusunu göster
        QMessageBox.critical(self, "Kritik Sıcaklık Uyarısı!",
                            f"{donanim} ({sicaklik:.1f} °C) eşik değeri ({esik} °C) aştı!")

        # Mesaj kutusu kapatıldıktan sonra alarmı durdur
        self.alarm_calisiyor = False
        self.alarm_thread.quit()
        self.alarm_thread.wait()

    def alarm_cal(self):
        """Alarm sesi çalar."""
        while self.alarm_calisiyor:
            winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
            time.sleep(1)  # 1 saniye bekle (alarmın sürekli çalmaması için)

    def gecmis_verileri_goster(self):
        """Geçmiş verileri seçmek için bir dialog penceresi açar."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Geçmiş Verileri Seç")
        layout = QVBoxLayout(dialog)

        # Başlangıç tarihi
        baslangic_tarihi_label = QLabel("Başlangıç Tarihi:", dialog)
        layout.addWidget(baslangic_tarihi_label)
        self.baslangic_tarihi_edit = QDateEdit(dialog)
        self.baslangic_tarihi_edit.setDate(QDate.currentDate().addDays(-7)) 
        layout.addWidget(self.baslangic_tarihi_edit)

        # Bitiş tarihi
        bitis_tarihi_label = QLabel("Bitiş Tarihi:", dialog)
        layout.addWidget(bitis_tarihi_label)
        self.bitis_tarihi_edit = QDateEdit(dialog)
        self.bitis_tarihi_edit.setDate(QDate.currentDate()) 
        layout.addWidget(self.bitis_tarihi_edit)

        # Butonlar
        buton_layout = QHBoxLayout()
        tamam_butonu = QPushButton("Tamam", dialog)
        tamam_butonu.clicked.connect(self.gecmis_verileri_grafikte_goster) 
        buton_layout.addWidget(tamam_butonu)
        iptal_butonu = QPushButton("İptal", dialog)
        iptal_butonu.clicked.connect(dialog.close)
        buton_layout.addWidget(iptal_butonu)
        layout.addLayout(buton_layout)

        dialog.exec_()

    def gecmis_verileri_grafikte_goster(self):
        """Seçilen tarih aralığındaki verileri grafikte gösterir."""
        baslangic_tarihi = self.baslangic_tarihi_edit.date().toString("yyyy-MM-dd")
        bitis_tarihi = self.bitis_tarihi_edit.date().toString("yyyy-MM-dd")

        # Veritabanından verileri al
        veriler = verileri_al(baslangic_tarihi, bitis_tarihi)

        # Grafik verilerini temizle
        self.gecmis_zaman_verileri.clear()
        self.gecmis_cpu_sicakliklari.clear()
        self.gecmis_gpu_sicakliklari.clear()
        self.gecmis_disk_sicakliklari.clear()

        # Verileri grafik listelerine ekle
        for veri in veriler:
            self.gecmis_zaman_verileri.append(datetime.strptime(veri[1] + " " + veri[2], "%Y-%m-%d %H:%M:%S").timestamp())
            self.gecmis_cpu_sicakliklari.append(veri[3])
            self.gecmis_gpu_sicakliklari.append(veri[4])
            self.gecmis_disk_sicakliklari.append(veri[5])

        # Grafiği çiz
        grafiği_ciz(self.gecmis_figure, self.gecmis_canvas, self.gecmis_zaman_verileri,
                   self.gecmis_cpu_sicakliklari, self.gecmis_gpu_sicakliklari, self.gecmis_disk_sicakliklari)
        self.gecmis_canvas.flush_events()

        # Seçilen tarihleri etiketlerde göster
        self.label_baslangic_tarihi.setText(f"Başlangıç Tarihi: {baslangic_tarihi}")
        self.label_bitis_tarihi.setText(f"Bitiş Tarihi: {bitis_tarihi}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = SicaklikUygulamasi()
    pencere.show()
    sys.exit(app.exec_())