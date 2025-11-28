# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0] - 2025-11-28

### 🎉 Initial Release

#### Added
- **Benutzer-Management**
  - Registrierung mit E-Mail-Verifikation
  - Login/Logout mit Token-Authentifizierung
  - Benutzerprofil-Ansicht
  - Rate-Limiting (django-axes)

- **Produkt-Management**
  - CRUD Operations für Produkte (Admin)
  - Produktkatalog mit Bootstrap UI
  - SKU-basierte Identifikation
  - Preisverwaltung in Cent
  - Max-per-Order Validierung

- **Bestellsystem**
  - Warenkorb-Funktionalität
  - Bestellung erstellen (DRAFT)
  - Bestellung aufgeben (PLACED)
  - Bestellung stornieren (CANCELLED)
  - Bestellhistorie
  - Order-Status-Tracking

- **REST API**
  - Django REST Framework Integration
  - Token-basierte Authentifizierung
  - Product Endpoints (GET)
  - Order Endpoints (CRUD)
  - Auth Endpoints (Register, Login, Logout)
  - Admin Export Endpoints

- **Export zu Access 97**
  - Management Command `export_orders`
  - CSV-Export-Funktionalität
  - Windows pyodbc Import-Script
  - Export-Log-Tracking
  - Dry-run Option

- **Admin Interface**
  - CustomUser Admin
  - Product Admin mit Euro-Preis-Anzeige
  - Order Admin mit Inline OrderItems
  - ExportLog Admin (read-only)
  - Bulk-Actions für Order-Recalculation

- **Frontend (Bootstrap 5)**
  - Responsive Design
  - Home Page
  - Registrierung & Login
  - Produktliste
  - Warenkorb
  - Checkout
  - Bestellhistorie
  - Bestelldetails
  - Profil-Seite

- **Docker & Deployment**
  - Multi-stage Dockerfile
  - docker-compose.yml (Production)
  - docker-compose.dev.yml (Development)
  - Nginx Reverse Proxy
  - PostgreSQL Container
  - Health Checks
  - Volume Management

- **CI/CD**
  - GitHub Actions Workflow
  - Linting (black, isort, flake8)
  - Testing (pytest)
  - Coverage Reporting
  - Docker Build

- **Tests**
  - Model Tests (pytest)
  - API Tests (DRF TestClient)
  - Auth Flow Tests
  - Order Placement Tests
  - Export Tests (Mock)

- **Dokumentation**
  - README.md (komplett)
  - QUICKSTART.md
  - DEPLOYMENT.md
  - API.md
  - CHANGELOG.md
  - Inline Code-Dokumentation

- **Scripts & Tools**
  - setup.bat (Windows Setup)
  - setup.sh (Linux/Mac Setup)
  - write_to_access.py (Windows ODBC Import)
  - load_sample_data Management Command

#### Security
- HTTPS/TLS Support (Nginx)
- CSRF Protection (Django built-in)
- Secure Cookies (HttpOnly, Secure)
- Security Headers (X-Frame-Options, etc.)
- Password Validation (min 10 chars)
- Email Verification required
- Rate Limiting (Login attempts)

#### Configuration
- Environment Variables (.env)
- Database: PostgreSQL (Prod) / SQLite (Dev)
- Email: SMTP (Prod) / Console (Dev)
- Static Files: Whitenoise + Nginx
- Media Files: Volume-mounted

---

## [Unreleased]

### Geplante Features

#### v1.1.0
- [ ] Passwort-Reset Funktionalität
- [ ] SFTP-Upload für Export-CSV
- [ ] Celery für async Tasks
- [ ] Redis für Caching
- [ ] User Dashboard mit Statistiken

#### v1.2.0
- [ ] PDF-Rechnungen generieren
- [ ] E-Mail-Benachrichtigungen bei Bestellstatus-Änderung
- [ ] Admin-Benachrichtigungen bei neuen Bestellungen
- [ ] Produktkategorien
- [ ] Produktbilder

#### v1.3.0
- [ ] OpenAPI/Swagger UI
- [ ] API Versionierung
- [ ] GraphQL API (optional)
- [ ] Webhook-Support für externe Systeme

#### v2.0.0
- [ ] Multi-Mandanten-Fähigkeit
- [ ] Abonnements/Wiederkehrende Bestellungen
- [ ] Rabatt-Codes
- [ ] Loyalty-Points System

### Known Issues

- Access 97 ODBC-Treiber kann auf neueren Windows-Versionen Probleme bereiten
- E-Mail-Verifikation-Link verwendet HTTP in Development (HTTPS in Prod erforderlich)
- Template-Filter für Cent→Euro könnte eleganter sein

---

## Versionierungsschema

**MAJOR.MINOR.PATCH**

- **MAJOR:** Breaking Changes, neue Haupt-Features
- **MINOR:** Neue Features, abwärtskompatibel
- **PATCH:** Bugfixes, kleine Verbesserungen

---

## Support

Bei Fragen oder Problemen öffnen Sie bitte ein Issue auf GitHub:
https://github.com/your-username/BaeckerPJ/issues

---

**Legende:**
- `Added` - Neue Features
- `Changed` - Änderungen an bestehenden Features
- `Deprecated` - Bald zu entfernende Features
- `Removed` - Entfernte Features
- `Fixed` - Bugfixes
- `Security` - Sicherheitsverbesserungen
