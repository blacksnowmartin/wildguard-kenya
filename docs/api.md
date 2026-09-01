# WildGuard Kenya - API Documentation

Complete REST API reference for WildGuard Kenya backend. Base URL: `http://localhost:8000`

## Authentication

All endpoints except `/api/health/` require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Obtain JWT Token

**Request:**
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "demo_grace_kisumu",
  "password": "password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Status Codes:**
- `200 OK` - Token successfully created
- `401 UNAUTHORIZED` - Invalid credentials

---

### Refresh Token

**Request:**
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Get Current User

**Request:**
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 5,
  "username": "demo_grace_kisumu",
  "email": "",
  "first_name": "Grace",
  "last_name": "Kisumu",
  "role": "COMMUNITY_MEMBER",
  "phone_number": "+254712345005",
  "is_active": true
}
```

---

## Health Check

**Request:**
```http
GET /api/health/
```

**Response:**
```json
{
  "status": "ok",
  "service": "wildguard-api"
}
```

**Status Codes:**
- `200 OK` - Service is running
- `503 SERVICE UNAVAILABLE` - Database connection failed

---

## Incidents

### List Incidents

**Request:**
```http
GET /api/incidents/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - Filter by status (REPORTED, VERIFIED, DISPATCHED, etc.)
- `risk_level` - Filter by risk level (LOW, MODERATE, HIGH, CRITICAL)
- `community_id` - Filter by community ID
- `page` - Page number (pagination)

**Response:**
```json
[
  {
    "id": 1,
    "species": {
      "id": 1,
      "name": "Elephant",
      "danger_factor": 75
    },
    "community": {
      "id": 1,
      "name": "Mara North",
      "county": "Narok"
    },
    "reporter": {
      "id": 5,
      "username": "demo_grace_kisumu",
      "role": "COMMUNITY_MEMBER"
    },
    "description": "Large herd of 8 elephants reported within 500m of cultivated land",
    "animal_count": 8,
    "severity": "CRITICAL",
    "status": "REPORTED",
    "event_time": "2026-09-01T14:00:00Z",
    "verified": false,
    "risk_score": 95,
    "risk_level": "CRITICAL",
    "location": {
      "type": "Point",
      "coordinates": [35.30, -1.35]
    },
    "created_at": "2026-09-01T14:15:00Z",
    "updated_at": "2026-09-01T14:15:00Z"
  }
]
```

**Status Codes:**
- `200 OK` - Successfully retrieved incidents
- `401 UNAUTHORIZED` - Missing or invalid token
- `403 FORBIDDEN` - Insufficient permissions

---

### Create Incident

**Request:**
```http
POST /api/incidents/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "species": 1,
  "community": 1,
  "animal_count": 3,
  "severity": "HIGH",
  "description": "Herd of elephants near farmland",
  "event_time": "2026-09-01T14:30:00Z",
  "latitude": -1.35,
  "longitude": 35.30,
  "property_damage": true
}
```

**Required Fields:**
- `species` (int) - Wildlife species ID
- `community` (int) - Community ID
- `severity` (string) - One of: LOW, MODERATE, HIGH, CRITICAL
- `description` (string) - Incident description
- `event_time` (ISO 8601) - When incident occurred
- `latitude` (float) - GPS latitude
- `longitude` (float) - GPS longitude
- `animal_count` (int) - Number of animals, default: 1
- `property_damage` (bool) - Whether property was damaged

**Response:**
```json
{
  "id": 8,
  "species": {
    "id": 1,
    "name": "Elephant",
    "danger_factor": 75
  },
  "community": {
    "id": 1,
    "name": "Mara North",
    "county": "Narok"
  },
  "reporter": {
    "id": 5,
    "username": "demo_grace_kisumu",
    "role": "COMMUNITY_MEMBER"
  },
  "description": "Herd of elephants near farmland",
  "animal_count": 3,
  "severity": "HIGH",
  "status": "REPORTED",
  "event_time": "2026-09-01T14:30:00Z",
  "verified": false,
  "risk_score": 65,
  "risk_level": "HIGH",
  "location": {
    "type": "Point",
    "coordinates": [35.30, -1.35]
  },
  "created_at": "2026-09-01T14:45:00Z",
  "updated_at": "2026-09-01T14:45:00Z"
}
```

**Status Codes:**
- `201 CREATED` - Incident successfully created
- `400 BAD REQUEST` - Invalid input data
- `401 UNAUTHORIZED` - Missing or invalid token
- `403 FORBIDDEN` - User cannot report incidents

---

### Get Incident Detail

**Request:**
```http
GET /api/incidents/{id}/
Authorization: Bearer <access_token>
```

**Response:** Same as list incidents response structure

**Status Codes:**
- `200 OK` - Successfully retrieved incident
- `401 UNAUTHORIZED` - Missing or invalid token
- `404 NOT FOUND` - Incident does not exist

---

### Update Incident Status

**Request:**
```http
PATCH /api/incidents/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "UNDER_REVIEW",
  "notes": "Initial review - appears valid"
}
```

**Fields:**
- `status` (string) - New status
- `notes` (string, optional) - Optional notes about the change

**Valid Status Transitions:**
```
REPORTED → UNDER_REVIEW
UNDER_REVIEW → VERIFIED or REJECTED
VERIFIED → DISPATCHED
DISPATCHED → RESPONDING
RESPONDING → RESOLVED
RESOLVED → CLOSED
```

**Response:** Updated incident object (same structure as detail response)

**Status Codes:**
- `200 OK` - Status successfully updated
- `400 BAD REQUEST` - Invalid status or invalid transition
- `401 UNAUTHORIZED` - Missing or invalid token
- `403 FORBIDDEN` - User cannot update this incident
- `404 NOT FOUND` - Incident does not exist

---

### Trigger Incident Action

**Request:**
```http
POST /api/incidents/{id}/action/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "action": "review"
}
```

**Available Actions:**
- `review` - Transition to UNDER_REVIEW
- `verify` - Transition to VERIFIED
- `reject` - Transition to REJECTED
- `dispatch` - Transition to DISPATCHED
- `respond` - Transition to RESPONDING
- `resolve` - Transition to RESOLVED
- `close` - Transition to CLOSED

**Response:** Updated incident object

**Status Codes:**
- `200 OK` - Action successfully executed
- `400 BAD REQUEST` - Invalid action or invalid transition
- `401 UNAUTHORIZED` - Missing or invalid token
- `403 FORBIDDEN` - User lacks permission for action
- `404 NOT FOUND` - Incident does not exist

---

## Alerts

### List Alerts

**Request:**
```http
GET /api/alerts/
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "incident": {
      "id": 1,
      "species": {
        "id": 1,
        "name": "Elephant",
        "danger_factor": 75
      },
      "community": {
        "id": 1,
        "name": "Mara North",
        "county": "Narok"
      },
      "reporter": {
        "id": 5,
        "username": "demo_grace_kisumu",
        "role": "COMMUNITY_MEMBER"
      },
      "description": "Large herd of 8 elephants...",
      "animal_count": 8,
      "severity": "CRITICAL",
      "status": "REPORTED",
      "event_time": "2026-09-01T14:00:00Z",
      "verified": false,
      "risk_score": 95,
      "risk_level": "CRITICAL",
      "location": {
        "type": "Point",
        "coordinates": [35.30, -1.35]
      },
      "created_at": "2026-09-01T14:15:00Z",
      "updated_at": "2026-09-01T14:15:00Z"
    },
    "title": "CRITICAL HWC INCIDENT",
    "message": "Elephant incident at Mara North has reached a critical risk score of 95/100.",
    "priority": "CRITICAL",
    "created_at": "2026-09-01T14:15:00Z"
  }
]
```

**Status Codes:**
- `200 OK` - Successfully retrieved alerts
- `401 UNAUTHORIZED` - Missing or invalid token

---

## Notifications

### List Notifications

**Request:**
```http
GET /api/notifications/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `read` - Filter by read status (true/false)

**Response:**
```json
[
  {
    "id": 1,
    "alert": {
      "id": 1,
      "incident": {...},
      "title": "CRITICAL HWC INCIDENT",
      "message": "Elephant incident at Mara North...",
      "priority": "CRITICAL",
      "created_at": "2026-09-01T14:15:00Z"
    },
    "read_at": null,
    "created_at": "2026-09-01T14:15:00Z"
  }
]
```

---

### Mark Notification as Read

**Request:**
```http
POST /api/notifications/{id}/read/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "alert": {...},
  "read_at": "2026-09-01T14:20:00Z",
  "created_at": "2026-09-01T14:15:00Z"
}
```

**Status Codes:**
- `200 OK` - Notification marked as read
- `401 UNAUTHORIZED` - Missing or invalid token
- `404 NOT FOUND` - Notification does not exist

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description",
  "error_code": "OPTIONAL_CODE"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Request successful |
| `201 CREATED` | Resource created successfully |
| `400 BAD REQUEST` | Invalid input data |
| `401 UNAUTHORIZED` | Missing or invalid authentication token |
| `403 FORBIDDEN` | Authenticated but lacks permission |
| `404 NOT FOUND` | Resource not found |
| `405 METHOD NOT ALLOWED` | HTTP method not allowed for endpoint |
| `500 INTERNAL SERVER ERROR` | Server error |
| `503 SERVICE UNAVAILABLE` | Database or service unavailable |

---

## Data Types & Validation

### Severity & Risk Level
- Values: `LOW`, `MODERATE`, `HIGH`, `CRITICAL`

### Incident Status
- `REPORTED` - Initial report received
- `UNDER_REVIEW` - Being reviewed by supervisor
- `VERIFIED` - Confirmed as valid incident
- `REJECTED` - Determined to be invalid
- `DISPATCHED` - Ranger team dispatched
- `RESPONDING` - Ranger actively responding
- `RESOLVED` - Incident resolved
- `CLOSED` - Incident finalized

### User Roles
- `COMMUNITY_MEMBER` - Can report incidents
- `RANGER` - Can respond to incidents
- `SUPERVISOR` - Can verify and dispatch incidents
- `ADMIN` - Full system access

### Geographic Coordinates
- Latitude: -34.8 to 5.0 (Kenya bounds)
- Longitude: 23.0 to 41.9 (Kenya bounds)
- Format: GeoJSON Point with WGS84 (SRID 4326)

---

## Example Workflows

### Community Member Reports Incident

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_grace_kisumu","password":"password"}' \
  | jq -r '.access')

# 2. Create incident
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "species": 1,
    "community": 1,
    "animal_count": 5,
    "severity": "HIGH",
    "description": "Elephant herd near village",
    "event_time": "2026-09-01T14:30:00Z",
    "latitude": -1.35,
    "longitude": 35.30,
    "property_damage": true
  }'
```

### Supervisor Reviews and Verifies

```bash
# 1. Get supervisor token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_alex_mwangi","password":"password"}' \
  | jq -r '.access')

# 2. Review incident
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "review"}'

# 3. Verify incident
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "verify"}'
```

### Ranger Dispatched and Responds

```bash
# 1. Get ranger token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_jane_kipchoge","password":"password"}' \
  | jq -r '.access')

# 2. Respond to incident
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "respond"}'

# 3. Resolve incident
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "resolve"}'
```

---

## Rate Limiting

Currently not implemented. Will be added in security hardening phase.

## CORS

CORS is enabled for `http://localhost:5173` (frontend development server).

Update `CORS_ALLOWED_ORIGINS` in `.env` for production deployments.

---

## Pagination

List endpoints return all results by default. Pagination will be added for large datasets.

---

## Versioning

Current API version: `1.0.0`
No version prefix in URLs (will be added if breaking changes needed)

---

**Last Updated**: 2026-09-01
**API Status**: Stable for Phase 2-3 features
