document.addEventListener("DOMContentLoaded", function () {
    var calendarEl = document.getElementById("calendar");

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "tr",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek"
        },
        events: "/api/seanslar",  // API'den seansları çek
        eventClick: function (info) {
            fetch(`/api/ogrenciler/${info.event.id}`)
                .then(response => response.json())
                .then(data => {
                    let studentList = "<h5>📋 Katılımcılar:</h5><ul>";
                    data.forEach(student => {
                        let status = student.devamsizlik > 0 ? "🔴" : "🟢";
                        studentList += `<li>${status} ${student.ad} ${student.soyad}</li>`;
                    });
                    studentList += "</ul>";
                    document.getElementById("eventDetails").innerHTML = studentList;
                    new bootstrap.Modal(document.getElementById("eventModal")).show();
                });
        }
    });

    calendar.render();
});
