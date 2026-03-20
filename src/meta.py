"""Provenance and failure metadata for generated Overpass QL entries.

Each generated output gets a companion .meta.json file.
Each failed attempt gets a not-found-{model_slug}.json file instead of
the legacy empty not-found.txt.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal


FailureReason = Literal["no_code_block", "too_many_lines", "zero_results", "api_error"]


def model_to_slug(model: str) -> str:
    """Convert a model name to a filesystem-safe slug.

    >>> model_to_slug("qwen2.5-coder:14b")
    'qwen2.5-coder-14b'
    >>> model_to_slug("gemma3:12b")
    'gemma3-12b'
    >>> model_to_slug("hf.co/org/model:latest")
    'hf.co-org-model-latest'
    """
    return model.replace(":", "-").replace("/", "-")


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GenerationMeta:
    """Provenance record written alongside each output-{slug}.overpassql."""

    model: str
    model_slug: str
    temperature: float
    num_predict: int
    generated_at: str
    element_count: int

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: str) -> GenerationMeta:
        with open(path) as f:
            return cls(**json.load(f))

    @classmethod
    def create(
        cls,
        *,
        model: str,
        temperature: float,
        num_predict: int,
        element_count: int,
    ) -> GenerationMeta:
        return cls(
            model=model,
            model_slug=model_to_slug(model),
            temperature=temperature,
            num_predict=num_predict,
            generated_at=now_iso(),
            element_count=element_count,
        )


@dataclass
class FailureMeta:
    """Failure record written as not-found-{slug}.json when generation fails."""

    model: str
    model_slug: str
    reason: FailureReason
    query: str | None
    generated_at: str

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: str) -> FailureMeta:
        with open(path) as f:
            data = json.load(f)
            data["reason"] = data["reason"]  # keep as-is; Literal checked at runtime
            return cls(**data)

    @classmethod
    def create(
        cls,
        *,
        model: str,
        reason: FailureReason,
        query: str | None = None,
    ) -> FailureMeta:
        return cls(
            model=model,
            model_slug=model_to_slug(model),
            reason=reason,
            query=query,
            generated_at=now_iso(),
        )
