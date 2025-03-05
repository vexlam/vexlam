import sqlite3
import os
from datetime import datetime, timedelta
import locale
from flask import Flask, flash  # Flask eksikti, eklendi
from flask_cors import CORS  # CORS eksikti, eklendi


# 📌 Veritabanı Bağlantısı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Eğer "database" klasörü içindeyse bu satırı kullan:
DB_PATH = os.path.join(BASE_DIR, "database", "databasestudents.db")

# ✅ Eğer "database" klasörü yoksa, aşağıdaki satırı kullan:
# DB_PATH = os.path.join(BASE_DIR, "databasestudents.db")

def get_db_connection():
    """ Veritabanına bağlanır ve SQLite Row Formatında döndürür. """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Sözlük formatında sonuç döndür
    return conn



def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")

    column_names = [desc[0] for desc in cursor.description]
    students = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    
    print("Öğrenciler:", students)  # Konsolda görmek için
    conn.close()
    return students






def transfer_students_to_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Öğrencileri "yoklamalar" tablosuna aktar (eğer zaten yoksa ekleme)
    cursor.execute("""
        INSERT INTO yoklamalar (ogrenci_id, seans_turu, seans_saati, tarih, yoklama_durumu)
        SELECT id, seans_turu, seans_saati, DATE('now'), 'Bilinmiyor'
        FROM students
        WHERE id NOT IN (SELECT ogrenci_id FROM yoklamalar WHERE tarih = DATE('now'))

    """)

    conn.commit()
    conn.close()
    print("📌 Tüm öğrenciler yoklama sistemine eklendi!")

# Fonksiyonu çalıştır
transfer_students_to_attendance()






def add_student_db(student_data):
    try:
        # 📌 Veritabanı bağlantısını aç
        conn = get_db_connection()
        cursor = conn.cursor()

        # 📌 Seans ücretleri
        seans_ucretleri = {
            "GDO-115": 1500,
            "GDO-130": 2000,
            "GA-200": 2500,
            "AH-400": 3000
        }

        # 📌 Seans türüne göre günleri belirleyelim
        seans_gunleri_mapping = {
            "GDO-115": "Salı, Perşembe",
            "GDO-130": "Salı, Perşembe",
            "GA-200": "Salı, Perşembe",
            "AH-400": "Pazartesi, Çarşamba, Cuma"
        }
        seans_gunleri = seans_gunleri_mapping.get(student_data.get("seans_turu", ""), "")

        # 📌 Debug için öğrenci verisini yazdır
        print("📌 Eklenen öğrenci verisi:", student_data)

        # 📌 Eksik veri kontrolü
        required_fields = ["ad", "soyad", "tc", "dogum_tarihi", "veli_adi", "veli_telefon", "seans_turu", "seans_saati", "odeme_turu"]
        missing_fields = [field for field in required_fields if not student_data.get(field)]

        if missing_fields:
            flash(f"⚠️ Eksik Alanlar: {', '.join(missing_fields)}", "danger")
            return False

        # 📌 Seans ücretini belirleme
        toplam_ucret = seans_ucretleri.get(student_data.get("seans_turu", ""), 0)

        # 📌 Geçerli float dönüşümü (Eğer boşsa veya None ise 0 yap)
        odenen = float(student_data.get("odenen_miktar", "0") or 0)
        kalan = max(0, toplam_ucret - odenen)

        # 📌 SQL sorgusunu çalıştır
        cursor.execute("""
            INSERT INTO students (ad, soyad, tc, dogum_tarihi, kayit_tarihi, veli_adi, veli_telefon, 
                                  seans_turu, seans_fiyat, seans_saati, odenen_miktar, kalan_miktar, 
                                  odeme_turu, seans_gunleri, created_at)
            VALUES (?, ?, ?, ?, DATE('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            student_data.get("ad", ""),
            student_data.get("soyad", ""),
            student_data.get("tc", ""),
            student_data.get("dogum_tarihi", ""),
            student_data.get("veli_adi", ""),
            student_data.get("veli_telefon", ""),
            student_data.get("seans_turu", ""),
            toplam_ucret,
            student_data.get("seans_saati", ""),
            odenen,
            kalan,
            student_data.get("odeme_turu", "Nakit"),  # Varsayılan olarak "Nakit"
            seans_gunleri
        ))

        # 📌 Değişiklikleri kaydet
        conn.commit()

        # 📌 Başarı mesajı ve konsol çıktısı
        flash("✅ Öğrenci başarıyla eklendi!", "success")
        print("✅ Öğrenci başarıyla veritabanına eklendi!")

        return True

    except sqlite3.Error as e:
        flash(f"❌ Veritabanı Hatası: {str(e)}", "danger")
        print(f"❌ Veritabanı Hatası: {str(e)}")
        return False
    except Exception as e:
        flash(f"❌ Genel Hata: {str(e)}", "danger")
        print(f"❌ Genel Hata: {str(e)}")
        return False
    finally:
        conn.close()





def get_seans_sayisi(seans_turu):
    seans_bilgileri = {
        "GDO-115": 8,  # Salı - Perşembe
        "GDO-130": 8,  # İki farklı saat (10:00 - 11:30 / 17:15 - 18:45)
        "GA-200": 8,  # Salı - Perşembe
        "AH-400": 12   # Pazartesi - Çarşamba - Cuma
    }
    return seans_bilgileri.get(seans_turu, 0)  # Eğer eşleşmezse 0 döndür




def check_students():
    conn = sqlite3.connect("database/databasestudents.db")  # Veritabanı dosyanın adı neyse onu kullan
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY created_at DESC LIMIT 5;")
    
    students = cursor.fetchall()
    conn.close()
    
    if students:
        for student in students:
            print(student)
    else:
        print("⚠️ Veritabanında öğrenci bulunamadı.")

# Fonksiyonu çalıştır
check_students()


def get_seans():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seans_takvimi")
    seanslar = cursor.fetchall()
    conn.close()
    return seanslar







### 📌 Öğrenciyi Güncelle
def update_student(student_id, student_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET ad=?, soyad=?, tc=?, dogum_tarihi=?, veli_adi=?, veli_telefon=?, seans_turu=?, seans_saati=?, odeme_turu=? WHERE id=?",
                   (student_data["ad"], student_data["soyad"], student_data["tc"], student_data["dogum_tarihi"], student_data["veli_adi"], student_data["veli_telefon"], student_data["seans_turu"], student_data["seans_saati"], student_data["odeme_turu"], student_id))
    conn.commit()
    conn.close()

### 📌 Öğrenciyi Sil
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

### 📌 Ders Programını Getir
def get_schedule():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedule")
    schedule = cursor.fetchall()
    conn.close()
    return schedule

def add_seans(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO seans_takvimi (name, teacher, date, time, capacity) VALUES (?, ?, ?, ?, ?)",
        (data["name"], data["teacher"], data["date"], data["time"], data.get("capacity", 0))
    )
    conn.commit()
    conn.close()
def update_seans(seans_turu, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE seans_takvimi SET name = ?, teacher = ?, date = ?, time = ?, capacity = ? WHERE id = ?",
        (data["name"], data["teacher"], data["date"], data["time"], data.get("capacity", 0), seans_turu)
    )
    conn.commit()
    conn.close()

def delete_seans(seans_turu):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seans_takvimi WHERE id = ?", (seans_turu,))
    conn.commit()
    conn.close()


### 📌 Seans Takvimini Getir
def get_seans_takvimi():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seans_takvimi")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

### 📌 Seans Ekle
def add_seans(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO seans_takvimi (name, teacher, date, time, capacity) VALUES (?, ?, ?, ?, ?)",
                   (data["name"], data["teacher"], data["date"], data["time"], data.get("capacity", 0)))
    conn.commit()
    conn.close()

### 📌 Seansı Güncelle
def update_seans(seans_turu, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE seans_takvimi SET name = ?, teacher = ?, date = ?, time = ?, capacity = ? WHERE id = ?",
                   (data["name"], data["teacher"], data["date"], data["time"], data.get("capacity", 0), seans_turu))
    conn.commit()
    conn.close()

### 📌 Seansı Sil
def delete_seans(seans_turu):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seans_takvimi WHERE id = ?", (seans_turu,))
    conn.commit()
    conn.close()

### 📌 Ödeme Kayıtlarını Getir
def get_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    conn.close()
    return payments

### 📌 Güncellemeleri Getir
def get_updates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM updates ORDER BY date DESC")
    updates = cursor.fetchall()
    conn.close()
    return updates

def get_seans(seans_turu):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seans_takvimi WHERE id = ?", (seans_turu,))
    seans = cursor.fetchone()
    conn.close()
    return seans

def get_seans(seans_turu):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seans_takvimi WHERE id = ?", (seans_turu,))
    seans = cursor.fetchone()
    conn.close()
    return seans

def get_late_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Geciken ödemesi olan öğrencileri çek
    cursor.execute("SELECT ad, soyad, veli_telefon, kalan_odeme FROM students WHERE kalan_odeme > 0")
    students = [{"ad": row[0], "soyad": row[1], "veli_telefon": row[2], "kalan_odeme": row[3]} for row in cursor.fetchall()]
    
    conn.close()
    return students

def get_seanslar():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seanslar")
    seanslar = cursor.fetchall()
    conn.close()
    return seanslar




def get_monthly_report():
    conn = get_db_connection()
    if conn is None:
        return {"month": "N/A", "total_students": 0, "total_due": 0}

    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            strftime('%Y-%m', date('now')) as month,
            COUNT(*) as total_students,
            SUM(CASE WHEN kalan_odeme > 0 THEN kalan_odeme ELSE 0 END) as total_due
        FROM students
    """)

    result = cursor.fetchone()
    conn.close()

    return {
        "month": result[0] or "N/A",
        "total_students": result[1] or 0,
        "total_due": result[2] or 0
    }





from datetime import datetime, timedelta

# 📌 İngilizce → Türkçe gün çeviri tablosu
EN_TR_DAYS = {
    "Monday": "Pazartesi",
    "Tuesday": "Salı",
    "Wednesday": "Çarşamba",
    "Thursday": "Perşembe",
    "Friday": "Cuma",
    "Saturday": "Cumartesi",
    "Sunday": "Pazar"
}

# 📌 Seans Bilgileri (Hangi Günlerde Ders Var?)
SEANS_BILGILERI = {
    "GDO-115": {"gunler": ["Salı", "Perşembe"], "saatler": ["15:15 - 16:30"]},
    "GDO-130": {"gunler": ["Salı", "Perşembe"], "saatler": ["10:00 - 11:30", "17:15 - 18:45"]},
    "GA-200": {"gunler": ["Salı", "Perşembe"], "saatler": ["12:30 - 14:30"]},
    "AH-400": {"gunler": ["Pazartesi", "Çarşamba", "Cuma"], "saatler": ["13:00 - 17:00"]}
}

def get_student_seans_dates(kayit_tarihi, seans_turu, ay_sayisi=3):
    """ 📌 Öğrencinin seanslarını belirlenen süre boyunca hesaplar """
    try:
        if seans_turu not in SEANS_BILGILERI:
            raise ValueError(f"⚠️ HATA: Geçersiz Seans Türü - {seans_turu}")

        kayit_tarihi = datetime.strptime(kayit_tarihi, "%Y-%m-%d")
        bitis_tarihi = kayit_tarihi + timedelta(days=30 * ay_sayisi)

        seans_gunleri = SEANS_BILGILERI[seans_turu]["gunler"]
        seans_saatleri = SEANS_BILGILERI[seans_turu]["saatler"]

        seans_listesi = []
        tarih = kayit_tarihi

        while tarih <= bitis_tarihi:
            gun_adi_tr = EN_TR_DAYS.get(tarih.strftime("%A"), "Bilinmeyen Gün")
            if gun_adi_tr in seans_gunleri:
                for saat in seans_saatleri:
                    seans_listesi.append({"date": tarih.strftime("%Y-%m-%d"), "time": saat})
            tarih += timedelta(days=1)

        return seans_listesi

    except Exception as e:
        print(f"⚠️ Tarih Hesaplama Hatası: {str(e)}")
        return []
