import RPi.GPIO as GPIO
import time

# GPIO modunu belirle
GPIO.setmode(GPIO.BCM)

# TB6600 bağlantıları
DIR_PIN = 18  # Yön pini
PUL_PIN = 17  # Step (Pulse) pini

# GPIO çıkışlarını ayarla
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PUL_PIN, GPIO.OUT)

def step_motor(derece, hiz, yon):
    """
    Step motoru belirli derece ve hızda döndürür.
    
    derece: Döndürmek istediğin derece
    hiz: Bekleme süresi (hız), düşük değer daha hızlı döndürür
    yon: 1 -> Saat yönü, 0 -> Saat yönünün tersi
    """
    adim_sayisi = int((derece / 1.8) * 2)  # 1.8 derece/adım, 2 fazlı sürüş

    # Yönü belirle
    GPIO.output(DIR_PIN, yon)

    # Step motoru döndür
    for _ in range(adim_sayisi):
        GPIO.output(PUL_PIN, GPIO.HIGH)
        time.sleep(hiz)  # Pulse süresi
        GPIO.output(PUL_PIN, GPIO.LOW)
        time.sleep(hiz)

try:
    while True:
        print("Saat yönünde dönüyor...")
        step_motor(derece=90, hiz=0.002, yon=1)  # 90 derece saat yönünde
        time.sleep(1)

        print("Saat yönünün tersinde dönüyor...")
        step_motor(derece=90, hiz=0.002, yon=0)  # 90 derece ters yönde
        time.sleep(1)

except KeyboardInterrupt:
    print("Çıkış yapılıyor...")
    GPIO.cleanup()  # GPIO pinlerini temizle
