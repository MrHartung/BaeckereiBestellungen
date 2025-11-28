# 🥖 Bäckerei Bestellsystem

Eine vollständige Web-Anwendung für Bäckerei-Bestellungen mit automatischem Export zu Access 97-Datenbank.

## 📋 Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Features](#features)
- [Technologie-Stack](#technologie-stack)
- [Architektur](#architektur)
- [Installation & Setup](#installation--setup)
  - [Lokale Entwicklung](#lokale-entwicklung)
  - [Docker Deployment](#docker-deployment)
- [Konfiguration](#konfiguration)
- [Export zu Access 97](#export-zu-access-97)
- [API Dokumentation](#api-dokumentation)
- [Tests](#tests)
- [Deployment](#deployment)
- [Sicherheit](#sicherheit)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Übersicht

Das Bäckerei-Bestellsystem ermöglicht es Kunden, online Backwaren zu bestellen. Bestellungen werden in einer Django/PostgreSQL-Datenbank gespeichert und täglich automatisch in die Access 97-Datenbank des Bäckers exportiert.

### Projektziel

- Kunden können sich registrieren, Produkte bestellen und ihre Bestellhistorie einsehen
- Admin-Interface für Produktverwaltung und Export-Management
- REST API für Frontend und externe Integrationen
- Automatischer Export neuer Bestellungen zu Access 97 via VPN

---

## ✨ Features

### Kundenfunktionen
- ✅ Benutzerregistrierung mit E-Mail-Verifikation
- ✅ Login/Logout mit Session-Management
- ✅ Produktkatalog mit Suche und Filter
- ✅ Warenkorb-Funktionalität
- ✅ Bestellhistorie und Bestelldetails
- ✅ Benutzerprofil-Verwaltung

### Admin-Funktionen
- ✅ Django Admin für Produkte, Bestellungen, Benutzer
- ✅ Export-Verwaltung und Log-Ansicht
- ✅ Manueller Export-Trigger
- ✅ Bestellstatus-Management

### Technische Features
- ✅ RESTful API (Django REST Framework)
- ✅ E-Mail-Verifikation
- ✅ Rate-Limiting (django-axes)
- ✅ CSRF-Schutz
- ✅ Responsive Bootstrap UI
- ✅ Docker & docker-compose Support
- ✅ Nginx Reverse Proxy
- ✅ PostgreSQL Datenbank (SQLite für Dev)
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Unit & Integration Tests

---

## 🛠 Technologie-Stack

**Backend:**
- Python 3.11+
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15 (Production) / SQLite (Development)
- Gunicorn (WSGI Server)

**Frontend:**
- Bootstrap 5.3
- Vanilla JavaScript
- Django Templates

**Infrastructure:**
- Docker & docker-compose
- Nginx (Reverse Proxy)
- GitHub Actions (CI/CD)

**Export:**
- Windows Server mit pyodbc
- Access 97 ODBC Driver

---

## 🏗 Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       ▼
              ┌─────────────────┐
              │  Nginx (443)    │  ◄── TLS Termination
              │  Reverse Proxy  │
              └────────┬────────┘
                       │
                       │ HTTP
                       ▼
              ┌─────────────────┐
              │ Django + Gunic. │
              │   (Web App)     │  ◄── REST API + Templates
              └────────┬────────┘
                       │
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
    ┌──────────────┐   ┌──────────────┐
    │  PostgreSQL  │   │  Export CSV  │
    │  (Database)  │   │   /exports/  │
    └──────────────┘   └──────┬───────┘
                              │
                              │ VPN / SFTP
                              ▼
                    ┌──────────────────────┐
                    │   Windows Server     │
                    │  write_to_access.py  │
                    └──────────┬───────────┘
                               │
                               │ ODBC
                               ▼
                    ┌──────────────────────┐
                    │  Access 97 Database  │
                    │   (Bäcker-System)    │
                    └──────────────────────┘
```

---

## 🚀 Installation & Setup

### Voraussetzungen

- Python 3.11+
- Git
- Docker & docker-compose (für Containerisierung)
- Windows Server mit Access 97 Driver (für Export)

### Lokale Entwicklung

#### 1. Repository klonen

```bash
git clone https://github.com/your-username/BaeckerPJ.git
cd BaeckerPJ
```

#### 2. Virtual Environment erstellen

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

#### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

#### 4. Umgebungsvariablen konfigurieren

```bash
copy .env.example .env
# Bearbeiten Sie .env mit Ihren Einstellungen
```

Wichtige Variablen für Entwicklung:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=  # Leer lassen für SQLite
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### 5. Datenbank initialisieren

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py load_sample_data  # Optional: Beispieldaten laden
```

#### 6. Server starten

```bash
python manage.py runserver
```

Öffnen Sie http://localhost:8000 im Browser.

**Login-Credentials (nach load_sample_data):**
- User: `test@example.com` / `testpass1234`
- Admin: `admin@example.com` / `admin1234567890`

---

### Docker Deployment

#### 1. Umgebungsvariablen konfigurieren

```bash
copy .env.example .env
# Bearbeiten Sie .env für Production
```

Wichtige Production-Variablen:
```env
SECRET_KEY=long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@db:5432/dbname
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

#### 2. Container starten

**Development:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Production:**
```bash
docker-compose up -d --build
```

#### 3. Initialisierung

```bash
# Migrations ausführen
docker-compose exec web python manage.py migrate

# Superuser erstellen
docker-compose exec web python manage.py createsuperuser

# Static files sammeln
docker-compose exec web python manage.py collectstatic --noinput

# Beispieldaten laden (optional)
docker-compose exec web python manage.py load_sample_data
```

#### 4. Zugriff

- **Frontend:** http://localhost (Production) oder http://localhost:8080 (Dev)
- **Admin:** http://localhost/admin
- **API:** http://localhost/api/v1/

---

## ⚙️ Konfiguration

### Django Settings

Wichtige Einstellungen in `baecker/settings.py`:

```python
# Sicherheit (Production)
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Datenbank
DATABASE_URL = 'postgresql://user:pass@host:5432/dbname'

# E-Mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Export
EXPORT_CSV_PATH = '/app/exports'
```

### Nginx SSL/TLS (Production)

1. Let's Encrypt Zertifikat erstellen:

```bash
sudo certbot certonly --nginx -d your-domain.com
```

2. `nginx/conf.d/default.conf` anpassen (HTTPS-Block auskommentieren)

3. Nginx neustarten:

```bash
docker-compose restart nginx
```

---

## 📤 Export zu Access 97

### Überblick

Der Export-Workflow besteht aus zwei Schritten:

1. **Django Command:** Erzeugt CSV mit neuen Bestellungen
2. **Windows Script:** Importiert CSV in Access 97 Datenbank

### 1. Export Command ausführen

**Manuell:**
```bash
python manage.py export_orders
```

**In Docker:**
```bash
docker-compose exec web python manage.py export_orders
```

**Mit Optionen:**
```bash
# Dry-run (ohne Orders als exportiert zu markieren)
python manage.py export_orders --dry-run

# Export seit bestimmtem Zeitpunkt
python manage.py export_orders --since 2025-01-01T00:00:00
```

**Output:**
```
============================================================
  EXPORT ORDERS TO ACCESS DATABASE
============================================================

Found 3 order(s) to export:
  - Order #42 (customer@example.com) - 2 items
  - Order #43 (another@example.com) - 3 items

✓ CSV exported to: /app/exports/export_orders_20251128_040512.csv
✓ 3 order(s) marked as exported

============================================================
  EXPORT COMPLETED
============================================================

Next steps:
1. Transfer CSV file to Windows host via VPN
2. Run: python write_to_access.py export_orders_20251128_040512.csv
3. Verify import in Access database
```

### 2. Windows Import Script

**Setup auf Windows Server:**

1. Python installieren (3.11+)
2. pyodbc installieren:
   ```cmd
   pip install pyodbc
   ```
3. Access 97 ODBC Driver installieren (Microsoft Access Driver)
4. Script konfigurieren:

Bearbeiten Sie `scripts/write_to_access.py`:
```python
ACCESS_DB_PATH = r'\\server\share\baecker.mdb'
ACCESS_TABLE_NAME = 'Bestellungen'
```

**Ausführen:**
```cmd
python write_to_access.py export_orders_20251128_040512.csv
```

**Access-Tabellenschema:**
```sql
CREATE TABLE Bestellungen (
    ID AUTOINCREMENT PRIMARY KEY,
    order_id INTEGER,
    user_id INTEGER,
    user_email TEXT(255),
    user_first_name TEXT(100),
    user_last_name TEXT(100),
    sku TEXT(50),
    product_name TEXT(200),
    quantity INTEGER,
    unit_price_cents INTEGER,
    placed_at DATETIME,
    order_total_cents INTEGER,
    imported_at DATETIME
)
```

### 3. Automatisierung

**Option A: Windows Task Scheduler**

1. Task erstellen: täglich um 04:00 UTC
2. Aktion: `python C:\path\to\write_to_access.py <csv_file>`
3. VPN muss aktiv sein

**Option B: Cron Job (Linux mit VPN)**

```bash
# /etc/cron.d/baecker-export
0 4 * * * root docker-compose exec -T web python manage.py export_orders >> /var/log/export.log 2>&1
```

**Option C: Django-cron oder Celery Beat**

Installieren Sie `django-cron` oder `celery` für Python-basierte Scheduling.

---

## 📡 API Dokumentation

### Base URL

```
http://localhost:8000/api/v1/
```

### Authentication

Die API verwendet Token-basierte Authentifizierung:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response:
{
  "token": "abc123...",
  "user": { ... }
}

# Authenticated Request
curl http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Token abc123..."
```

### Endpoints

#### **Auth**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Benutzer registrieren |
| POST | `/auth/login/` | Login |
| POST | `/auth/logout/` | Logout |
| POST | `/auth/verify-email/` | E-Mail verifizieren |
| POST | `/auth/password-reset/` | Passwort zurücksetzen |

#### **Products**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | Alle Produkte auflisten |
| GET | `/products/{sku}/` | Produkt-Details |

**Filter:**
```bash
GET /products/?available=true
```

#### **Orders**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | Eigene Bestellungen |
| POST | `/orders/` | Neue Bestellung erstellen |
| GET | `/orders/{id}/` | Bestellung-Details |
| POST | `/orders/{id}/place/` | Bestellung aufgeben |
| POST | `/orders/{id}/cancel/` | Bestellung stornieren |

**Create Order Example:**
```json
POST /orders/
{
  "items": [
    {"sku": "BR-001", "quantity": 2},
    {"sku": "CK-001", "quantity": 1}
  ]
}
```

#### **Admin / Export** (Staff only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/export/run/` | Export manuell triggern |
| GET | `/admin/export/logs/` | Export-Logs anzeigen |

---

## 🧪 Tests

### Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=bestellungen --cov-report=html

# Spezifische Test-Datei
pytest bestellungen/tests/test_models.py

# Einzelner Test
pytest bestellungen/tests/test_models.py::TestOrder::test_place_order
```

### Test-Coverage anzeigen

```bash
pytest --cov=bestellungen --cov-report=html
open htmlcov/index.html  # oder start htmlcov\index.html (Windows)
```

### Linting & Code Quality

```bash
# Black (Code Formatter)
black .

# isort (Import Sorting)
isort .

# flake8 (Linter)
flake8 .
```

---

## 🚢 Deployment

### Production Checklist

- [ ] `DEBUG = False` in settings
- [ ] Starkes `SECRET_KEY` generieren
- [ ] `ALLOWED_HOSTS` konfigurieren
- [ ] PostgreSQL Datenbank einrichten
- [ ] SMTP E-Mail-Server konfigurieren
- [ ] SSL/TLS Zertifikat installieren (Let's Encrypt)
- [ ] Static Files sammeln
- [ ] Backups einrichten (DB + Media)
- [ ] Monitoring einrichten (Logs, Uptime)
- [ ] Rate-Limiting konfigurieren
- [ ] Firewall-Regeln setzen
- [ ] VPN zu Bäcker-Netzwerk testen

### Backup & Restore

**Datenbank Backup:**
```bash
# Backup
docker-compose exec db pg_dump -U baecker_user baecker_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U baecker_user baecker_db < backup_20251128.sql
```

**Volumes Backup:**
```bash
docker run --rm -v baeckerp_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### Monitoring

**Logs ansehen:**
```bash
# Alle Services
docker-compose logs -f

# Nur Web
docker-compose logs -f web

# Nur Nginx
docker-compose logs -f nginx
```

**Fehlersuche:**
```bash
# Container Status
docker-compose ps

# In Container einsteigen
docker-compose exec web bash

# Django Shell
docker-compose exec web python manage.py shell
```

---

## 🔒 Sicherheit

### Implementierte Sicherheitsmaßnahmen

✅ **Authentifizierung & Autorisierung:**
- Token-basierte API-Authentifizierung
- Session-basierte Web-Authentifizierung
- E-Mail-Verifikation erforderlich
- Passwort-Mindestlänge: 10 Zeichen
- Rate-Limiting: 5 Fehlversuche → 1h Sperre

✅ **Datenübertragung:**
- HTTPS/TLS in Production
- Secure Cookies (HttpOnly, Secure)
- HSTS Header
- CSRF-Schutz (Django built-in)

✅ **Headers & Policies:**
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: no-referrer-when-downgrade

✅ **Datenbank:**
- Prepared Statements (SQL Injection Prevention)
- Passwörter gehasht (PBKDF2)

### GDPR-Compliance

**Datenschutz-Anforderungen:**

1. **Datenminimierung:** Nur notwendige Daten sammeln
2. **Recht auf Auskunft:** Admin kann Benutzerdaten exportieren
3. **Recht auf Löschung:** Implementieren Sie:

```python
# Management Command für Datenlöschung
python manage.py delete_user_data --email user@example.com
```

4. **Datenschutzerklärung:** Erstellen und verlinken (siehe Footer)

### Security Checklist

- [ ] SSL/TLS aktiviert
- [ ] `DEBUG=False` in Production
- [ ] Starke Passwörter für DB/Admin
- [ ] Rate-Limiting aktiv
- [ ] Backups verschlüsselt
- [ ] Logs rotiert und geschützt
- [ ] Security Headers gesetzt
- [ ] Dependency Updates regelmäßig
- [ ] Penetration Tests durchführen

---

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. **Import Error: "Module not found"**

**Lösung:**
```bash
pip install -r requirements.txt
# oder in Docker:
docker-compose up --build
```

#### 2. **Database Connection Error**

**Symptom:** `django.db.utils.OperationalError: could not connect to server`

**Lösung:**
```bash
# Prüfen, ob PostgreSQL läuft
docker-compose ps db

# Logs ansehen
docker-compose logs db

# Database URL prüfen
echo $DATABASE_URL
```

#### 3. **Static Files nicht geladen**

**Lösung:**
```bash
python manage.py collectstatic --noinput
# oder in Docker:
docker-compose exec web python manage.py collectstatic --noinput
```

#### 4. **E-Mail-Versand schlägt fehl**

**Lösung:**
- Prüfen Sie `EMAIL_*` Variablen in `.env`
- Für Entwicklung: Console-Backend verwenden
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### 5. **Access 97 Import schlägt fehl**

**Häufige Ursachen:**
- ODBC-Treiber nicht installiert
- Falscher Pfad zu `.mdb`-Datei
- VPN-Verbindung nicht aktiv
- Berechtigungsprobleme

**Debugging:**
```python
# Test ODBC Connection
import pyodbc
print(pyodbc.drivers())  # Sollte "Microsoft Access Driver" enthalten
```

#### 6. **Permission Denied in Docker**

**Lösung:**
```bash
# Berechtigungen anpassen
chmod -R 755 exports/
chmod +x entrypoint.sh
```

---

## 📞 Support & Kontakt

**Dokumentation:**
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Docker: https://docs.docker.com/

**Issue Tracker:**
https://github.com/your-username/BaeckerPJ/issues

**Lizenz:**
MIT License - siehe LICENSE-Datei

---

## 🎉 Credits

Entwickelt mit:
- Django 4.2
- Django REST Framework
- Bootstrap 5
- PostgreSQL
- Docker

© 2025 Bäckerei Bestellsystem. Alle Rechte vorbehalten.
