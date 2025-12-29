from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import List
from app.core.config import EngineConfig

def build_mit_command(cfg: EngineConfig, input_folder: Path, output_folder: Path) -> List[str]:
    # force absolute paths so cwd/workdir never affects where output goes
    input_folder = Path(input_folder).expanduser().resolve()
    output_folder = Path(output_folder).expanduser().resolve()

    cmd: List[str] = [cfg.python_exe, "-m", "manga_translator"]

    if cfg.verbose:
        cmd.append("-v")

    if cfg.use_gpu:
        cmd.append("--use-gpu")

    cmd += ["--kernel-size", "7"]

    font = (cfg.font_path or "").strip()
    if not font:
        engine_dir = Path(getattr(cfg, "engine_dir", "")).expanduser()
        candidate = engine_dir / "fonts" / "anime_ace_3.ttf"
        if candidate.exists():
            font = str(candidate)

    if font:
        cmd += ["--font-path", font]

    # Subcommand (ABSOLUTE -i and -o)
    cmd += ["local", "-i", str(input_folder), "-o", str(output_folder), "--overwrite"]

    cfg_file = (getattr(cfg, "config_file", "") or "").strip()
    if cfg_file:
        cfg_path = Path(cfg_file).expanduser().resolve()
        cmd += ["--config-file", str(cfg_path)]

    return cmd


def run_mit_blocking(cfg: EngineConfig, input_folder: Path, output_folder: Path) -> int:
    output_folder.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()

    cmd = build_mit_command(cfg, input_folder, output_folder)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    assert proc.stdout is not None
    for line in proc.stdout:
        # This is consumed by the UI thread worker; here it's just for completeness if used headless.
        print(line.rstrip())

    return proc.wait()
