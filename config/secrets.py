import os
import yaml
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def _load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {}

def get_secret(key: str, default: Any = None) -> Any:
    """
    Reads a secret/config value. First checks environment variables,
    then config.yaml.
    """
    env_val = os.environ.get(key.upper())
    if env_val is not None:
        return env_val
    config = _load_config()
    return config.get(key, default)

def save_secret(key: str, value: Any) -> None:
    """
    Writes a secret/config value safely to config.yaml.
    """
    config = _load_config()
    config[key] = value
    
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
