from __future__ import annotations

import os, subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSplitter, QTextEdit,
    QMessageBox, QCheckBox, QLineEdit, QFormLayout, QComboBox,
    QTabWidget, QToolBar, QDockWidget, QGroupBox, QScrollArea, QToolButton, 
    QSizePolicy
)

from app.core.config import AppConfig
from app.core.settings_store import load_settings, save_settings
from app.core.mit_runner import build_mit_command

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


# --------- Themes (Manga Studio: dark + warm light) ---------
DARK_THEME = """
QMainWindow, QWidget { background: #0f1115; color: #e7e7e7; font-size: 12px; }
QToolBar { background: #0f1115; border: 0px; spacing: 8px; padding: 8px; }
QToolBar QToolButton { background: #1a1f29; border: 1px solid #2a3140; border-radius: 10px; padding: 8px 10px; }
QToolBar QToolButton:hover { background: #232a36; }
QToolBar QToolButton:pressed { background: #2c3546; }
QScrollArea { background: #0b0d12; border-radius: 12px; }
QScrollArea QWidget { background: transparent; }

QLineEdit, QComboBox, QTextEdit {
  background: #121722;
  border: 1px solid #2a3140;
  border-radius: 10px;
  padding: 8px;
  selection-background-color: #3b6cff;
  selection-color: #0f1115;
}

QComboBox::drop-down { border: 0px; padding-right: 8px; }

/* Dark mode dropdown popup (custom blue) */
QComboBox QAbstractItemView {
  background: #121722;
  border: 1px solid #2a3140;
  outline: 0px;
}

QComboBox QAbstractItemView::item {
  padding: 6px 10px;
  color: #e7e7e7;
}

QComboBox QAbstractItemView::item:hover {
  background: #1a2234;
}

QComboBox QAbstractItemView::item:selected {
  background: #3b6cff;
  color: #0f1115;
}


QListWidget {
  background: #121722;
  border: 1px solid #2a3140;
  border-radius: 12px;
  padding: 6px;
}
QListWidget::item {
  padding: 8px;
  margin: 2px;
  border-radius: 10px;
}
QListWidget::item:selected { background: #24304a; border: 1px solid #345089; }
QListWidget::item:hover { background: #1a2234; }

QTabWidget::pane { border: 1px solid #2a3140; border-radius: 12px; background: #121722; }
QTabBar::tab {
  background: #0f1115;
  border: 1px solid #2a3140;
  padding: 8px 12px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  margin-right: 4px;
}
QTabBar::tab:selected { background: #121722; }

QGroupBox {
  border: 1px solid #2a3140;
  border-radius: 12px;
  margin-top: 18px;          /* more space for title */
  padding: 14px 12px 12px 12px;
  background: #121722;
  font-weight: 600;
}
QGroupBox::title {
  subcontrol-origin: margin;
  subcontrol-position: top left;
  left: 14px;
  top: 10px;                /* lift title off border */
  padding: 2px 8px;
  background: #121722;       /* match box bg so it looks cut out */
  border-radius: 8px;
  color: #cbd5e1;
}

QDockWidget { titlebar-close-icon: none; titlebar-normal-icon: none; }
QDockWidget::title {
  background: #0f1115;
  padding: 8px;
  border-bottom: 1px solid #2a3140;
}
QDockWidget QWidget { background: #0f1115; }

QPushButton {
  background: #1a1f29;
  border: 1px solid #2a3140;
  border-radius: 10px;
  padding: 8px 10px;
}
QPushButton:hover { background: #232a36; }
QPushButton:pressed { background: #2c3546; }

QLabel#CanvasTitle { color: #aab3c2; font-size: 11px; }

/* Dark mode checkbox indicator (custom blue) */
QCheckBox::indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #2a3140;
  background: #121722;
}

QCheckBox::indicator:hover {
  border: 1px solid #3a4a66;
}

QCheckBox::indicator:checked {
  background: #3b6cff; /* your custom blue */
  border: 1px solid #2f7fa0;
  image: url(assets/check_dark.svg);
}

QCheckBox::indicator:checked:hover {
  background: #5bb3d6; /* slightly lighter on hover */
}
"""

LIGHT_THEME = """
QMainWindow, QWidget { background: #f3eadb; color: #2a2420; font-size: 12px; }
QToolBar { background: #f3eadb; border: 0px; spacing: 8px; padding: 8px; }
QScrollArea { background: #efe2cf; border-radius: 12px; }
QScrollArea QWidget { background: transparent; }

QToolBar QToolButton {
  background: #fff7ea;
  border: 1px solid #e2caa7;
  border-radius: 10px;
  padding: 8px 10px;
}
QToolBar QToolButton:hover { background: #fff0da; }
QToolBar QToolButton:pressed { background: #ffe7c5; }

QLineEdit, QComboBox, QTextEdit {
  background: #fff7ea;
  border: 1px solid #e2caa7;
  border-radius: 10px;
  padding: 8px;
  selection-background-color: #ebae34;
  selection-color: #2a2420;
}

QComboBox::drop-down { border: 0px; padding-right: 8px; }

QComboBox QAbstractItemView {
  background: #fff7ea;
  border: 1px solid #ebae34;
  outline: 0px;
}

QComboBox QAbstractItemView::item {
  padding: 6px 10px;
  color: #2a2420;
}

QComboBox QAbstractItemView::item:selected {
  background: #ebae34;
  color: #2a2420;
}

QListWidget {
  background: #fff7ea;
  border: 1px solid #e2caa7;
  border-radius: 12px;
  padding: 6px;
}
QListWidget::item { padding: 8px; margin: 2px; border-radius: 10px; }
QListWidget::item:selected { background: #ffe3b5; border: 1px solid #f0b35a; }
QListWidget::item:hover { background: #fff0da; }

QTabWidget::pane { border: 1px solid #e2caa7; border-radius: 12px; background: #fff7ea; }
QTabBar::tab {
  background: #f3eadb;
  border: 1px solid #e2caa7;
  padding: 8px 12px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  margin-right: 4px;
  color: #2a2420;
}
QTabBar::tab:selected { background: #fff7ea; }

QGroupBox {
  border: 1px solid #e2caa7;
  border-radius: 12px;
  margin-top: 18px;
  padding: 14px 12px 12px 12px;
  background: #fff7ea;
  font-weight: 600;
}
QGroupBox::title {
  subcontrol-origin: margin;
  subcontrol-position: top left;
  left: 14px;
  top: 10px;
  padding: 2px 8px;
  background: #fff7ea;
  border-radius: 8px;
  color: #6a4b2a;
}

QDockWidget::title { background: #f3eadb; padding: 8px; border-bottom: 1px solid #e2caa7; }
QDockWidget QWidget { background: #f3eadb; }

QPushButton {
  background: #fff7ea;
  border: 1px solid #e2caa7;
  border-radius: 10px;
  padding: 8px 10px;
}
QPushButton:hover { background: #fff0da; }
QPushButton:pressed { background: #ffe7c5; }

QLabel#CanvasTitle { color: #6a5a4c; font-size: 11px; }

QCheckBox::indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #e2caa7;
  background: #fff7ea;
  image: none;
}

QCheckBox::indicator:checked {
  background: #ebae34;
  border: 1px solid #c97f12;
  image: url(assets/check_dark.svg);
}

QCheckBox::indicator:hover {
  border: 1px solid #ebae34;
}

QListWidget::item:selected {
  background: #ffe3b5;
  border: 1px solid #f0b35a;
  color: #2a2420;
}
"""

@dataclass
class PageItem:
    path: Path


class MitWorker(QThread):
    log_line = Signal(str)
    finished_code = Signal(int)

    def __init__(self, cmd: List[str], workdir: Optional[Path] = None):
        super().__init__()
        self.cmd = cmd
        self.workdir = workdir

    def run(self) -> None:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"   
        proc = subprocess.Popen(
            self.cmd,
            cwd=str(self.workdir) if self.workdir else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            self.log_line.emit(line.rstrip())
        self.finished_code.emit(proc.wait())


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Manga Localizer UI")
        self.resize(1280, 820)

        self.cfg: AppConfig = load_settings()
        self.current_dir: Optional[Path] = Path(self.cfg.last_open_dir) if self.cfg.last_open_dir else None
        self.pages: List[PageItem] = []
        self.current_page: Optional[PageItem] = None
        self.worker: Optional[MitWorker] = None

        # Zoom state for previews
        self._zoom = 1.0
        self._fit_to_view = True

        # -------- Toolbar --------
        tb = QToolBar("Main")
        tb.setIconSize(QSize(18, 18))
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        self.act_open = QAction("Open Folder", self)
        self.act_open.triggered.connect(self.open_folder)
        tb.addAction(self.act_open)

        self.act_run = QAction("Translate", self)
        self.act_run.triggered.connect(self.translate_folder)
        tb.addAction(self.act_run)

        self.act_out = QAction("Open Output", self)
        self.act_out.triggered.connect(self.open_output_folder)
        tb.addAction(self.act_out)

        tb.addSeparator()

        self.theme_btn = QToolButton()
        self.theme_btn.setText("☾ Dark")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setChecked(True)
        self.theme_btn.clicked.connect(self.toggle_theme)
        tb.addWidget(self.theme_btn)

        # -------- Left: search + list --------
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search pages…")
        self.search.textChanged.connect(self._apply_search_filter)

        self.progress_badge = QLabel("0/0")
        self.progress_badge.setObjectName("CanvasTitle")

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_select_page)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(self.search, 1)
        row.addWidget(self.progress_badge)
        left_layout.addLayout(row)
        left_layout.addWidget(self.list_widget, 1)

        # -------- Center: preview tabs + zoom controls --------
        self.preview_tabs = QTabWidget()
        
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.original_label.setScaledContents(False)

        self.output_label = QLabel()
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.output_label.setScaledContents(False)

        self.original_scroll = QScrollArea()
        self.original_scroll.setWidgetResizable(True)
        self.original_scroll.setFrameShape(QScrollArea.NoFrame)
        self.original_scroll.setWidget(self.original_label)
        self.original_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.original_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.output_scroll = QScrollArea()
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setFrameShape(QScrollArea.NoFrame)
        self.output_scroll.setWidget(self.output_label)
        self.output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.preview_tabs.addTab(self._wrap_canvas(self.original_scroll, "Original"), "Original")
        self.preview_tabs.addTab(self._wrap_canvas(self.output_scroll, "Output"), "Output")


        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(8)
        self.btn_fit = QPushButton("Fit")
        self.btn_fit.clicked.connect(self.zoom_fit)
        self.btn_100 = QPushButton("100%")
        self.btn_100.clicked.connect(self.zoom_100)
        self.btn_minus = QPushButton("–")
        self.btn_minus.clicked.connect(self.zoom_out)
        self.btn_plus = QPushButton("+")
        self.btn_plus.clicked.connect(self.zoom_in)
        zoom_row.addWidget(self.btn_fit)
        zoom_row.addWidget(self.btn_100)
        zoom_row.addStretch(1)
        zoom_row.addWidget(self.btn_minus)
        zoom_row.addWidget(self.btn_plus)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_layout.setSpacing(10)
        center_layout.addLayout(zoom_row)
        center_layout.addWidget(self.preview_tabs, 1)

        # -------- Right: settings cards (collapsible-ish via groupboxes) --------
        self.chk_gpu = QCheckBox("Use GPU")
        self.chk_gpu.setChecked(self.cfg.engine.use_gpu)

        self.chk_verbose = QCheckBox("Verbose (debug + intermediates)")
        self.chk_verbose.setChecked(self.cfg.engine.verbose)

        self.python_exe = QLineEdit(self.cfg.engine.python_exe)

        self.engine_dir = QLineEdit(getattr(self.cfg.engine, "engine_dir", ""))
        self.config_file = QLineEdit(getattr(self.cfg.engine, "config_file", ""))
        self.font_path = QLineEdit(self.cfg.engine.font_path)

        self.detector = QComboBox()
        self.detector.addItems(["default", "ctd"])
        self.detector.setCurrentText(self.cfg.engine.detector)

        self.ocr = QComboBox()
        self.ocr.addItems(["48px", "default"])
        self.ocr.setCurrentText(self.cfg.engine.ocr)

        self.inpainter = QComboBox()
        self.inpainter.addItems(["lama_large", "lama", "none"])
        self.inpainter.setCurrentText(self.cfg.engine.inpainter)

        self.target_lang = QLineEdit(self.cfg.engine.target_lang)

        engine_box = QGroupBox("Engine")
        engine_form = QFormLayout(engine_box)
        engine_form.setSpacing(10)
        engine_form.addRow("Engine dir:", self.engine_dir)
        engine_form.addRow("Engine python:", self.python_exe)
        engine_form.addRow("", self.chk_gpu)
        engine_form.addRow("", self.chk_verbose)

        typeset_box = QGroupBox("Typeset")
        typeset_form = QFormLayout(typeset_box)
        typeset_form.setSpacing(10)
        typeset_form.addRow("Target lang:", self.target_lang)
        typeset_form.addRow("Font path:", self.font_path)
        typeset_form.addRow("Config file:", self.config_file)

        cleaning_box = QGroupBox("Cleaning")
        cleaning_form = QFormLayout(cleaning_box)
        cleaning_form.setSpacing(10)
        cleaning_form.addRow("Detector:", self.detector)
        cleaning_form.addRow("OCR:", self.ocr)
        cleaning_form.addRow("Inpainter:", self.inpainter)

        settings_panel = QWidget()
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        settings_layout.setSpacing(10)
        settings_layout.addWidget(engine_box)
        settings_layout.addWidget(typeset_box)
        settings_layout.addWidget(cleaning_box)
        settings_layout.addStretch(1)

        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QScrollArea.NoFrame)
        settings_scroll.setWidget(settings_panel)

        # -------- Root splitter (Left / Center / Right) --------
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(settings_scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([280, 720, 360])

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

        # -------- Bottom log dock --------
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        dock = QDockWidget("Logs", self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        dock.setWidget(self.log)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        dock.setMinimumHeight(160)

        # Autofill on first run
        self._autofill_paths_if_missing()

        if self.current_dir and self.current_dir.exists():
            self._load_folder(self.current_dir)

        # Apply theme (default dark)
        self.apply_theme(dark=True)

    # ---------- UI helpers ----------
    def _wrap_canvas(self, widget: QWidget, title: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        cap = QLabel(title)
        cap.setObjectName("CanvasTitle")
        lay.addWidget(cap)
        lay.addWidget(widget, 1)
        return w

    def apply_theme(self, dark: bool) -> None:
        self.setStyleSheet(DARK_THEME if dark else LIGHT_THEME)
        self.theme_btn.setText("☾ Dark" if dark else "☀ Light")

    def toggle_theme(self) -> None:
        self.apply_theme(dark=self.theme_btn.isChecked())

    # ---------- persistence ----------
    def closeEvent(self, event) -> None:
        self._save_cfg()
        super().closeEvent(event)

    def _save_cfg(self) -> None:
        self.cfg.engine.engine_dir = self.engine_dir.text().strip()
        self.cfg.engine.config_file = self.config_file.text().strip()

        self.cfg.engine.python_exe = self.python_exe.text().strip() or self.cfg.engine.python_exe
        self.cfg.engine.font_path = self.font_path.text().strip()
        self.cfg.engine.target_lang = self.target_lang.text().strip() or "ENG"
        self.cfg.engine.use_gpu = self.chk_gpu.isChecked()
        self.cfg.engine.verbose = self.chk_verbose.isChecked()
        self.cfg.engine.detector = self.detector.currentText()
        self.cfg.engine.ocr = self.ocr.currentText()
        self.cfg.engine.inpainter = self.inpainter.currentText()
        self.cfg.last_open_dir = str(self.current_dir) if self.current_dir else ""
        self.cfg.output_root = str(self._output_root_abs())
        save_settings(self.cfg)

    def _autofill_paths_if_missing(self) -> None:
        changed = False
        base = Path(__file__).resolve().parents[2] 

        if not (self.engine_dir.text() or "").strip():
            candidate_engine = base / "manga-image-translator"
            if candidate_engine.exists() and (candidate_engine / "manga_translator").exists():
                self.engine_dir.setText(str(candidate_engine))
                changed = True

        if not (self.config_file.text() or "").strip():
            candidate_cfg = base / "mit-config.json"
            if candidate_cfg.exists():
                self.config_file.setText(str(candidate_cfg))
                changed = True

        if not (self.font_path.text() or "").strip():
            eng = Path((self.engine_dir.text() or "").strip())
            if eng.exists():
                # Prefer Comic Shanns (your file)
                candidate_font = eng / "fonts" / "comic shanns 2.ttf"
                if candidate_font.exists():
                    self.font_path.setText(str(candidate_font))
                    changed = True
                else:
                    # Fallback
                    fallback_font = eng / "fonts" / "anime_ace_3.ttf"
                    if fallback_font.exists():
                        self.font_path.setText(str(fallback_font))
                        changed = True

        desired_output = (base / "output").resolve()
        current_output = Path(getattr(self.cfg, "output_root", "") or "").expanduser()

        need_change = False
        if not str(current_output).strip():
            need_change = True
        else:
            # If it's relative or points inside manga-image-translator, fix it
            abs_current = current_output
            if not abs_current.is_absolute():
                abs_current = (base / abs_current).resolve()

            norm = str(abs_current).replace("\\", "/").lower()
            if "manga-image-translator" in norm:
                need_change = True
            else:
                # keep the absolute version so it won't drift later
                if abs_current != current_output:
                    current_output = abs_current
                    need_change = True

        if need_change:
            self.cfg.output_root = str(desired_output)
            changed = True

        if changed:
            self._save_cfg()

    # ---------- folder + pages ----------
    def open_folder(self) -> None:
        start = str(self.current_dir) if self.current_dir else ""
        folder = QFileDialog.getExistingDirectory(self, "Select manga folder", start)
        if not folder:
            return
        self._load_folder(Path(folder))

    def _load_folder(self, folder: Path) -> None:
        self.current_dir = folder
        self.pages = []
        self.list_widget.clear()

        files = sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS])
        for p in files:
            item = PageItem(p)
            self.pages.append(item)
            li = QListWidgetItem(p.name)
            li.setData(Qt.UserRole, str(p))
            self.list_widget.addItem(li)

        if self.pages:
            self.list_widget.setCurrentRow(0)

        self._update_progress_badge()
        self._save_cfg()

    def _apply_search_filter(self, text: str) -> None:
        query = (text or "").strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(query not in item.text().lower())

    def _update_progress_badge(self) -> None:
        total = len(self.pages)
        done = 0
        if self.current_dir:
            out_dir = self._output_root_abs() / self.current_dir.name
            for p in self.pages:
                if (out_dir / p.path.name).exists():
                    done += 1
        self.progress_badge.setText(f"{done}/{total}")

    # ---------- preview ----------
    def _on_select_page(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if not current:
            return
        p = Path(current.data(Qt.UserRole))
        self.current_page = PageItem(p)
        self._refresh_previews()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.current_page:
            self._refresh_previews()

    def _refresh_previews(self) -> None:
        if not self.current_page:
            return
        original = self.current_page.path
        self._show_pixmap(self.original_label, original)

        out_img = self._translated_output_for(original)
        if out_img and out_img.exists():
            self._show_pixmap(self.output_label, out_img)
        else:
            self.output_label.setText("Not translated yet.")
            self.output_label.setPixmap(QPixmap())

        self._update_progress_badge()

    def _show_pixmap(self, target: QLabel, path: Path) -> None:
        if not path.exists():
            target.setText("(missing)")
            target.setPixmap(QPixmap())
            return

        pm = QPixmap(str(path))
        if pm.isNull():
            target.setText("(failed to load image)")
            target.setPixmap(QPixmap())
            return

        if self._fit_to_view:
            target.setMinimumSize(0, 0)
            target.resize(0, 0)

            scroll = target.parent()
            while scroll is not None and not isinstance(scroll, QScrollArea):
                scroll = scroll.parent()
            viewport_size = scroll.viewport().size() if isinstance(scroll, QScrollArea) else target.size()

            scaled = pm.scaled(viewport_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            target.setPixmap(scaled)
        else:
            scaled = pm.scaled(pm.size() * self._zoom, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            target.setPixmap(scaled)

            # IMPORTANT: make the label actually become bigger than the viewport
            target.resize(scaled.size())
            target.setMinimumSize(scaled.size())


    # ---------- zoom controls ----------
    def zoom_fit(self) -> None:
        self._fit_to_view = True
        self._zoom = 1.0
        self._apply_scroll_mode()
        self._refresh_previews()

    def zoom_100(self) -> None:
        self._fit_to_view = False
        self._zoom = 1.0
        self._apply_scroll_mode()
        self._refresh_previews()

    def zoom_in(self) -> None:
        self._fit_to_view = False
        self._zoom = min(5.0, self._zoom * 1.2)
        self._apply_scroll_mode()
        self._refresh_previews()

    def zoom_out(self) -> None:
        self._fit_to_view = False
        self._zoom = max(0.2, self._zoom / 1.2)
        self._apply_scroll_mode()
        self._refresh_previews()

    # ---------- actions ----------
    def open_output_folder(self) -> None:
        if not self.current_dir:
            QMessageBox.information(self, "No folder", "Open a manga folder first.")
            return
        out_dir = (self._output_root_abs() / self.current_dir.name).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            os.startfile(str(out_dir))  # Windows
        except Exception:
            QMessageBox.information(self, "Output", f"Output folder:\n{out_dir}")

    def translate_folder(self) -> None:
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Busy", "Translation is already running.")
            return
        
        if not self.current_dir:
            QMessageBox.warning(self, "No folder", "Open a manga folder first.")
            return

        self._save_cfg()

        engine_dir = Path(self.cfg.engine.engine_dir).expanduser()
        if not engine_dir.exists():
            QMessageBox.warning(
                self,
                "Engine dir missing",
                "Set 'Engine dir' to your manga-image-translator folder (the one containing 'manga_translator').",
            )
            return

        out_dir = (self._output_root_abs() / self.current_dir.name).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        self.cfg.output_root = str(self._output_root_abs())
        save_settings(self.cfg)

        cmd = build_mit_command(self.cfg.engine, self.current_dir, out_dir)

        self.log.append("Running:\n" + " ".join(cmd) + "\n")

        self.act_open.setEnabled(False)
        self.act_out.setEnabled(False)
        self.act_run.setEnabled(False)

        try:
            self.worker = MitWorker(cmd, workdir=engine_dir)
            self.worker.log_line.connect(self.log.append)
            self.worker.finished_code.connect(self._on_worker_done)
            self.worker.start()
        except Exception as e:
            self.log.append(f"Failed to start worker: {e}")
            self.act_open.setEnabled(True)
            self.act_out.setEnabled(True)
            self.act_run.setEnabled(True)

    def _on_worker_done(self, code: int) -> None:
        self.log.append(f"\nDone. Exit code: {code}")
        self.act_open.setEnabled(True)
        self.act_out.setEnabled(True)
        self.act_run.setEnabled(True)

        if self.current_page:
            self._refresh_previews()
        else:
            self._update_progress_badge()

        self.worker.deleteLater()
        self.worker = None

    def _translated_output_for(self, original: Path) -> Optional[Path]:
        if not self.current_dir:
            return None
        return (self._output_root_abs() / self.current_dir.name / original.name)

    def _apply_scroll_mode(self) -> None:
        # Fit mode => scroll area resizes label to viewport (no scrollbars needed)
        # Zoom mode => label keeps its own size (scrollbars can appear)
        resizable = self._fit_to_view
        self.original_scroll.setWidgetResizable(resizable)
        self.output_scroll.setWidgetResizable(resizable)

        if resizable:
            # allow labels to shrink back down when returning to Fit
            self.original_label.setMinimumSize(0, 0)
            self.output_label.setMinimumSize(0, 0)

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _output_root_abs(self) -> Path:
        """
        Always return an absolute output root.
        If cfg.output_root is relative, resolve it under repo root.
        """
        root = Path(getattr(self.cfg, "output_root", "") or "").expanduser()

        if not str(root).strip():
            root = self._repo_root() / "output"

        if not root.is_absolute():
            root = (self._repo_root() / root).resolve()

        return root

