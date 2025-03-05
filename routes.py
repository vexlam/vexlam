from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import sqlite3
import os
import json
from datetime import datetime  # 📌 Burada sadece datetime sınıfını içe aktarıyoruz
from db_models import get_students  # Öğrenci modeli
from app import app


# ✅ Veritabanı yolu
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "databasestudents.db")  # Veritabanı yolunu oluştur

# ✅ Veritabanı bağlantı fonksiyonu
def get_db_connection():
    """ SQLite Veritabanına bağlanır ve Row Formatında döndürür. """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  # Foreign Key desteğini aç
    return conn


# ✅ Seans tablosunu kontrol etme fonksiyonu
def check_seans_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(seans_takvimi)")
    columns = cursor.fetchall()

    if columns:  # Eğer tablo varsa
        print(f"✅ Bugün ({datetime.today().strftime('%Y-%m-%d')}) yoklama sayfası çalıştırıldı.")  
    else:
        print("⚠️ Seans tablosu bulunamadı!")

    conn.close()

# ✅ Seans tablosunu kontrol et
check_seans_table()



# 📌 Ana Sayfa (Index)
@app.route('/')
def homepage():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 📌 Bugünün tarihini al
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 📌 Bugünün yoklamasını çek
    cursor.execute("SELECT COUNT(*) FROM yoklamalar WHERE tarih = ?", (today_str,))
    bugun_yoklama_sayisi = cursor.fetchone()[0]

    # 📌 Kalan seansı 2 veya daha az olan öğrenci sayısını çekiyoruz
    cursor.execute("SELECT COUNT(*) FROM students WHERE kalan_seans <= 2")
    kritik_ogrenci_sayisi = cursor.fetchone()[0]

    conn.close()

    yoklama_alindi_mi = (bugun_yoklama_sayisi > 0)
    kritik_ogrenci_var_mi = (kritik_ogrenci_sayisi > 0)

    return render_template('index.html',
                           yoklama_alindi_mi=yoklama_alindi_mi,
                           kritik_ogrenci_var_mi=kritik_ogrenci_var_mi)


# 📌 Bugünün Yoklamasını Al
@app.route('/today_attendance_page', methods=['GET', 'POST'])
def today_attendance_page():
    if request.method == 'POST':
        # 📌 POST isteğiyle yoklama kaydedilir
        flash("Yoklama kaydedildi!", "success")
        return redirect(url_for('attendance'))
    
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.today().strftime("%Y-%m-%d")

        # 📌 Bugün hangi öğrencilerin seansı var, onları çekiyoruz
        cursor.execute("""
            SELECT id, ad, soyad, veli_adi, veli_telefon, seans_turu, seans_saati 
            FROM students 
            WHERE seans_gunleri LIKE ?
        """, (f"%{today}%",))  # ✅ `seans_saati` yerine `seans_gunleri` kullanıldı

        students = cursor.fetchall()
        conn.close()

        students_list = [
            {"id": row["id"], "ad": row["ad"], "soyad": row["soyad"], 
             "veli_adi": row["veli_adi"], "veli_telefon": row["veli_telefon"], 
             "seans_turu": row["seans_turu"], "seans_saati": row["seans_saati"]}
            for row in students
        ]

        return render_template("today_attendance.html", students=students_list)
    


@app.route('/api/seans_takvimi', methods=['GET'])
def get_seans_takvimi():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, session_name, session_date, session_days, session_time, session_fee FROM seans_takvimi")
    
    seanslar = []
    for row in cursor.fetchall():
        try:
            session_days = json.loads(row["session_days"]) if row["session_days"] else ["Tanımsız"]
        except json.JSONDecodeError:
            session_days = ["Tanımsız"]

        seanslar.append({
            "id": row["id"],
            "session_name": row["session_name"],
            "session_days": ", ".join(session_days),  # ✅ **Hatalı `session_date` yerine `session_days` kullanıldı!**
            "session_time": row["session_time"],
            "session_fee": row["session_fee"]
        })

    conn.close()
    return jsonify(seanslar)






# 📌 Uygulamayı Çalıştır
if __name__ == "__main__":
    app.run(debug=True)
