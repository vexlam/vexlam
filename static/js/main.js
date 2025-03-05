// ✅ Silme işlemi için doğrulama ekranı
function confirmDelete(studentId) {
    if (confirm("Bu öğrenciyi silmek istediğinizden emin misiniz?")) {
        deleteStudent(studentId);
    }
}

// ✅ Öğrenciyi veritabanından sil ve tabloyu güncelle
function deleteStudent(studentId) {
    fetch(`/delete_student/${studentId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("✅ Silme işlemi başarılı:", data.message);
            document.getElementById(`student-row-${studentId}`).remove(); // HTML'den satırı kaldır
        } else {
            alert("❌ Silme işlemi başarısız: " + data.message);
        }
    })
    .catch(error => console.error('⚠️ Silme hatası:', error));
}
