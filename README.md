# SAYT (Django)

Bu loyiha Django asosidagi veb-sayt va admin panel. Loyihada yangiliklar, galereya, tinglovchilar, xodimlar, kurslar, jurnal va hujjatlar boshqaruvi mavjud.

## Texnologiyalar
- Python 3.10+
- Django 4.2
- Pandas + OpenPyXL (Excel import/export)
- Pillow (media rasmlar)
- WhiteNoise (static fayllar)

## Loyihani ishga tushirish
1. Virtual muhit yarating:
```bash
python -m venv venv
```

2. Virtual muhitni yoqing:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Kutubxonalarni ornating:
```bash
pip install -r requirements.txt
```

4. Migratsiyalarni ishga tushiring:
```bash
python manage.py migrate
```

5. Superuser yarating:
```bash
python manage.py createsuperuser
```

6. Serverni ishga tushiring:
```bash
python manage.py runserver
```

7. Brauzerda oching:
- Sayt: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Muhim sozlamalar
`markaz_backend/settings.py` ichida asosiy sozlamalar:
- `DEBUG`
- `ALLOWED_HOSTS`
- `STATIC_ROOT`, `MEDIA_ROOT`

## Production uchun qisqa eslatma
- `DEBUG=False` qiling.
- `DJANGO_SECRET_KEY` ni environment variable orqali bering.
- `ALLOWED_HOSTS` ni domeningizga moslang.
- `collectstatic` ni ishga tushiring:
```bash
python manage.py collectstatic --noinput
```

## Foydali buyruqlar
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
