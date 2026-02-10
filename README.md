# Badiiy Ta'lim Markazi - Rasmiy Veb-Sayti

O'zbekiston Badiiy akademiyasi huzuridagi Badiiy ta'lim sohasida pedagog kadrlarni qayta tayyorlash va ularning malakasini oshirish markazi uchun to'liq funksional veb-sayt.

## 📋 Loyiha Tuzilmasi

```
SAYT/
├── Backend/           # Django REST Framework backend
│   ├── backend/       # Asosiy sozlamalar
│   ├── core/          # API va modellar
│   ├── media/         # Yuklangan fayllar
│   └── requirements.txt
│
└── frontend/          # React + TypeScript frontend
    ├── api/           # Backend API bilan bog'lanish
    ├── components/    # React komponentlar
    ├── context/       # Global state management
    ├── pages/         # Sahifalar
    └── package.json
```

## 🛠 Texnologiyalar

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - API
- **PostgreSQL** - Ma'lumotlar bazasi (ishlab chiqish uchun SQLite)
- **Pillow** - Rasm ishlash
- **WhiteNoise** - Statik fayllar
- **Jazzmin** - Admin panel dizayni

### Frontend
- **React 18** - UI kutubxonasi
- **TypeScript** - Tiplangan JavaScript
- **Vite** - Build tool
- **TailwindCSS** - CSS framework
- **Recharts** - Grafiklar
- **Lucide React** - Ikonkalar

## 🚀 O'rnatish va Ishga Tushirish

### 1. Repozitoriyani klonlash

```bash
git clone <repository-url>
cd SAYT
```

### 2. Backend O'rnatish

```bash
# Backend papkasiga o'tish
cd Backend

# Virtual muhit yaratish
python -m venv venv

# Virtual muhitni faollashtirish
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Migratsiyalarni bajarish
python manage.py migrate

# Admin foydalanuvchi yaratish
python manage.py createsuperuser

# Serverni ishga tushirish
python manage.py runserver 8000
```

Backend: `http://localhost:8000`
Admin Panel: `http://localhost:8000/admin/`

### 3. Frontend O'rnatish

Yangi terminal oching:

```bash
# Frontend papkasiga o'tish
cd frontend

# .env faylini yaratish
cp .env.example .env

# Paketlarni o'rnatish
npm install

# Development serverni ishga tushirish
npm run dev
```

Frontend: `http://localhost:5173`

## ⚙️ Muhit O'zgaruvchilari

### Backend (`Backend/.env`)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000/api
```

## 📱 Sayt Bo'limlari

| Bo'lim | Tavsifi |
|--------|---------|
| **Bosh sahifa** | Statistika, yangiliklar, ustozlar, galereya |
| **Markaz haqida** | Tarix va tuzilma |
| **Ilmiy jurnal** | Ilmiy maqolalar va jurnallar |
| **Tinglovchilar uchun** | O'quv materiallari |
| **Ochiq ma'lumotlar** | Hujjatlar va hisobotlar |
| **Reestr** | MO/QT hujjatlarni tekshirish |

## 🔐 Admin Panel

Django admin panel orqali boshqarish:

1. `http://localhost:8000/admin/` ga o'ting
2. Superuser login/parol bilan kiring
3. Boshqarish mumkin:
   - **Yangiliklar** - rasmlar bilan
   - **Galereya** - ko'p rasmli albomlar
   - **Ustozlar** - pedagoglar ro'yxati
   - **Kurslar** - malaka oshirish va qayta tayyorlash
   - **Hujjatlar** - yuklab olinadigan fayllar
   - **Tinglovchilar (Listener)** - MO/QT reestr
   - **Statistika** - raqamlar

## 📊 API Endpointlari

```
GET  /api/news/          - Yangiliklar
GET  /api/gallery/       - Galereya
GET  /api/teachers/      - Ustozlar
GET  /api/courses/       - Kurslar
GET  /api/documents/     - Hujjatlar
GET  /api/listeners/     - Tinglovchilar (reestr)
GET  /api/statistics/    - Statistika
GET  /api/search/?type=MO&number=123  - Reestr qidirish
```

## 🌐 Production Deploy

### Backend (Gunicorn + Nginx)
```bash
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

### Frontend (Build)
```bash
npm run build
# dist/ papkasini serverga yuklang
```

### Muhim sozlamalar
1. `DEBUG=False` qiling
2. `SECRET_KEY` yangilang
3. `ALLOWED_HOSTS` to'g'rilang
4. HTTPS sozlang
5. Statik fayllarni `collectstatic` bilan yig'ing

## 📝 Litsenziya

Bu loyiha maxsus litsenziya ostida. Ruxsatsiz foydalanish taqiqlanadi.

## 👥 Muallif

O'zbekiston Badiiy akademiyasi huzuridagi Badiiy ta'lim markazi

---

**Eslatma:** Ishlab chiqish uchun har ikkala serverni (backend va frontend) bir vaqtda ishga tushiring.
=======
