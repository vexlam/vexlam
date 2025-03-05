// Ödeme popup'ını aç
function openPaymentPopup() {
    document.getElementById("paymentPopup").style.display = "block";
}

// Ödeme popup'ını kapat
function closePaymentPopup() {
    document.getElementById("paymentPopup").style.display = "none";
}

// TC Kimlik Numarası girildiğinde öğrenci bilgilerini getir
function fetchStudentInfo() {
    let tc = document.getElementById("tc").value;

    if (tc.length === 11) {  // TC Kimlik numarası 11 hane olmalı
        fetch(`/get_student_by_tc/${tc}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("student_name").value = data.ad;
                    document.getElementById("student_surname").value = data.soyad;
                    document.getElementById("total_amount").value = data.kalan_odeme + " TL";
                } else {
                    alert("Öğrenci bulunamadı!");
                }
            })
            .catch(error => console.error("Hata:", error));
    }
}

// Ödeme kaydetme işlemi
function submitPayment() {
    let tc = document.getElementById("tc").value;
    let payment_amount = document.getElementById("payment_amount").value;

    if (!tc || !payment_amount) {
        alert("Lütfen tüm alanları doldurun!");
        return;
    }

    fetch('/submit_payment', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tc: tc, amount: payment_amount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Ödeme başarıyla kaydedildi!");
            closePaymentPopup();
        } else {
            alert("Ödeme başarısız oldu!");
        }
    })
    .catch(error => console.error("Hata:", error));


    document.getElementById("search_student").addEventListener("keyup", function() {
        let query = this.value;
    
        fetch(`/list_students?search=${query}`)
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");
            document.querySelector("tbody").innerHTML = doc.querySelector("tbody").innerHTML;
        })
        .catch(error => console.error("Hata:", error));
    });

    
    document.getElementById("search_student").addEventListener("keyup", function() {
        let query = this.value;
    
        fetch(`/list_students?search=${query}`)
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");
            document.querySelector("tbody").innerHTML = doc.querySelector("tbody").innerHTML;
        })
        .catch(error => console.error("Hata:", error));
    });
    

    function highlightSearch(query, text) {
        if (!query) return text;
        let regex = new RegExp(`(${query})`, "gi");
        return text.replace(regex, `<span style="background-color: yellow;">$1</span>`);
    }
    
    document.getElementById("search_student").addEventListener("keyup", function() {
        let query = this.value.toLowerCase();
    
        fetch(`/list_students?search=${query}`)
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");
            let tbody = doc.querySelector("tbody");
    
            tbody.querySelectorAll("td").forEach(td => {
                td.innerHTML = highlightSearch(query, td.textContent);
            });
    
            document.querySelector("tbody").innerHTML = tbody.innerHTML;
        })
        .catch(error => console.error("Hata:", error));
    });
    
    
}


function deleteStudent(studentId) {
    if (!confirm("Bu öğrenciyi silmek istediğinizden emin misiniz?")) {
        return;
    }

    fetch(`/delete_student/${studentId}`, {
        method: "DELETE",
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Silme işlemi başarılı:", data.message);
            document.getElementById(`student-row-${studentId}`).remove(); // Satırı kaldır
        } else {
            alert("Silme işlemi başarısız: " + data.message);
        }
    })
    .catch(error => console.error("Silme hatası:", error));
}



fetch('/add_student', {
    method: 'POST',
    body: new FormData(document.getElementById("add_student_form")),
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert("✅ Öğrenci başarıyla eklendi!");
        window.location.href = "/list_students";  // 🔄 Öğrenci listesini aç
    } else {
        alert("❌ Hata: " + data.message);
    }
});





document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("#seansForm").addEventListener("submit", function(event) {
        event.preventDefault();

        let selectedDays = Array.from(document.querySelector("#session_days").selectedOptions)
            .map(option => option.value);

        console.log("📌 Seçili Günler (JS):", selectedDays);

        if (selectedDays.length === 0) {
            alert("⚠️ Lütfen en az bir gün seçin!");
            return;
        }

        let payload = {
            session_name: document.querySelector("#session_name").value,
            session_date: document.querySelector("#session_date").value,
            session_time: document.querySelector("#session_time").value,
            session_fee: document.querySelector("#session_fee").value,
            session_count: document.querySelector("#session_count").value,
            session_days: selectedDays  // JSON formatında gönder
        };

        fetch("/add_seans", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("✅ Seans başarıyla eklendi!", data);
                fetchSeansList();  
                this.reset();
            } else {
                alert("⚠️ Seans eklenirken hata oluştu: " + data.message);
            }
        })
        .catch(error => console.error("⚠️ Hata:", error));
    });

    fetchSeansList();
});





