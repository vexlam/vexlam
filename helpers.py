import datetime

def format_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
    except ValueError:
        return date_str

def calculate_attendance_percentage(total_classes, attended_classes):
    if total_classes == 0:
        return 0
    return round((attended_classes / total_classes) * 100, 2)

def format_currency(amount):
    return f"{amount:.2f}₺"

def filter_students_by_payment(students, status='pending'):
    if status == 'pending':
        return [student for student in students if student['payment_due']]
    elif status == 'paid':
        return [student for student in students if not student['payment_due']]
    return students

def filter_sessions_by_capacity(sessions, status='available'):
    if status == 'full':
        return [session for session in sessions if session['capacity'] == 0]
    elif status == 'available':
        return [session for session in sessions if session['capacity'] > 0]
    return sessions

def validate_form_data(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return missing_fields
