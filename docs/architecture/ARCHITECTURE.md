# CropMind — Architecture for World Scale

## Design Principles

| Principle | Implementation |
|---|---|
| Offline first | On-device TFLite model (2 MB) runs with zero connectivity |
| Pay per use | Balance system — no subscriptions, debit per action |
| Global reach | 7 languages, PostGIS spatial queries, region-aware content |
| Zero to one cost | Fly.io free tier → paid only when revenue arrives |
| Lightweight | APK under 8 MB, API responses under 5 KB, gzipped |
| Defensible moat | Regional supplier DB + farm history grows with users |

---

## How It Scales to Go Viral

### Phase 1 — Zero cost (0 → 1,000 users)
```
Fly.io free tier (256 MB RAM, shared CPU)
  └─ FastAPI (1 worker)
  └─ PostgreSQL (Supabase free tier, 500 MB)
  └─ Redis (Upstash free tier, 10K req/day)
  └─ Ollama (self-hosted on same machine, Mistral 7B Q4)
  └─ Whisper-small (CPU, ~3s per minute of audio)

Cost: $0/month
Capacity: ~200 requests/day comfortably
```

### Phase 2 — First revenue (1K → 50K users)
```
Fly.io paid ($7/mo for dedicated CPU)
  └─ FastAPI (2 workers)
  └─ PostgreSQL (Fly Postgres, $5/mo)
  └─ Redis (Upstash $10/mo)
  └─ Ollama on separate 2GB VM ($10/mo)

Cost: ~$32/month
At 1,000 active users × 600 RWF avg/month → $480/mo revenue
Margin: ~93%
```

### Phase 3 — Hyper-growth (50K → 1M users)
```
Multi-region Fly.io (jnb, sin, iad)
  └─ FastAPI (auto-scale, 4-8 workers per region)
  └─ PostgreSQL (read replicas per region)
  └─ Redis Cluster (session + cache)
  └─ Ollama cluster (GPU instances for LLM)
  └─ CDN (Cloudflare free tier for static assets)
  └─ S3-compatible storage (Backblaze B2, ~$5/TB)

Cost: ~$300/month
At 50K users × 600 RWF avg/month → $24,000/mo revenue
```

### Phase 4 — B2B layer unlocks (post 100K users)
```
Dedicated outbreak heatmap API → $500/mo per govt client
Supplier listing API → $50/mo per agro-input company
NGO enrollment API → $2/farmer enrolled
Crop insurance verification → $1/claim

B2B can 10× the B2C revenue at near-zero marginal cost.
```

---

## Viral Loop Architecture

```
Farmer uses CropMind → saves harvest → tells neighbours
        ↓
Neighbour downloads → first scan is FREE (offline only)
        ↓
Neighbour wants treatment plan → tops up 500 RWF
        ↓
Farmer refers → earns 100 RWF credit per referral
        ↓
Community health champion earns enough to cover their own use
```

**The referral credit system is the flywheel.**
- A farmer who refers 5 friends earns 500 RWF = 1 free diagnosis
- A community champion who refers 50 earns 5,000 RWF = 8 free diagnoses
- Cost to CropMind: 100 RWF (< $0.10) per acquired user

---

## Data Architecture

### Write path (diagnosis)
```
Mobile → POST /api/v1/diagnose/enrich
  → Auth middleware (JWT)
  → Balance check (PostgreSQL)
  → LLM treatment plan (Ollama, async)
  → PostGIS supplier query
  → Market price lookup
  → Balance deduction (atomic UPDATE)
  → Diagnosis record INSERT
  → Celery task: update outbreak aggregate
  → Response to client
```

### Read path (history / heatmap)
```
Mobile → GET /api/v1/history
  → Auth middleware
  → PostgreSQL SELECT (indexed by user_id + created_at)
  → Redis cache (5 min TTL for repeated calls)
  → Response

B2B → GET /api/v1/outbreaks/heatmap
  → API key auth
  → PostGIS aggregate query (materialised view)
  → GeoJSON response
```

### Offline sync queue
```
Phone offline → capture image → local SQLite queue
Phone online  → Celery-like background sync
             → POST /api/v1/diagnose/enrich for each queued item
             → Update local SQLite with results
```

---

## Security Architecture

| Layer | Measure |
|---|---|
| Auth | JWT (HS256, 7-day expiry) + refresh token |
| Transport | TLS 1.3 (Nginx), HSTS |
| Rate limiting | Nginx: 60 req/min general, 10/min auth |
| Data at rest | PostgreSQL encrypted volumes (Fly.io) |
| Image storage | S3 presigned URLs (15-min TTL) |
| PII | Phone/email hashed in logs, not plain text |
| B2B keys | Separate API key table, scoped permissions |

---

## Database Schema (simplified)

```sql
users           -- auth, balance, preferences
farms           -- PostGIS point, crop types per user
diagnoses       -- core record: prediction, enrichment JSON, cost
suppliers       -- PostGIS point, products[], verified flag
balance_txns    -- full ledger: every debit/credit
outbreak_rpts   -- aggregated weekly, used for B2B heatmap
```

### Critical indexes
```sql
CREATE INDEX idx_diagnoses_user_created ON diagnoses(user_id, created_at DESC);
CREATE INDEX idx_suppliers_location ON suppliers USING GIST(location);
CREATE INDEX idx_diagnoses_location ON diagnoses USING GIST(location);
CREATE INDEX idx_outbreaks_disease_week ON outbreak_reports(disease, week_of);
```

---

## Internationalisation Strategy

Languages added in order of farmer population:
1. English (global default)
2. French (West + Central Africa, 250M farmers)
3. Swahili (East Africa, 200M speakers)
4. Kinyarwanda (Rwanda, pilot market)
5. Hausa (Nigeria + Niger, 80M speakers)
6. Amharic (Ethiopia, 50M speakers)
7. Portuguese (Brazil + Mozambique)

Adding a language = 1 JSON translation file + LLM prompt update.
LLM (Mistral 7B multilingual) handles the rest.

---

## Monetisation Layer

### Balance top-up flow
```
User → selects amount (500, 1000, 5000 RWF)
     → Stripe / MTN MoMo / Airtel Money / cash agent
     → Webhook → POST /api/v1/balance/topup
     → balance_rwf += amount
     → Transaction record

Deduction (per diagnosis):
     → Atomic: UPDATE users SET balance_rwf = balance_rwf - 600
     → If balance_rwf < 600: 402 Payment Required
     → Transaction record: type=DIAGNOSIS
```

### Pricing table
| Action | Cost (RWF) | Cost (USD) |
|---|---|---|
| On-device detection | 0 | $0 |
| Full enrichment (treatment + suppliers + price) | 600 | ~$0.50 |
| Voice Q&A (per minute) | 50 | ~$0.04 |
| Batch farm history export (PDF) | 200 | ~$0.17 |
| Share diagnosis with extension worker | 0 | $0 |

---

## Competitive Moat Over Time

```
Month 1-3  : Launch in Rwanda, 1,000 farmers
Month 4-6  : Supplier DB has 200+ verified listings (organic, community-driven)
Month 7-12 : Outbreak heatmap has 6 months of real data — first govt contract
Year 2     : Farm history DB has 100K+ diagnoses — training data for v2 model
Year 2     : v2 model trained on our own data → accuracy > Plantix
Year 3     : Regional supplier marketplace → suppliers pay for premium listings
Year 3     : Crop insurance integration → CropMind diagnosis = claim trigger
```

The data flywheel is unstoppable once it starts.
