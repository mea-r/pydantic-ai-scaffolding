import json
from os import path
from typing import Any, Dict, List
from pydantic import BaseModel, Field

class Defaults(BaseModel):
    model: str

class LimitConfig(BaseModel):
    per_model: Dict[str, int] = Field(default_factory=dict)
    per_service: Dict[str, int] = Field(default_factory=dict)

class Config(BaseModel):
    defaults: Defaults
    daily_limits: LimitConfig
    monthly_limits: LimitConfig
    model_mappings: Dict[str, str] = Field(default_factory=dict)
    excluded_models: List[str] = Field(default_factory=list)
    mode: str = Field(default='strict', description="Strict = don't allow any model that fail custom tool calling. Loose = allow models that fail tool calling but are still usable for other tasks.")

class ConfigHelper:
    def __init__(self):
        self.config_path = path.join(path.dirname(__file__), '../../config.json')
        if not path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        self.configuration = self._load()

    def _load(self) -> Config:
        with open(self.config_path, 'r') as f:
            return Config(**json.load(f))

    def _save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.configuration.model_dump(), f, indent=4)

    def get_config(self, key: str) -> Any:
        return getattr(self.configuration, key, None)

    def append_config(self, key: str, value: Any):
        setattr(self.configuration, key, value)
        self._save()

    def append_config_list(self, key: str, value: Any):
        current_list = getattr(self.configuration, key, [])
        if not isinstance(current_list, list):
            raise ValueError(f"Key '{key}' is not a list. Cannot append value.")
        current_list.append(value)
        self._save()

    @property
    def config(self) -> Config:
        return self.configuration
