import os
import datetime
from flask import Flask, render_template, request, redirect, url_for

# Google'ın Firestore veritabanı kütüphanelerini içe aktar
import firebase_admin
from firebase_admin import credentials, firestore

# --- Veritabanı Bağlantısı ---
# Cloud Run'da çalışırken, Google kimlik bilgilerini
# otomatik olarak (hizmet hesabından) alır.
try:
    firebase_admin.initialize_app()
except ValueError:
    pass # Zaten başlatılmışsa hata verme

# Firestore veritabanı istemcisini başlat
db = firestore.client()
# Fikirlerimizi saklayacağımız koleksiyonun (tablonun) adı
ideas_collection = db.collection('ideas')
# ------------------------------


app = Flask(__name__)

@app.route('/')
def index():
    """
    Ana sayfayı yükler ve TÜM fikirleri veritabanından çeker.
    Bu, sizin index.html'inizdeki 'ideas' değişkenini doldurur.
    """
    
    # Fikirleri veritabanından al, 'timestamp' (zaman damgası) alanına göre
    # en yeniden en eskiye (DESCENDING) doğru sırala.
    ideas_stream = ideas_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    # Gelen veriyi HTML'in anlayacağı bir listeye dönüştür
    ideas_list = []
    for idea in ideas_stream:
        idea_data = idea.to_dict() # Veriyi Python sözlüğüne çevir
        idea_data['id'] = idea.id    # Her fikrin kendi kimliğini de ekle
        ideas_list.append(idea_data)

    # index.html'i aç ve 'ideas' değişkenini bu listeyle doldur
    return render_template('index.html', ideas=ideas_list)

@app.route('/add_idea', methods=['POST'])
def add_idea():
    """
    Formdan gelen yeni fikri alır ve veritabanına kaydeder.
    Bu, sizin formunuzdaki action="/add_idea" kısmını yakalar.
    """
    
    # Formdaki 'idea_text' adlı textarea'dan metni al
    text = request.form['idea_text']
    
    if text: # Metin boş değilse
        # Veritabanına kaydedilecek veriyi hazırla
        data = {
            'text': text,
            'timestamp': datetime.datetime.now(datetime.timezone.utc) # Sıralama için zaman damgası
        }
        # Fikri 'ideas' koleksiyonuna ekle
        ideas_collection.add(data)
    
    # İşlem bittikten sonra kullanıcıyı ana sayfaya geri yönlendir
    return redirect(url_for('index'))

# Dockerfile'ımızın Gunicorn ile kullanacağı kısım
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)