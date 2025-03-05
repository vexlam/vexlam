// Bugünün yoklamasını aç
function openAttendancePopup() {
    document.getElementById("attendancePopup").style.display = "block";
}

// Bugünün yoklamasını kapat
function closeAttendancePopup() {
    document.getElementById("attendancePopup").style.display = "none";
}

// Bugünün yoklamasını yükle
function loadTodayAttendance() {
    fetch('/api/today_attendance')
    .then(response => response.json())
    .then(data => {
        let tbody = document.getElementById("todayAttendanceList");
        tbody.innerHTML = "";  

        if (data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>Bugün için yoklama verisi bulunamadı.</td></tr>";
            return;
        }

        data.forEach(student => {
            let row = `<tr class="text-center">
                <td>${student.ad}</td>
                <td>${student.soyad}</td>
                <td>${student.seans_turu}</td>
                <td>${student.seans_saati}</td>
                <td>
                    <button class="btn btn-success btn-sm" onclick="submitAttendance(${student.id}, 'Geldi')">✅ Geldi</button>
                    <button class="btn btn-danger btn-sm" onclick="submitAttendance(${student.id}, 'Gelmedi')">❌ Gelmedi</button>
                </td>
            </tr>`;
            tbody.innerHTML += row;
        });

        openAttendancePopup();
    })
    .catch(error => console.error("Hata:", error));
}

// Bütün öğrencileri yükle
function loadAllStudents() {
    fetch('/api/all_students')
    .then(response => response.json())
    .then(data => {
        let tbody = document.getElementById("studentList");
        tbody.innerHTML = "";

        data.forEach(student => {
            let row = `<tr class="text-center">
                <td><input type="checkbox"></td>
                <td><input type="checkbox"></td>
                <td>${student.ad} ${student.soyad}</td>
                <td>${student.seans_turu}</td>
                <td>${student.seans_saati}</td>
                <td>${student.devamsizlik}</td>
            </tr>`;
            tbody.innerHTML += row;
        });
    })
    .catch(error => console.error("Hata:", error));
}

// Yoklama kaydetme işlemi
function submitAttendance(studentId, status) {
    fetch('/api/take_attendance', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            student_id: studentId,
            status: status
        })
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
        loadTodayAttendance();
    })
    .catch(error => console.error("Hata:", error));
}

// Sayfa yüklendiğinde butonları bağla
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("btnTodayAttendance").addEventListener("click", loadTodayAttendance);
    document.getElementById("btnAllStudents").addEventListener("click", loadAllStudents);
});


// Pop-up açma ve kapama fonksiyonları
function openAttendancePopup() {
    document.getElementById("attendancePopup").style.display = "block";
}

function closeAttendancePopup() {
    document.getElementById("attendancePopup").style.display = "none";
}

// Bugünün yoklamasını yükle (tüm bugünkü öğrencileri getir)
function loadTodayAttendance() {
    fetch('/api/today_attendance')
    .then(response => response.json())
    .then(data => {
        let tbody = document.getElementById("todayAttendanceList");
        tbody.innerHTML = "";
        if (data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='7'>Bugün için yoklama verisi bulunamadı.</td></tr>";
            return;
        }
        data.forEach(student => {
            let row = `<tr class="text-center">
                <td>${student.ad} ${student.soyad}</td>
                <td>${student.veli_adi}</td>
                <td>${student.veli_telefon}</td>
                <td>${student.seans_turu}</td>
                <td>${student.seans_saati || 'Belirtilmemiş'}</td>
                <td><input type="checkbox" name="attendance_${student.id}" value="Geldi"></td>
                <td><input type="checkbox" name="attendance_${student.id}" value="Gelmedi"></td>
            </tr>`;
            tbody.innerHTML += row;
        });
        openAttendancePopup();
    })
    .catch(error => console.error("Hata:", error));
}

// Yoklamayı al butonuna tıklayınca (burada backend entegrasyonunu eklemeliyiz)
function submitTodayAttendance() {
    // Bu kısım, seçilen checkbox değerlerini toplamalı ve backend'e göndermeli.
    alert("Yoklama kaydedildi! (Backend entegrasyonu yapılmalı)");
    closeAttendancePopup();
}

// Event listener (butonlara bağlı)
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("btnTodayAttendance").addEventListener("click", loadTodayAttendance);
});

document.addEventListener("DOMContentLoaded", function() {
    fetch("/attendance")  // Flask API'den öğrenci listesini çekiyoruz
    .then(response => response.text()) 
    .then(html => {
        document.getElementById("attendanceTableBody").innerHTML = 
            new DOMParser().parseFromString(html, "text/html")
            .querySelector("#attendanceTableBody").innerHTML;
    })
    .catch(error => console.error("Hata:", error));
});




// Yazdır Butonu
function printAttendance() {
    window.print();
}
