import wmi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sqlite3

def openhardwaremonitor_calisiyor_mu():
    """OpenHardwareMonitor'ün çalışıp çalışmadığını kontrol eder."""
    try:
        w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
        w.Sensor()  # Herhangi bir sorgu çalıştır
        return True
    except wmi.x_wmi:
        return False

def sicakliklari_al():
    """Sistem sıcaklık bilgilerini toplar.
       OpenHardwareMonitor çalışmıyorsa None döndürür.
    """
    try:
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
                    sicakliklar[sensor.Name] = sensor.Value
        return sicakliklar
    except wmi.x_wmi:
        return None

def grafiği_ciz(figure, canvas, zaman_verileri, cpu_sicakliklari, gpu_sicakliklari, disk_sicakliklari):
    """Sıcaklık grafiğini çizer."""
    figure.clear()  # Grafiği temizle
    ax = figure.add_subplot(111)

    ax.plot(zaman_verileri, cpu_sicakliklari, label='CPU')
    ax.plot(zaman_verileri, gpu_sicakliklari, label='GPU')
    ax.plot(zaman_verileri, disk_sicakliklari, label='Disk')

    ax.set_xlabel('Zaman')
    ax.set_ylabel('Sıcaklık (°C)')
    ax.legend()
    canvas.draw()  # Grafiği güncelle

def veritabani_olustur():
    """Sıcaklık verilerini kaydetmek için bir veritabanı ve tablo oluşturur."""
    conn = sqlite3.connect('sicakliklar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sicaklik_verileri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            saat TEXT,
            cpu_sicaklik REAL,
            gpu_sicaklik REAL,
            disk_sicaklik REAL
        )
    ''')
    conn.commit()
    conn.close()

def sicaklik_verilerini_kaydet(tarih, saat, cpu_sicaklik, gpu_sicaklik, disk_sicaklik):
    """Sıcaklık verilerini veritabanına kaydeder."""
    conn = sqlite3.connect('sicakliklar.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sicaklik_verileri (tarih, saat, cpu_sicaklik, gpu_sicaklik, disk_sicaklik)
        VALUES (?, ?, ?, ?, ?)
    ''', (tarih, saat, cpu_sicaklik, gpu_sicaklik, disk_sicaklik))
    conn.commit()
    conn.close()

def verileri_al(baslangic_tarihi, bitis_tarihi):
    """Veritabanından belirli bir tarih aralığındaki verileri alır."""
    conn = sqlite3.connect('sicakliklar.db')
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT * FROM sicaklik_verileri 
        WHERE tarih BETWEEN '{baslangic_tarihi}' AND '{bitis_tarihi}'
    ''')
    veriler = cursor.fetchall()
    conn.close()
    return veriler