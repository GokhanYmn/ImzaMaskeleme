# 🖊️ İmza Maskeleme Uygulaması

PDF veya resim dosyalarındaki lacivert/mavi imzaları otomatik olarak maskeleyen basit bir **Flask web uygulaması**.

---

## 🎯 Özellikler
- PDF ve resim dosyalarını destekler (PDF, JPG, JPEG, PNG)
- Lacivert/mavi imzaları beyaz ile maskeleme
- Maskeleme sonrası çıktı PDF veya resim olarak kaydedilir
- Basit ve kullanıcı dostu web arayüzü
- Exe olarak çalıştırılabilir, Python kurulumu gerektirmez

---

## 🖥️ Kurulum (Python ile)

1. Projeyi klonlayın:
    ``bash
    git clone https://github.com/GokhanYmn/ImzaMaskeleme.git
    cd ImzaMaskeleme
   
2.Gerekli paketleri yükleyin:
    pip install -r requirements.txt

3.Poppler yolunu ayarlayın:
    POPPLER_PATH = r"D:\poppler-25.07.0\Library\bin"

4.Uygulamayı çalıştırın:
    python app.py

5.Tarayıcıdan erişin:
    http://localhost:5000

