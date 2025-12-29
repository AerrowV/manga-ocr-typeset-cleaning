from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field
import sys

class EngineConfig(BaseModel):
    # Python executable that has manga-image-translator installed
    python_exe: str = Field(default_factory=lambda: sys.executable)    
    engine_dir: str = ""  # path to manga-image-translator folder (where manga_translator/ exists)
    config_file: str = ""

    use_gpu: bool = False
    detector: str = "default"      # matches engine options
    ocr: str = "48px"              # recommended for JP in their docs :contentReference[oaicite:6]{index=6}
    inpainter: str = "lama_large"  # recommended :contentReference[oaicite:7]{index=7}

    target_lang: str = "ENG"       # engine language code
    font_path: str = ""            # optional
    overwrite: bool = True
    verbose: bool = True

    def ensure_valid(self) -> None:
        if self.font_path:
            p = Path(self.font_path)
            if not p.exists():
                raise ValueError(f"Font path does not exist: {p}")

class AppConfig(BaseModel):
    last_open_dir: str = ""
    output_root: str = "output"
    engine: EngineConfig = Field(default_factory=EngineConfig)
