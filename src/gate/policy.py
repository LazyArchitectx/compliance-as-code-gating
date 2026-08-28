"""Load the gating policy from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from gate.schema import Policy


def load_policy(path: str | Path) -> Policy:
    return Policy.model_validate(yaml.safe_load(Path(path).read_text()))
