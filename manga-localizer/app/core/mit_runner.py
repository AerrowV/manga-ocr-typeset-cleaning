from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import List
from app.core.config import EngineConfig

def build_mit_command(cfg: EngineConfig, input_folder: Path, output_folder: Path) -> List[str]:
    input_folder = Path(input_folder).expanduser().resolve()
    output_folder = Path(output_folder).expanduser().resolve()

    cmd: List[str] = [cfg.python_exe, "-m", "manga_translator"]

    if cfg.verbose:
        cmd.append("-v")

    if cfg.use_gpu:
        cmd.append("--use-gpu")

    cmd += ["--kernel-size", "7"]

    # Font (prefer Comic Shanns, fallback Anime Ace)
    font = (cfg.font_path or "").strip()
    engine_dir = Path(getattr(cfg, "engine_dir", "") or "").expanduser().resolve()

    if not font and engine_dir.exists():
        preferred = engine_dir / "fonts" / "comic shanns 2.ttf"
        fallback = engine_dir / "fonts" / "anime_ace_3.ttf"
        if preferred.exists():
            font = str(preferred)
        elif fallback.exists():
            font = str(fallback)

    if font:
        cmd += ["--font-path", str(Path(font).expanduser().resolve())]

    cmd += ["local", "-i", str(input_folder), "-o", str(output_folder), "--overwrite"]

    cfg_file = (getattr(cfg, "config_file", "") or "").strip()
    if cfg_file:
        cfg_path = Path(cfg_file).expanduser().resolve()
        cmd += ["--config-file", str(cfg_path)]

    return cmd


def run_mit_blocking(cfg: EngineConfig, input_folder: Path, output_folder: Path) -> int:
    output_folder = Path(output_folder).expanduser().resolve()
    output_folder.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    engine_dir = Path(getattr(cfg, "engine_dir", "") or "").expanduser().resolve()
    cmd = build_mit_command(cfg, input_folder, output_folder)

    proc = subprocess.Popen(
        cmd,
        cwd=str(engine_dir) if engine_dir.exists() else None,  # IMPORTANT
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    assert proc.stdout is not None
    for line in proc.stdout:
        print(line.rstrip())

    return proc.wait()
