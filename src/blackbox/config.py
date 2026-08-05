"""Central config: read settings from the environment (loaded from `.env`).

Nothing secret lives in this file — it only *reads* values you put in `.env`.
Import `settings` anywhere you need a connection string or model id.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load key=value pairs from a local `.env` file into the environment.
# In production (Lambda/ECS) these come from the platform instead, and this is a no-op.
load_dotenv()


def _require(name: str) -> str:
    """Return an env var, or fail loudly if it's missing — better than a confusing crash later."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


@dataclass(frozen=True)
class Settings:
    # CockroachDB
    database_url: str
    mcp_url: str
    # AWS / Bedrock
    aws_region: str
    bedrock_model_id: str
    bedrock_embed_model_id: str

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            database_url=_require("DATABASE_URL"),
            mcp_url=os.environ.get("COCKROACH_MCP_URL", "https://cockroachlabs.cloud/mcp"),
            aws_region=os.environ.get("AWS_REGION", "us-east-1"),
            bedrock_model_id=os.environ.get(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
            ),
            bedrock_embed_model_id=os.environ.get(
                "BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"
            ),
        )


# Loaded lazily so importing this module never crashes; call Settings.load() when you need it.
def get_settings() -> Settings:
    return Settings.load()
