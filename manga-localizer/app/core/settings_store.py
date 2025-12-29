from __future__ import annotations
import json
from pathlib import Path
from app.core.config import AppConfig

def _config_path() -> Path:
    base = Path.home() / ".manga_localizer_ui"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"

def load_settings() -> AppConfig:
    p = _config_path()
    if not p.exists():
        return AppConfig()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
    except Exception:
        # If settings file is corrupted, reset safely.
        return AppConfig()

def save_settings(cfg: AppConfig) -> None:
    p = _config_path()
    p.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")
