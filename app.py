import os
import sys
import sqlite3
import csv
import json
import requests
import fitz  
import random
from io import StringIO
from datetime import datetime, timedelta
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, flash, session
from flask_cors import CORS
from flask import send_file, abort
from __init__ import create_app  # ✅ `create_app()` çağrılıyor

# 📌 Flask Uygulamasını Başlat
app = create_app()


# 📌 Veritabanı Bağlantısı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "databasestudents.db")

def get_db_connection():
    """ Veritabanına bağlanır ve SQLite Row Formatında döndürür. """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Sözlük formatında sonuç döndür
    return conn

# 📌 Veritabanı İşlemleri için db_models Modülünü İçe Aktar
from db_models import (
    get_students, add_student_db, update_student, delete_student, 
    get_seans_takvimi, get_payments, get_updates, 
    add_seans, update_seans, delete_seans
)

# 📌 Routes (URL Tanımlamaları)
import routes 




@app.route('/')
def home():
    return render_template('index.html')



# 📌 Öğrenci Ekleme Sayfası (Hem Form Hem API İçin)
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            required_fields = ["ad", "soyad", "tc", "dogum_tarihi", "veli_adi", "veli_telefon", "seans_turu", "seans_fiyat", "seans_saati", "odeme_turu"]
            for field in required_fields:
                if field not in data or not data[field].strip():
                    flash(f"❌ Eksik Alan: {field}", "danger")
                    return redirect(url_for('add_student'))  # Eksikse geri dön

            # Doğum tarihi ve fiyat doğrulama işlemleri burada...

            # Veritabanına kaydet
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (ad, soyad, tc, dogum_tarihi, veli_adi, veli_telefon, seans_turu, seans_fiyat, seans_saati, odeme_turu) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data["ad"], data["soyad"], data["tc"], data["dogum_tarihi"], data["veli_adi"], data["veli_telefon"], data["seans_turu"], data["seans_fiyat"], data["seans_saati"], data["odeme_turu"]))

            conn.commit()
            conn.close()

            flash("✅ Öğrenci başarıyla eklendi!", "success")  # 🎉 Başarı mesajı
            return redirect(url_for('list_students'))  # Listeye yönlendir

        except Exception as e:
            flash(f"Hata oluştu: {str(e)}", "danger")
            return redirect(url_for('add_student'))  # Hata varsa geri dön

    return render_template('add_student.html')







# 📌 Belirli Bir Seansa Kayıtlı Öğrencileri Getiren API
@app.route('/api/ogrenciler/<int:seans_id>')
def get_ogrenciler(seans_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT session_date FROM seans_takvimi WHERE id = ?", (seans_id,))
    seans_info = cursor.fetchone()

    if not seans_info:
        return jsonify({"error": "Seans bulunamadı"}), 404

    session_date = seans_info[0]

    cursor.execute("""
        SELECT id, ad, soyad, seans_turu, seans_saati, devamsizlik 
        FROM students 
        WHERE seans_gunleri LIKE ?
    """, (f"%{session_date}%",))

    students = [{"id": row[0], "ad": row[1], "soyad": row[2], "seans_turu": row[3], "seans_saati": row[4], "devamsizlik": row[5]} for row in cursor.fetchall()]

    conn.close()
    return jsonify(students)


# 📌 Ana Sayfa (Takvim Görünümü)
@app.route("/takvim")
def takvim():
    return render_template("takvim.html")


@app.route('/list_students')
def list_students():
    students = get_students() or []
    return render_template('list_students.html', students=students)


@app.route('/attendance')
def attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 📌 Bugünün tarihini ve gününü al
    today_date = datetime.today().strftime('%Y-%m-%d')  # Örn: "2025-03-03"
    today_day = datetime.today().strftime('%A')  # Örn: "Monday", "Tuesday"

    # 📌 Bugünün seansı olan öğrencileri çek
    cursor.execute("""
        SELECT id, ad, soyad, seans_turu, seans_saati, seans_gunleri 
        FROM students 
        WHERE seans_gunleri LIKE ?
    """, (f"%{today_day}%",))

    students = cursor.fetchall()
    conn.close()
    
    return render_template("attendance.html", students=students, today_date=today_date)



@app.route('/payment_tracking')
def payment_tracking():
    payments = get_payments() or []  # Ödeme bilgilerini al
    return render_template('payment_tracking.html', payments=payments)







# 📌 Rastgele Renk Üreten Fonksiyon (Her Seans Türü İçin Farklı)
def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))



# ✅ Seans Ekleme API'si
@app.route('/add_seans', methods=['POST'])
def add_seans():
    try:
        data = request.get_json()
        session_name = data.get("session_name", "")
        session_date = data.get("session_date", "")
        session_time = data.get("session_time", "")
        session_fee = float(data.get("session_fee", 0))
        session_count = int(data.get("session_count", 1))

        # 📌 Günleri JSON olarak kaydet
        session_days = data.get("session_days", [])
        session_days_json = json.dumps(session_days)

        # 📌 Veritabanına ekle
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO seans_takvimi (session_name, session_date, session_days, session_time, session_fee, session_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_name, session_date, session_days_json, session_time, session_fee, session_count))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Seans başarıyla eklendi!"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Hata oluştu: {str(e)}"}), 400

# ✅ Seansları Listeleme API'si
@app.route('/api/seanslar', methods=['GET'])
def get_seanslar():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seans_takvimi")
    seanslar = cursor.fetchall()
    conn.close()

    seans_list = []
    for row in seanslar:
        try:
            session_days = json.loads(row["session_days"])  # JSON formatına çevir
        except json.JSONDecodeError:
            session_days = ["Tanımsız"]  # Hatalı verileri yakala
        
        seans_list.append({
            "id": row["id"],
            "title": row["session_name"],
            "start": row["session_date"],
            "days": session_days,  # 📌 Artık JSON formatında!
            "time": row["session_time"],
            "fee": row["session_fee"],
            "count": row["session_count"]
        })

    return jsonify(seans_list)





@app.route('/admin_panel')
def admin_panel():
    return render_template('admin_panel.html')



@app.route('/seanslar')
def seanslar():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 📌 Seansları veritabanından çek
    cursor.execute("SELECT * FROM seans_takvimi")
    seanslar = cursor.fetchall()
    
    conn.close()
    
    return render_template('seanslar.html', seanslar=seanslar)


@app.route('/schedule')
def schedule():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT seans_turu, ad, soyad, seans_saati, seans_gunleri, kayit_tarihi
        FROM students
        ORDER BY kayit_tarihi DESC, seans_turu, seans_saati
    """)
    
    students = cursor.fetchall()
    conn.close()

    seans_listesi = {"Geçmiş Seanslar": {}, "Gelecek Seanslar": {}}
    bugun = datetime.today().date()

    for student in students:
        seans_tarihi = datetime.strptime(student[5], "%Y-%m-%d").date()
        kategori = "Geçmiş Seanslar" if seans_tarihi < bugun else "Gelecek Seanslar"

        seans_turu = student[0]
        if seans_turu not in seans_listesi[kategori]:
            seans_listesi[kategori][seans_turu] = []
        seans_listesi[kategori][seans_turu].append(student)

    return render_template("schedule.html", seans_listesi=seans_listesi)


@app.route('/seans_takvimi')
def seans_takvimi():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 📌 Tüm seansları çek
    cursor.execute("""
        SELECT id, session_name, session_date, session_time, session_fee, session_count 
        FROM seans_takvimi
    """)
    
    seanslar = cursor.fetchall()
    conn.close()

    return render_template("takvim.html", seanslar=seanslar)


@app.route('/lesson_management')
def lesson_management():
    return render_template('lesson_management.html')



@app.route('/update_log')
def update_log():
    updates = get_updates() or []  # Güncellemeleri veritabanından çek
    return render_template('update_log.html', updates=updates)





@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    for key, value in request.form.items():
        if key.startswith("attendance_"):
            student_id = key.split("_")[1]

            # 📌 Öğrencinin o gün için zaten yoklaması var mı kontrol et
            cursor.execute("""
                SELECT yoklama_durumu FROM yoklamalar 
                WHERE ogrenci_id = ? AND tarih = DATE('now')
            """, (student_id,))
            existing_record = cursor.fetchone()

            if existing_record:
                # 📌 Eğer kayıt varsa ve değer değişiyorsa, güncelle
                if existing_record[0] != value:
                    cursor.execute("""
                        UPDATE yoklamalar SET yoklama_durumu = ? 
                        WHERE ogrenci_id = ? AND tarih = DATE('now')
                    """, (value, student_id))
            else:
                # 📌 Eğer yoksa, yeni kayıt ekle
                cursor.execute("""
                    INSERT INTO yoklamalar (ogrenci_id, tarih, yoklama_durumu)
                    VALUES (?, DATE('now'), ?)
                """, (student_id, value))

            # 📌 Eğer öğrenci "Gelmedi" seçilmişse ve daha önce "Gelmedi" olarak kayıtlı değilse devamsızlık artır
            if value == "Gelmedi":
                cursor.execute("""
                    UPDATE students
                    SET devamsizlik = devamsizlik + 1
                    WHERE id = ? AND NOT EXISTS 
                    (SELECT 1 FROM yoklamalar WHERE ogrenci_id = ? AND tarih = DATE('now') AND yoklama_durumu = 'Gelmedi')
                """, (student_id, student_id))

                print(f"✅ Devamsızlık güncellendi: Öğrenci ID {student_id}")

    conn.commit()
    conn.close()

    flash("📌 Yoklama başarıyla kaydedildi ve devamsızlık güncellendi!", "success")
    return redirect(url_for('attendance'))





@app.route('/export_students', methods=['GET'])
def export_students():
    students = get_students() or []  # 📌 Öğrenci listesini çek
    si = StringIO()
    writer = csv.writer(si)

    # 📌 CSV Başlıkları
    writer.writerow(["ID", "Ad", "Soyad", "Ödeme Durumu", "Devamsızlık", "Kayıt Tarihi"])

    # 📌 Öğrenci verilerini ekle
    for student in students:
        writer.writerow([
            student.get("id", ""), 
            student.get("ad", ""), 
            student.get("soyad", ""),
            student.get("odeme_durumu", ""), 
            student.get("devamsizlik", ""),
            student.get("kayit_tarihi", "")
        ])
    
    # 📌 CSV Yanıtı Döndür
    output = Response(si.getvalue(), mimetype="text/csv")
    output.headers["Content-Disposition"] = "attachment; filename=ogrenci_listesi.csv"
    
    return output



@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form.to_dict()
        cursor.execute("""
            UPDATE students 
            SET ad=?, soyad=?, tc=?, dogum_tarihi=?, veli_adi=?, veli_telefon=?, 
                seans_turu=?, seans_saati=?, odeme_turu=? 
            WHERE id=?
        """, (
            data.get("ad", ""), data.get("soyad", ""), data.get("tc", ""), data.get("dogum_tarihi", ""),
            data.get("veli_adi", ""), data.get("veli_telefon", ""), data.get("seans_turu", ""), 
            data.get("seans_saati", ""), data.get("odeme_turu", ""), student_id
        ))
        conn.commit()
        conn.close()
        flash("✅ Öğrenci bilgileri güncellendi!", "success")
        return redirect(url_for('list_students'))

    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        flash("⚠️ Öğrenci bulunamadı!", "danger")
        return redirect(url_for('list_students'))

    return render_template('edit_student.html', student=student)



@app.route('/student/<int:student_id>')
def student_details(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Öğrenci bilgilerini çek
    cursor.execute("""
        SELECT id, ad, soyad, veli_adi, veli_telefon, seans_turu, seans_saati, devamsizlik 
        FROM students WHERE id = ?
    """, (student_id,))
    student = cursor.fetchone()

    # Eğer öğrenci yoksa, 404 hatası ver
    if student is None:
        flash("⚠️ Öğrenci bulunamadı!", "danger")
        return redirect(url_for('list_students'))

    # ✅ Öğrencinin yoklama geçmişini çek
    cursor.execute("""
        SELECT tarih, yoklama_durumu FROM yoklamalar 
        WHERE ogrenci_id = ? ORDER BY tarih DESC
    """, (student_id,))
    attendance_history = cursor.fetchall()

    # ✅ Öğrencinin ödeme geçmişini çek (Eğer ödeme sistemi kullanılıyorsa)
    cursor.execute("""
        SELECT amount, payment_date, status FROM payments 
        WHERE student_id = ? ORDER BY payment_date DESC
    """, (student_id,))
    payment_history = cursor.fetchall()

    conn.close()

    return render_template("student_details.html", student=student, 
                           attendance_history=attendance_history, 
                           payment_history=payment_history)



@app.route('/delete_seans/<int:seans_id>', methods=['DELETE'])
def delete_seans(seans_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM seans_takvimi WHERE id = ?", (seans_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Seans başarıyla silindi!"})


@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Öğrenci var mı kontrol et
        cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()

        if not student:
            conn.close()
            return jsonify({"success": False, "message": "⚠️ Öğrenci bulunamadı!"}), 404

        # Öğrenciyi sil
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "✅ Öğrenci başarıyla silindi!"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Hata oluştu: {str(e)}"}), 500




@app.route('/student_details/<int:student_id>')
def student_info(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        return "Öğrenci bulunamadı!", 404

    return render_template("student_details.html", student=student)



def dict_from_row(row):
    return dict(zip(row.keys(), row))

@app.route('/student_form/<int:student_id>')
def student_form(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        return f"Hata: ID {student_id} ile öğrenci bulunamadı!", 404

    student = dict_from_row(student)  # ✅ SQL Row'u Dictionary formatına çeviriyoruz

    conn.close()
    return render_template("student_form.html", student=student)







# 📌 Güncellenmiş Route Listesi Yazdır
print(app.url_map)

# 📌 Uygulamayı Çalıştır
if __name__ == "__main__":
    app.run(debug=True)
