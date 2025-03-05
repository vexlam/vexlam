from flask import Flask
from app.db_models import get_db_connection  # db_models.py artık "app" içinde

def create_app():
    """ Flask uygulamasını başlatır ve veritabanı bağlantısını kontrol eder. """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'  

    with app.app_context():
        conn = get_db_connection()
        conn.close()  

    return app

# 📌 Flask Uygulamasını Başlat
app = create_app()