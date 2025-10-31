# 1. Adım: Temel imaj olarak Python 3.10'un hafif (slim) versiyonunu kullan.
FROM python:3.10-slim

# 2. Adım: Konteyner içinde /app adında bir çalışma dizini oluştur.
WORKDIR /app

# 3. Adım: Önce sadece gereksinim dosyasını kopyala ve kur.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Adım: Geri kalan tüm proje dosyalarını (/app'in içine) kopyala.
COPY . .

# 5. Adım: (Gerekli değil ama kalabilir)
EXPOSE 8080

# 6. Adım: Gunicorn sunucusu ile uygulamayı başlat (SHELL FORM)
CMD gunicorn --bind 0.0.0.0:$PORT app:app