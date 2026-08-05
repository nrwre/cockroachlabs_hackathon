-- ═══════════════════════════════════════════════════════════════════════════
-- Blackbox schema — three memory layers, one CockroachDB, one transaction boundary
-- ═══════════════════════════════════════════════════════════════════════════
-- Apply with:  cockroach sql --url "$DATABASE_URL" -f db/schema.sql
-- or:          python scripts/init_db.py
--
-- LAYER 1  operational state   → services, incidents      (system of record)
-- LAYER 2  live timeline       → incident_events          (working memory)
-- LAYER 3  semantic long-term  → incident_memory, runbooks (vector recall)
-- ═══════════════════════════════════════════════════════════════════════════

-- ── Layer 1: operational state ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS services (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       STRING NOT NULL,
    region     STRING NOT NULL,
    depends_on UUID[]                       -- dependency graph → blast-radius reasoning
);

CREATE TABLE IF NOT EXISTS incidents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id  UUID REFERENCES services(id),
    title       STRING NOT NULL,
    severity    INT NOT NULL,               -- 1..4  (SEV1 = worst)
    status      STRING NOT NULL DEFAULT 'open',   -- open|investigating|mitigated|resolved
    opened_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

-- ── Layer 2: live timeline (append-only) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS incident_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor       STRING NOT NULL,            -- 'agent' | 'human:<name>'
    kind        STRING NOT NULL,            -- hypothesis|action|observation|resolution
    content     STRING NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_incident ON incident_events (incident_id, ts);

-- ── Layer 3: semantic long-term memory (the recall store + flywheel) ────────
-- Titan Text Embeddings v2 produce 1024-dimensional vectors.
CREATE TABLE IF NOT EXISTS incident_memory (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id       UUID REFERENCES incidents(id),
    symptom_text      STRING NOT NULL,
    symptom_embedding VECTOR(1024),
    root_cause        STRING,
    resolution        STRING,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS runbooks (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title     STRING NOT NULL,
    body      STRING NOT NULL,
    embedding VECTOR(1024)
);

-- ── Distributed vector indexes (fast semantic search at scale) ──────────────
CREATE VECTOR INDEX IF NOT EXISTS idx_memory_embedding  ON incident_memory (symptom_embedding);
CREATE VECTOR INDEX IF NOT EXISTS idx_runbook_embedding ON runbooks (embedding);
