# 📡 API Dokumentation

Base URL: `http://localhost:8000/api/v1/`

## Authentifizierung

Die API verwendet Token-basierte Authentifizierung. Nach dem Login erhalten Sie einen Token, der bei jedem Request mitgesendet werden muss.

```bash
Authorization: Token <your-token>
```

---

## 🔐 Authentication Endpoints

### Registrierung

**POST** `/auth/register/`

Erstellt einen neuen Benutzer und sendet eine Verifikations-E-Mail.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "Max",
  "last_name": "Mustermann",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "Registrierung erfolgreich. Bitte überprüfen Sie Ihre E-Mails zur Verifizierung.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann",
    "is_verified_email": false
  }
}
```

---

### Login

**POST** `/auth/login/`

Meldet einen Benutzer an und gibt einen Authentifizierungs-Token zurück.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann",
    "is_verified_email": true
  }
}
```

**Error (400):**
```json
{
  "non_field_errors": ["Ungültige Anmeldedaten."]
}
```

---

### Logout

**POST** `/auth/logout/`

Meldet den Benutzer ab und löscht den Token.

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "message": "Erfolgreich abgemeldet."
}
```

---

### E-Mail Verifizierung

**POST** `/auth/verify-email/`

Verifiziert die E-Mail-Adresse eines Benutzers.

**Request Body:**
```json
{
  "token": "verification-token-from-email"
}
```

**Response (200):**
```json
{
  "message": "E-Mail erfolgreich verifiziert."
}
```

---

## 🛍 Product Endpoints

### Liste aller Produkte

**GET** `/products/`

**Query Parameters:**
- `available` (optional): `true` oder `false` (default: `true`)

**Response (200):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "sku": "BR-001",
      "name": "Bauernbrot",
      "description": "Rustikales Bauernbrot aus regionalen Zutaten",
      "price_cents": 350,
      "price_euro": "3.50",
      "available": true,
      "max_per_order": 5,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### Produkt-Details

**GET** `/products/{sku}/`

**Response (200):**
```json
{
  "id": 1,
  "sku": "BR-001",
  "name": "Bauernbrot",
  "description": "Rustikales Bauernbrot aus regionalen Zutaten",
  "price_cents": 350,
  "price_euro": "3.50",
  "available": true,
  "max_per_order": 5,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## 🛒 Order Endpoints

**Authentifizierung erforderlich für alle Order-Endpoints**

### Bestellung erstellen

**POST** `/orders/`

Erstellt eine neue Bestellung im Status "DRAFT".

**Headers:**
```
Authorization: Token abc123...
```

**Request Body:**
```json
{
  "items": [
    {
      "sku": "BR-001",
      "quantity": 2
    },
    {
      "sku": "CK-001",
      "quantity": 1
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 42,
  "user": 1,
  "user_email": "user@example.com",
  "status": "DRAFT",
  "total_cents": 1950,
  "total_euro": "19.50",
  "placed_at": null,
  "exported_at": null,
  "created_at": "2025-01-20T14:22:00Z",
  "updated_at": "2025-01-20T14:22:00Z",
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Bauernbrot",
      "product_sku": "BR-001",
      "quantity": 2,
      "unit_price_cents": 350,
      "subtotal_cents": 700,
      "subtotal_euro": "7.00"
    },
    {
      "id": 2,
      "product": 5,
      "product_name": "Schokoladenkuchen",
      "product_sku": "CK-001",
      "quantity": 1,
      "unit_price_cents": 1250,
      "subtotal_cents": 1250,
      "subtotal_euro": "12.50"
    }
  ]
}
```

**Error (400):**
```json
{
  "items": [
    {
      "sku": ["Produkt mit SKU 'INVALID' existiert nicht."]
    }
  ]
}
```

---

### Meine Bestellungen

**GET** `/orders/`

Gibt alle Bestellungen des authentifizierten Benutzers zurück.

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "user": 1,
      "user_email": "user@example.com",
      "status": "PLACED",
      "total_cents": 1950,
      "total_euro": "19.50",
      "placed_at": "2025-01-20T14:25:00Z",
      "exported_at": null,
      "created_at": "2025-01-20T14:22:00Z",
      "updated_at": "2025-01-20T14:25:00Z",
      "items": [...]
    }
  ]
}
```

---

### Bestellung abrufen

**GET** `/orders/{id}/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "id": 42,
  "user": 1,
  "user_email": "user@example.com",
  "status": "PLACED",
  "total_cents": 1950,
  "total_euro": "19.50",
  "placed_at": "2025-01-20T14:25:00Z",
  "exported_at": null,
  "created_at": "2025-01-20T14:22:00Z",
  "updated_at": "2025-01-20T14:25:00Z",
  "items": [...]
}
```

---

### Bestellung aufgeben

**POST** `/orders/{id}/place/`

Ändert den Status von "DRAFT" zu "PLACED" und setzt `placed_at`.

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "id": 42,
  "status": "PLACED",
  "placed_at": "2025-01-20T14:25:00Z",
  ...
}
```

**Error (400):**
```json
{
  "error": "Order cannot be placed. Current status: PLACED"
}
```

---

### Bestellung stornieren

**POST** `/orders/{id}/cancel/`

Ändert den Status zu "CANCELLED" (nur möglich, wenn noch nicht exportiert).

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "id": 42,
  "status": "CANCELLED",
  ...
}
```

**Error (400):**
```json
{
  "error": "Exported orders cannot be cancelled"
}
```

---

## 🔧 Admin / Export Endpoints

**Nur für Staff-Benutzer (is_staff=True)**

### Export ausführen

**POST** `/admin/export/run/`

Triggert den Export-Prozess manuell.

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
{
  "id": 15,
  "run_at": "2025-01-20T15:00:00Z",
  "orders_exported": 3,
  "status": "OK",
  "details": "Successfully exported 3 orders to export_orders_20251120_150000.csv"
}
```

---

### Export-Logs

**GET** `/admin/export/logs/`

Gibt die letzten 50 Export-Logs zurück.

**Headers:**
```
Authorization: Token abc123...
```

**Response (200):**
```json
[
  {
    "id": 15,
    "run_at": "2025-01-20T15:00:00Z",
    "orders_exported": 3,
    "status": "OK",
    "details": "Successfully exported 3 orders..."
  },
  {
    "id": 14,
    "run_at": "2025-01-19T04:00:00Z",
    "orders_exported": 5,
    "status": "OK",
    "details": "..."
  }
]
```

---

## 📊 Status Codes

| Code | Bedeutung |
|------|-----------|
| 200 | OK - Request erfolgreich |
| 201 | Created - Ressource erstellt |
| 400 | Bad Request - Ungültige Daten |
| 401 | Unauthorized - Authentifizierung erforderlich |
| 403 | Forbidden - Keine Berechtigung |
| 404 | Not Found - Ressource nicht gefunden |
| 500 | Internal Server Error |

---

## 🧪 Beispiel-Requests mit curl

### Registrierung
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

### Produkte abrufen
```bash
curl http://localhost:8000/api/v1/products/
```

### Bestellung erstellen
```bash
TOKEN="your-token-here"

curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{
    "items": [
      {"sku": "BR-001", "quantity": 2},
      {"sku": "CK-001", "quantity": 1}
    ]
  }'
```

### Bestellung aufgeben
```bash
ORDER_ID=42

curl -X POST http://localhost:8000/api/v1/orders/$ORDER_ID/place/ \
  -H "Authorization: Token $TOKEN"
```

---

## 🔍 API Testing Tools

**Empfohlene Tools:**
- **curl** - Kommandozeile
- **Postman** - GUI Client
- **HTTPie** - Benutzerfreundliche CLI
- **Insomnia** - REST Client

**Postman Collection:**
Importieren Sie die API-Endpoints in Postman für einfaches Testing.

---

## 📝 Notes

- Alle Timestamps sind in UTC (ISO 8601 Format)
- Preise werden in Cent gespeichert (Integer)
- Paginierung: 50 Items pro Seite (konfigurierbar)
- Rate-Limiting: 5 Fehlversuche pro Stunde (Login)
