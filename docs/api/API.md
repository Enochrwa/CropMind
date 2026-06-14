# CropMind API Reference v1

Base URL: `https://api.cropmind.app/api/v1`

All authenticated endpoints require: `Authorization: Bearer <token>`

---

## Authentication

### POST /auth/register
Create a new farmer account.
```json
// Request
{
  "phone": "+250780123456",       // or email
  "password": "mypassword",
  "full_name": "Jean Habimana",
  "language": "kin",              // en | fr | sw | kin | ha | am | pt
  "country_code": "RW",
  "region": "Musanze"
}

// Response 201
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": "...", "balance_rwf": 0, ... }
}
```

### POST /auth/login
```json
// Request
{ "identifier": "+250780123456", "password": "mypassword" }

// Response 200 — same as register
```

---

## Diagnosis

### POST /diagnose/enrich ⚡ costs 600 RWF
Submit device prediction for full server enrichment.
```json
// Request
{
  "device_prediction": "tomato_late_blight",
  "device_confidence": 0.91,
  "crop_type": "tomato",
  "latitude": -1.9441,
  "longitude": 30.0619,
  "language": "kin",
  "farm_id": "uuid (optional)"
}

// Response 200
{
  "diagnosis_id": "uuid",
  "is_enriched": true,
  "cost_rwf": 600,
  "balance_remaining": 1400.0,
  "result": {
    "disease_display_name": "Indwara y'inyanya irengeje igihe",
    "severity": "critical",
    "confidence": 0.91,
    "description": "...",
    "urgency_message": "Fata ingamba ubu...",
    "treatment_steps": [
      { "step": 1, "action": "...", "product": "Ridomil Gold", "timing": "Ubu" }
    ],
    "prevention_tips": ["...", "..."],
    "suppliers": [
      {
        "id": "uuid",
        "name": "Agro-Rwanda Musanze",
        "phone": "+250788000001",
        "whatsapp": "+250788000001",
        "distance_km": 2.4,
        "is_verified": true,
        "rating": 4.7
      }
    ],
    "market_prices": [
      { "crop": "tomato", "price_per_kg_rwf": 500, "price_per_kg_usd": 0.417, "market": "Musanze Market", "updated_at": "2025-06-01" }
    ]
  },
  "created_at": "2025-06-01T08:30:00Z"
}

// Error 402 — insufficient balance
{ "detail": "Insufficient balance. Need 600 RWF, have 200 RWF." }
```

### POST /diagnose/voice-question ⚡ costs 50 RWF/min
Send voice audio for AI agronomist Q&A.
```
Content-Type: multipart/form-data
Fields:
  audio       : file (webm/wav/m4a)
  diagnosis_id: string
  crop_type   : string
  disease_name: string
  region      : string

Response:
{
  "question": "Transcribed farmer question",
  "answer": "AI agronomist response in farmer's language",
  "language": "kin"
}
```

---

## Balance

### GET /balance/
```json
{ "balance_rwf": 1400.0, "user_id": "uuid" }
```

### POST /balance/topup
```json
// Request
{
  "amount_rwf": 2000,
  "payment_method": "stripe",
  "payment_reference": "pi_stripe_123"
}

// Response
{ "balance_rwf": 3400.0, "user_id": "uuid" }
```

### GET /balance/transactions?limit=20&offset=0
```json
[
  {
    "id": "uuid",
    "type": "diagnosis",
    "amount_rwf": -600,
    "balance_after": 1400.0,
    "description": "Diagnosis: Tomato Late Blight on tomato",
    "created_at": "2025-06-01T08:30:00Z"
  }
]
```

---

## History

### GET /history/?limit=20&offset=0
```json
[
  {
    "id": "uuid",
    "disease": "Tomato Late Blight",
    "crop": "tomato",
    "severity": "critical",
    "confidence": 0.91,
    "cost_rwf": 600,
    "created_at": "2025-06-01T08:30:00Z"
  }
]
```

---

## Outbreaks (B2B — requires API key)

### GET /outbreaks/heatmap?country=RW&days=30
```json
{
  "features": [
    {
      "disease": "tomato_late_blight",
      "crop": "tomato",
      "country": "RW",
      "region": "Musanze",
      "cases": 47,
      "severity_avg": 3.2,
      "centroid": { "type": "Point", "coordinates": [29.6, -1.5] },
      "week_of": "2025-05-26"
    }
  ],
  "total": 1,
  "period_days": 30
}
```

---

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Bad request / validation error |
| 401 | Invalid or expired token |
| 402 | Insufficient balance |
| 404 | Resource not found |
| 409 | Conflict (duplicate user) |
| 422 | Unprocessable entity |
| 429 | Rate limit exceeded |
| 500 | Server error |
