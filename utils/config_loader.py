from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or (
            Path(__file__).resolve().parents[1] / "config" / "config.yaml"
        )

    def load_config(self) -> dict[str, Any]:
        try:
            with self.config_path.open(encoding="utf-8") as config_file:
                config = yaml.safe_load(config_file)
        except yaml.YAMLError as error:
            raise ValueError(
                f"Invalid YAML configuration in {self.config_path}"
            ) from error

        if not isinstance(config, dict):
            raise ValueError(f"Expected a YAML mapping in {self.config_path}")
        return config