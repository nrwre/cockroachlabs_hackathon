# 🪳 Blackbox — the on-call copilot whose memory survives the outage

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

> An SRE incident-response agent whose memory is a globally-distributed, always-on
> **CockroachDB**. Named after the flight recorder — the box that survives the crash and
> holds the memory of what happened. **The agent that fixes outages can't have memory that
> goes down *during* an outage.** That's the whole idea.

Built for the **CockroachDB × AWS Hackathon — Build with Agentic Memory**.

---

## The problem

Production AI agents write constantly and fail hard. When an agent's memory goes offline it
doesn't degrade gracefully — it *stops*. An on-call agent is the sharpest example: the moment
you need it most (a regional outage) is exactly when a single-region memory store would be
down too.

## What Blackbox does

When an incident fires, the agent:

1. **Recalls** similar past incidents by semantic search over embeddings *(vector memory)*.
2. **Inspects** live system state read-only via the CockroachDB MCP Server *(operational memory)*.
3. **Records** every hypothesis and action to an append-only timeline *(working memory)*.
4. **Reasons** with Amazon Bedrock to propose a diagnosis + ranked runbook.
5. **Resolves**, then embeds the incident back into memory so it gets smarter over time
   *(the flywheel)*.

All three memory layers live in **one CockroachDB** — no separate vector store, no
consistency gap. Kill a region mid-incident and the agent keeps reasoning with its timeline
intact.

## Architecture

See **[DESIGN.md](./DESIGN.md)** for the full design (schema, agent tools, demo script,
build plan). High level:

```
alert → Lambda ingest → CockroachDB
                          ├── vector index      (recall past incidents)
                          ├── operational state (services, dependencies)
                          └── live timeline     (this incident)
agent (LangGraph) ── reasons via Amazon Bedrock ── acts via Lambda
        └── introspects via CockroachDB MCP (read-only)
        └── checks blast radius via ccloud CLI
```

## Tools used

### CockroachDB (3 of 4)
| Tool | How the agent uses it |
|---|---|
| **Distributed Vector Indexing** | Semantic recall of similar past incidents & runbooks |
| **Managed MCP Server** | Read-only introspection of live system-of-record state |
| **ccloud CLI** | Cluster/region health checks + the survivability demo |

### AWS
| Service | How it's used |
|---|---|
| **Amazon Bedrock** | Claude for reasoning; Titan v2 for embeddings |
| **AWS Lambda** | Serverless alert ingest + remediation executor |

## Project structure

```
.
├── DESIGN.md            # full design doc — start here
├── README.md
├── LICENSE              # Apache-2.0
├── requirements.txt
├── .env.example         # copy to .env and fill in (never committed)
├── db/
│   └── schema.sql       # the three memory layers
├── scripts/
│   └── init_db.py       # apply the schema to your cluster
└── src/
    └── blackbox/
        ├── config.py    # reads settings from the environment
        └── db.py        # CockroachDB connection helper
```

## Getting started

> Prerequisites: Python 3.11+, a CockroachDB Cloud cluster, and AWS Bedrock access.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
copy .env.example .env      # then edit .env with your real values

# 4. Create the schema in your cluster
python scripts/init_db.py
```

## Status

🚧 **Phase 0 — scaffolding.** Memory layer, agent core, and AWS wiring are in progress.
Follow the build plan in [DESIGN.md](./DESIGN.md).

## License

[Apache-2.0](./LICENSE).
