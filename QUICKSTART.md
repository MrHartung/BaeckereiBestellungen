# Quick Start Guide

## 🚀 Schnellstart für Entwickler

### 1. Setup (5 Minuten)

```bash
# Repository klonen
git clone <repo-url>
cd BaeckerPJ

# Virtual Environment
python -m venv venv
.\venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Environment
copy .env.example .env

# Datenbank & Beispieldaten
python manage.py migrate
python manage.py load_sample_data
```

### 2. Server starten

```bash
python manage.py runserver
```

Öffne: http://localhost:8000

### 3. Login

**User:** test@example.com / testpass1234  
**Admin:** admin@example.com / admin1234567890

---

## 🐳 Docker Schnellstart

```bash
# Development starten
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Beispieldaten laden
docker-compose exec web python manage.py load_sample_data
```

Öffne: http://localhost:8080

---

## 📝 Wichtige Commands

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Tests
pytest

# Export simulieren
python manage.py export_orders --dry-run

# Django Shell
python manage.py shell
```

---

## 🔗 Wichtige URLs

- **Frontend:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **API:** http://localhost:8000/api/v1/
- **API Docs:** http://localhost:8000/api/v1/ (im Browser)

---

## 🎯 Nächste Schritte

1. ✅ README.md durchlesen
2. ✅ Tests ausführen: `pytest`
3. ✅ Frontend erkunden
4. ✅ Admin-Interface testen
5. ✅ API-Endpoints testen (mit Postman/curl)
6. ✅ Export-Command testen

---

## ❓ Hilfe

Siehe **README.md** für ausführliche Dokumentation und **DEPLOYMENT.md** für Production-Setup.
