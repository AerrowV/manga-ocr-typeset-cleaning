# Manga Localizer UI (Desktop)

A desktop UI wrapper that batch-translates Japanese manga pages to English using:
- `manga-image-translator` (detection + OCR + inpaint cleaning + typesetting)
- OpenAI API (translation via OPENAI_API_KEY)

## Why this approach?
`manga-image-translator` already supports OCR + text removal + typesetting + translation. This app focuses on a clean workflow/UI and reproducible settings.

## Requirements
- Python 3.10+ (3.11 recommended)
- Windows: Microsoft C++ Build Tools may be required for some deps (common with ML stacks).
- Optional GPU: install correct PyTorch build (depends on your CUDA).

## Setup (recommended)
### 1) Create a venv
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
