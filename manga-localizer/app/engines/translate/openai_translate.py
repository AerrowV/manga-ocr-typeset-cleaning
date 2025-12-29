from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
from openai import OpenAI

@dataclass
class RegionText:
    region_id: str
    jp: str

class OpenAITranslator:
    def __init__(self, model: str = "gpt-5.2"):
        self.client = OpenAI()
        self.model = model

    def translate_regions(self, regions: Iterable[RegionText]) -> List[str]:
        items = list(regions)
        payload = "\n".join([f"[{r.region_id}]\n{r.jp}" for r in items])

        instructions = (
            "You are translating Japanese manga dialogue into natural English.\n"
            "Rules:\n"
            "- Keep honorifics (-san, -kun, -chan, -sama) when present.\n"
            "- Keep name order as it appears.\n"
            "- Preserve bracketed region ids exactly.\n"
            "- Output ONLY in this format:\n"
            "[id]\nEnglish\n\n"
        )

        resp = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=payload,
        )

        text = resp.output_text.strip()
        return self._parse_blocks(text, [r.region_id for r in items])

    def _parse_blocks(self, text: str, ids: List[str]) -> List[str]:
        out = {rid: "" for rid in ids}
        current = None
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                continue
            if current in out and line:
                out[current] += (line + "\n")
        return [out[rid].strip() for rid in ids]