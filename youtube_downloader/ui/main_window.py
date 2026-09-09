from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from youtube_downloader.core.errors import classify_error
from youtube_downloader.core.results import BatchState, summarize_results
from youtube_downloader.core.models import AudioFormat, DownloadRequest, MediaType, VideoProfile
from youtube_downloader.services.analyzer import MediaAnalyzer
from youtube_downloader.services.dependencies import DependencyService
from youtube_downloader.services.downloader import YtDlpBackend
from youtube_downloader.ui.workers import AnalysisWorker, DownloadWorker


APP_STYLE = """
QMainWindow, QWidget#Root, QScrollArea, QScrollArea > QWidget > QWidget {
    background: #080d14;
}
QWidget {
    color: #edf2f8;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QLabel { background: transparent; }
QFrame#Card {
    background: #101722;
    border: 1px solid #202b3a;
    border-radius: 16px;
}
QLabel#Title {
    color: #f8fafc;
    font-size: 26px;
    font-weight: 700;
}
QLabel#Subtitle, QLabel#Muted {
    color: #8f9caf;
}
QLabel#Section {
    color: #f5f8fc;
    font-size: 15px;
    font-weight: 700;
}
QLabel#FieldLabel {
    color: #aab5c5;
    font-size: 12px;
    font-weight: 600;
}
QLabel#MediaTitle {
    color: #f5f8fc;
    font-size: 16px;
    font-weight: 650;
}
QLabel#EngineStatus {
    background: #0c1917;
    border: 1px solid #1e4b3e;
    border-radius: 12px;
    color: #76e4b4;
    padding: 7px 11px;
    font-size: 12px;
    font-weight: 600;
}
QLabel#EngineStatus[state="warning"] {
    background: #201710;
    border-color: #67411d;
    color: #ffb66e;
}
QLabel#Thumbnail {
    background: #0a1018;
    border: 1px solid #1a2533;
    border-radius: 13px;
    color: #5f6c7d;
}
QLineEdit, QComboBox {
    background: #0b121c;
    border: 1px solid #29384b;
    border-radius: 10px;
    padding: 9px 12px;
    min-height: 24px;
    selection-background-color: #2f75e8;
}
QLineEdit:hover, QComboBox:hover {
    border-color: #3b4d65;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #4b8cff;
}
QLineEdit:read-only {
    color: #a8b4c5;
    background: #0a1018;
}
QComboBox::drop-down {
    border: 0;
    width: 30px;
}
QComboBox QAbstractItemView {
    background: #111927;
    color: #edf2f8;
    border: 1px solid #2b394d;
    selection-background-color: #244f8f;
    outline: 0;
    padding: 4px;
}
QPushButton {
    background: #172231;
    border: 1px solid #2b3a4f;
    border-radius: 10px;
    color: #e7edf5;
    padding: 9px 15px;
    min-height: 24px;
    font-weight: 600;
}
QPushButton:hover {
    background: #1d2b3e;
    border-color: #3c506b;
}
QPushButton:pressed {
    background: #121d2b;
}
QPushButton#Primary {
    background: #3d7eff;
    border-color: #4c8cff;
    color: white;
    font-weight: 700;
}
QPushButton#Primary:hover {
    background: #4b89ff;
}
QPushButton#Danger {
    background: #24161a;
    border-color: #63313a;
    color: #ff8d9b;
}
QPushButton#Ghost {
    background: transparent;
    border-color: #29384b;
    color: #aeb9c9;
    padding: 6px 10px;
    min-height: 20px;
    font-size: 12px;
}
QPushButton:disabled {
    background: #101722;
    border-color: #1c2634;
    color: #566274;
}
QProgressBar {
    background: #0a1018;
    border: 1px solid #263447;
    border-radius: 6px;
    min-height: 10px;
    max-height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background: #3d7eff;
    border-radius: 5px;
}
QTableWidget {
    background: #0b121c;
    alternate-background-color: #0d1520;
    border: 1px solid #29384b;
    border-radius: 10px;
    gridline-color: #1c2735;
    selection-background-color: #1d447a;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #121b28;
    color: #9eabbd;
    border: 0;
    border-bottom: 1px solid #29384b;
    padding: 8px;
    font-weight: 600;
}
QScrollBar:vertical {
    background: #080d14;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #263447;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


class ThumbnailLabel(QLabel):
    def __init__(self, text: str = "Önizleme"):
        super().__init__(text)
        self._source_pixmap: QPixmap | None = None
        self.setObjectName("Thumbnail")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(360, 203)
        self.setMaximumHeight(320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_image_bytes(self, payload: bytes | None) -> None:
        if not payload:
            self._source_pixmap = None
            self.clear()
            self.setText("Önizleme")
            return
        pixmap = QPixmap()
        if pixmap.loadFromData(payload):
            self._source_pixmap = pixmap
            self._render_pixmap()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        self._render_pixmap()

    def _render_pixmap(self) -> None:
        if not self._source_pixmap or self._source_pixmap.isNull():
            return
        target = self.contentsRect().size()
        if target.width() <= 0 or target.height() <= 0:
            return
        self.setPixmap(
            self._source_pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader V2")
        # Keep the app usable on smaller laptop screens. The central QScrollArea
        # handles vertical overflow; the body switches to a stacked layout when narrow.
        self.setMinimumSize(720, 560)
        self._body_is_stacked = False

        self.dependencies = DependencyService()
        self.analyzer = MediaAnalyzer(self.dependencies)
        self.backend = YtDlpBackend(self.dependencies)
        self.analysis = None
        self.analysis_thread: QThread | None = None
        self.analysis_worker = None
        self.download_thread: QThread | None = None
        self.download_worker = None
        self.save_path = Path.home() / "Downloads"
        if not self.save_path.exists():
            self.save_path = Path.home()

        self._build_ui()
        self._refresh_dependencies()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        self.main_scroll = scroll
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        root = QWidget()
        root.setObjectName("Root")
        scroll.setWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(30, 24, 30, 26)
        outer.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(16)
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("YouTube Downloader")
        title.setObjectName("Title")
        subtitle = QLabel("Video ve sesi doğru kaliteyle indir. Format seçimini ve dönüştürmeyi uygulama yönetsin.")
        subtitle.setObjectName("Subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)
        self.engine_label = QLabel("Motor kontrol ediliyor…")
        self.engine_label.setObjectName("EngineStatus")
        self.engine_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.engine_label, 0, Qt.AlignmentFlag.AlignTop)
        outer.addLayout(header)

        url_card = self._card()
        url_layout = QHBoxLayout(url_card)
        url_layout.setContentsMargins(16, 14, 16, 14)
        url_layout.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube video, Shorts veya playlist bağlantısını yapıştır…")
        self.url_input.setClearButtonEnabled(True)
        self.url_input.returnPressed.connect(self.analyze_url)
        self.analyze_button = QPushButton("Analiz Et")
        self.analyze_button.setObjectName("Primary")
        self.analyze_button.setMinimumWidth(112)
        self.analyze_button.clicked.connect(self.analyze_url)
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.analyze_button)
        outer.addWidget(url_card)

        self.body_layout = QGridLayout()
        self.body_layout.setHorizontalSpacing(16)
        self.body_layout.setVerticalSpacing(16)
        outer.addLayout(self.body_layout)

        self.preview_card = self._card()
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        preview_layout.setSpacing(12)
        self.thumbnail = ThumbnailLabel()
        preview_layout.addWidget(self.thumbnail, 1)

        self.media_title = QLabel("Henüz bağlantı analiz edilmedi")
        self.media_title.setObjectName("MediaTitle")
        self.media_title.setWordWrap(True)
        self.media_title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.media_meta = QLabel("Bağlantıyı yapıştırıp Analiz Et'e bas.")
        self.media_meta.setObjectName("Muted")
        self.media_meta.setWordWrap(True)
        preview_layout.addWidget(self.media_title)
        preview_layout.addWidget(self.media_meta)
        self.body_layout.addWidget(self.preview_card, 0, 0)

        self.options_card = self._card()
        self.options_card.setMinimumWidth(0)
        options = QVBoxLayout(self.options_card)
        options.setContentsMargins(18, 18, 18, 18)
        options.setSpacing(0)
        options.addWidget(self._section_label("İndirme ayarları"))
        options.addSpacing(14)

        self.media_type = QComboBox()
        self.media_type.addItem("Video", MediaType.VIDEO)
        self.media_type.addItem("Sadece ses", MediaType.AUDIO)
        self.media_type.currentIndexChanged.connect(self._sync_option_visibility)
        self._add_field(options, "Tür", self.media_type)

        self.quality_combo = QComboBox()
        self.quality_combo.setEnabled(False)
        self.quality_label = self._add_field(options, "Kalite", self.quality_combo)

        self.profile_combo = QComboBox()
        self.profile_combo.addItem("Uyumlu MP4 · H.264/AAC öncelikli", VideoProfile.COMPATIBLE_MP4)
        self.profile_combo.addItem("En iyi kalite · kaynak codec'leri", VideoProfile.BEST_QUALITY)
        self.profile_combo.addItem("Orijinale yakın · minimum müdahale", VideoProfile.ORIGINAL)
        self.profile_label = self._add_field(options, "Video profili", self.profile_combo)

        self.audio_combo = QComboBox()
        self.audio_combo.addItem("MP3 · 192 kbps", AudioFormat.MP3)
        self.audio_combo.addItem("M4A", AudioFormat.M4A)
        self.audio_combo.addItem("Opus", AudioFormat.OPUS)
        self.audio_combo.addItem("FLAC", AudioFormat.FLAC)
        self.audio_combo.addItem("WAV", AudioFormat.WAV)
        self.audio_combo.addItem("En iyi ses · dönüştürme yok", AudioFormat.BEST)
        self.audio_label = self._add_field(options, "Ses formatı", self.audio_combo)

        self.cookies_combo = QComboBox()
        self.cookies_combo.addItem("Oturum kullanma", None)
        self.cookies_combo.addItem("Chrome çerezleri", "chrome")
        self.cookies_combo.addItem("Edge çerezleri", "edge")
        self.cookies_combo.addItem("Firefox çerezleri", "firefox")
        self.cookies_combo.addItem("Brave çerezleri", "brave")
        self._add_field(options, "Oturum / kısıtlı videolar", self.cookies_combo)

        path_label = self._field_label("Kayıt konumu")
        options.addWidget(path_label)
        options.addSpacing(6)
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_display = QLineEdit(str(self.save_path))
        self.path_display.setReadOnly(True)
        self.path_display.setToolTip(str(self.save_path))
        browse = QPushButton("Klasör seç")
        browse.setMinimumWidth(96)
        browse.clicked.connect(self.choose_folder)
        path_row.addWidget(self.path_display, 1)
        path_row.addWidget(browse)
        options.addLayout(path_row)
        options.addSpacing(16)

        self.download_button = QPushButton("İndir")
        self.download_button.setObjectName("Primary")
        self.download_button.setMinimumHeight(42)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)
        options.addWidget(self.download_button)
        options.addStretch(1)

        self.body_layout.addWidget(self.options_card, 0, 1)
        self.body_layout.setColumnStretch(0, 3)
        self.body_layout.setColumnStretch(1, 2)
        self.body_layout.setColumnMinimumWidth(1, 330)

        self.playlist_card = self._card()
        playlist_layout = QVBoxLayout(self.playlist_card)
        playlist_layout.setContentsMargins(16, 16, 16, 16)
        playlist_layout.setSpacing(10)

        playlist_header = QHBoxLayout()
        self.playlist_title = self._section_label("Playlist")
        playlist_header.addWidget(self.playlist_title)
        playlist_header.addStretch(1)
        select_all = QPushButton("Tümünü seç")
        select_all.setObjectName("Ghost")
        select_all.clicked.connect(lambda: self._set_playlist_checks(True))
        clear_all = QPushButton("Seçimi temizle")
        clear_all.setObjectName("Ghost")
        clear_all.clicked.connect(lambda: self._set_playlist_checks(False))
        playlist_header.addWidget(select_all)
        playlist_header.addWidget(clear_all)
        playlist_layout.addLayout(playlist_header)

        self.playlist_table = QTableWidget(0, 3)
        self.playlist_table.setHorizontalHeaderLabels(["Seç", "Başlık", "Kanal"])
        self.playlist_table.horizontalHeader().setStretchLastSection(False)
        self.playlist_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.playlist_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.playlist_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.playlist_table.verticalHeader().setVisible(False)
        self.playlist_table.setAlternatingRowColors(True)
        self.playlist_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.playlist_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.playlist_table.setMaximumHeight(220)
        playlist_layout.addWidget(self.playlist_table)
        self.playlist_card.hide()
        outer.addWidget(self.playlist_card)

        progress_card = self._card()
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(16, 14, 16, 14)
        progress_layout.setSpacing(8)

        progress_header = QHBoxLayout()
        progress_header.setSpacing(10)
        self.status_label = QLabel("Hazır")
        self.status_label.setObjectName("Section")
        self.progress_percent = QLabel("0%")
        self.progress_percent.setObjectName("Muted")
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.setObjectName("Danger")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setMinimumWidth(92)
        self.cancel_button.clicked.connect(self.cancel_download)
        progress_header.addWidget(self.status_label)
        progress_header.addStretch(1)
        progress_header.addWidget(self.progress_percent)
        progress_header.addWidget(self.cancel_button)
        progress_layout.addLayout(progress_header)

        self.progress_item = QLabel("Henüz aktif indirme yok")
        self.progress_item.setObjectName("Muted")
        self.progress_item.setWordWrap(True)
        progress_layout.addWidget(self.progress_item)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        progress_layout.addWidget(self.progress)

        self.progress_detail = QLabel("")
        self.progress_detail.setObjectName("Muted")
        progress_layout.addWidget(self.progress_detail)
        outer.addWidget(progress_card)
        outer.addStretch(1)

        self._sync_option_visibility()
        self._apply_responsive_layout(self.width())

    def _apply_initial_window_size(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            self.resize(1180, 790)
            return

        available = screen.availableGeometry()
        width = min(1180, max(720, int(available.width() * 0.90)))
        height = min(790, max(560, int(available.height() * 0.88)))
        self.resize(width, height)
        self.move(
            available.x() + max(0, (available.width() - width) // 2),
            available.y() + max(0, (available.height() - height) // 2),
        )

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        self._apply_responsive_layout(event.size().width())

    def _apply_responsive_layout(self, width: int) -> None:
        # Two-column layout is comfortable above this threshold. Below it, moving
        # settings under the preview avoids clipped controls and horizontal scrolling.
        should_stack = width < 980
        if should_stack == self._body_is_stacked:
            return

        self._body_is_stacked = should_stack
        if should_stack:
            self.body_layout.addWidget(self.preview_card, 0, 0, 1, 2)
            self.body_layout.addWidget(self.options_card, 1, 0, 1, 2)
            self.body_layout.setColumnStretch(0, 1)
            self.body_layout.setColumnStretch(1, 0)
            self.body_layout.setColumnMinimumWidth(1, 0)
            self.thumbnail.setMinimumSize(300, 169)
        else:
            self.body_layout.addWidget(self.preview_card, 0, 0)
            self.body_layout.addWidget(self.options_card, 0, 1)
            self.body_layout.setColumnStretch(0, 3)
            self.body_layout.setColumnStretch(1, 2)
            self.body_layout.setColumnMinimumWidth(1, 330)
            self.thumbnail.setMinimumSize(360, 203)

    @staticmethod
    def _card() -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("Section")
        return label

    @staticmethod
    def _field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FieldLabel")
        return label

    def _add_field(self, layout: QVBoxLayout, label_text: str, widget: QWidget) -> QLabel:
        label = self._field_label(label_text)
        layout.addWidget(label)
        layout.addSpacing(6)
        layout.addWidget(widget)
        layout.addSpacing(12)
        return label

    def _refresh_dependencies(self) -> None:
        statuses = self.dependencies.check_all()
        missing = [item.name for item in statuses if item.required and not item.available]
        if missing:
            self.engine_label.setProperty("state", "warning")
            self.engine_label.setText("● Eksik: " + ", ".join(missing))
        else:
            self.engine_label.setProperty("state", "ready")
            self.engine_label.setText("● Motor hazır")
        self.engine_label.style().unpolish(self.engine_label)
        self.engine_label.style().polish(self.engine_label)

    def _sync_option_visibility(self) -> None:
        is_audio = self.media_type.currentData() is MediaType.AUDIO
        self.quality_combo.setEnabled(bool(self.analysis) and not is_audio)
        self.quality_label.setVisible(not is_audio)
        self.quality_combo.setVisible(not is_audio)
        self.profile_label.setVisible(not is_audio)
        self.profile_combo.setVisible(not is_audio)
        self.audio_label.setVisible(is_audio)
        self.audio_combo.setVisible(is_audio)

    def _set_playlist_checks(self, checked: bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.playlist_table.rowCount()):
            item = self.playlist_table.item(row, 0)
            if item:
                item.setCheckState(state)

    def choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Kayıt klasörü", str(self.save_path))
        if selected:
            self.save_path = Path(selected)
            self.path_display.setText(str(self.save_path))
            self.path_display.setToolTip(str(self.save_path))

    def analyze_url(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Bağlantı gerekli", "Önce bir YouTube bağlantısı gir.")
            return

        self.analyze_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.status_label.setText("Video analiz ediliyor…")
        self.progress_item.setText("Formatlar ve video bilgileri kontrol ediliyor")
        self.progress_detail.clear()
        self.progress_percent.setText("…")
        self.progress.setRange(0, 0)

        thread = QThread(self)
        worker = AnalysisWorker(self.analyzer, url)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._analysis_finished)
        worker.failed.connect(self._analysis_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.analysis_thread = thread
        self.analysis_worker = worker
        thread.finished.connect(self._clear_analysis_worker)
        thread.start()

    def _analysis_finished(self, result, thumbnail_bytes) -> None:
        self.analysis = result
        self.analyze_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_percent.setText("0%")
        self.status_label.setText("İndirmeye hazır")
        self.progress_item.setText(result.title)
        self.progress_detail.clear()

        self.media_title.setText(result.title)
        meta = []
        if result.uploader:
            meta.append(result.uploader)
        if result.is_playlist:
            meta.append(f"{len(result.entries)} video")
        elif result.duration:
            minutes, seconds = divmod(int(result.duration), 60)
            hours, minutes = divmod(minutes, 60)
            meta.append(f"{hours:d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:d}:{seconds:02d}")
        if result.warnings:
            meta.append(result.warnings[0])
        self.media_meta.setText("  ·  ".join(meta))
        self.thumbnail.set_image_bytes(thumbnail_bytes)

        self.quality_combo.clear()
        for option in result.qualities:
            self.quality_combo.addItem(option.label, option.height)
        self._sync_option_visibility()

        if result.is_playlist:
            self.playlist_card.show()
            self.playlist_title.setText(f"Playlist · {len(result.entries)} video")
            self.playlist_table.setRowCount(len(result.entries))
            for row, entry in enumerate(result.entries):
                check_item = QTableWidgetItem(str(row + 1))
                check_item.setFlags(check_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                check_item.setCheckState(Qt.CheckState.Checked)
                self.playlist_table.setItem(row, 0, check_item)
                self.playlist_table.setItem(row, 1, QTableWidgetItem(entry.title))
                self.playlist_table.setItem(row, 2, QTableWidgetItem(entry.uploader or "—"))
        else:
            self.playlist_card.hide()

    def _analysis_failed(self, exc) -> None:
        self.analyze_button.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_percent.setText("0%")
        classified = classify_error(exc)
        self.status_label.setText("Analiz başarısız")
        self.progress_item.setText(classified.user_message)
        self.progress_detail.clear()
        QMessageBox.critical(
            self,
            "Video analiz edilemedi",
            f"{classified.user_message}\n\nTeknik detay:\n{classified.technical_message[:800]}",
        )

    def start_download(self) -> None:
        if not self.analysis:
            return

        media_type = self.media_type.currentData()
        quality = None if media_type is MediaType.AUDIO else self.quality_combo.currentData()
        profile = self.profile_combo.currentData()
        audio_format = self.audio_combo.currentData()

        if self.analysis.is_playlist:
            source_urls = [
                entry.url
                for row, entry in enumerate(self.analysis.entries)
                if self.playlist_table.item(row, 0)
                and self.playlist_table.item(row, 0).checkState() == Qt.CheckState.Checked
            ]
        else:
            source_urls = [self.analysis.source_url]

        requests = [
            DownloadRequest(
                url=url,
                output_dir=self.save_path,
                media_type=media_type,
                quality_height=quality,
                video_profile=profile,
                audio_format=audio_format,
                browser_cookies=self.cookies_combo.currentData(),
            )
            for url in source_urls
            if url
        ]
        if not requests:
            QMessageBox.warning(self, "İndirilecek video yok", "Playlist içinde seçili bir video bulunamadı.")
            return

        # Reset cancellation before exposing the Cancel button. Doing it inside the
        # worker would create a race where an immediate click could be cleared.
        self.backend.reset_cancel()
        self.download_button.setEnabled(False)
        self.analyze_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_percent.setText("0%")
        self.status_label.setText("İndirme başlatılıyor…")
        if len(requests) > 1:
            self.progress_item.setText(f"{len(requests)} video indirme sırasına alındı")
        else:
            self.progress_item.setText(self.analysis.title)
        self.progress_detail.clear()

        thread = QThread(self)
        worker = DownloadWorker(self.backend, requests)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._download_progress)
        worker.finished.connect(self._download_finished)
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.download_thread = thread
        self.download_worker = worker
        thread.finished.connect(self._clear_download_worker)
        thread.start()

    def _download_progress(self, progress) -> None:
        percent = max(0, min(int(progress.percent), 100))
        self.status_label.setText(progress.status)
        self.progress.setValue(percent)
        self.progress_percent.setText(f"{percent}%")

        parts = []
        if progress.speed:
            parts.append(progress.speed)
        if progress.eta:
            parts.append(f"{progress.eta} kaldı")
        self.progress_detail.setText("  ·  ".join(parts))

    def _download_finished(self, results) -> None:
        self.download_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        summary = summarize_results(results)
        successes = list(summary.successes)
        failures = list(summary.failures)

        if summary.state is BatchState.CANCELLED:
            self.status_label.setText("İndirme iptal edildi")
            if successes:
                self.progress_item.setText(f"İptal edilmeden önce {len(successes)} dosya tamamlandı")
                self.progress_detail.setText(str(self.save_path))
            else:
                self.progress_item.setText("İşlem kullanıcı tarafından durduruldu")
                self.progress_detail.setText("Tamamlanmamış indirme devam dosyaları daha sonra sürdürülebilir.")
            # Preserve the last visible progress instead of presenting cancellation as 0% failure.
            self.progress_percent.setText("İptal")
            return

        if summary.state is BatchState.COMPLETED:
            self.status_label.setText(f"Tamamlandı · {len(successes)} dosya")
            self.progress.setValue(100)
            self.progress_percent.setText("100%")
            if len(successes) == 1 and successes[0].output_path:
                self.progress_item.setText(successes[0].output_path.name)
                self.progress_item.setToolTip(str(successes[0].output_path))
                self.progress_detail.setText(str(successes[0].output_path.parent))
                QMessageBox.information(self, "İndirme tamamlandı", f"Dosya kaydedildi:\n{successes[0].output_path}")
            else:
                self.progress_item.setText(f"{len(successes)} video başarıyla indirildi")
                self.progress_detail.setText(str(self.save_path))
                QMessageBox.information(self, "İndirme tamamlandı", f"{len(successes)} video başarıyla indirildi.")
            return

        if summary.state is BatchState.PARTIAL:
            self.status_label.setText(f"Kısmen tamamlandı · {len(successes)} başarılı, {len(failures)} hata")
            self.progress_item.setText("Bazı videolar indirilemedi")
        else:
            self.status_label.setText("İndirme başarısız")
            self.progress.setValue(0)
            self.progress_percent.setText("0%")
            self.progress_item.setText(failures[0].error_message or "İndirme tamamlanamadı")

        self.progress_detail.clear()
        error_lines = [f"• {item.title}: {item.error_message or item.error_code}" for item in failures[:8]]
        if len(failures) > 8:
            error_lines.append(f"• … ve {len(failures) - 8} hata daha")
        QMessageBox.warning(self, "İndirme sonucu", "\n".join(error_lines))

    def cancel_download(self) -> None:
        self.backend.cancel()
        self.cancel_button.setEnabled(False)
        self.status_label.setText("İptal ediliyor…")
        self.progress_detail.setText("Aktif işlem güvenli şekilde durduruluyor")

    def _clear_analysis_worker(self) -> None:
        self.analysis_worker = None
        self.analysis_thread = None

    def _clear_download_worker(self) -> None:
        self.download_worker = None
        self.download_thread = None


def run_app() -> int:
    app = QApplication.instance() or QApplication([])
    # Explicitly setting a valid point size avoids the QFont point-size -1 warning
    # observed on some Windows/Qt combinations when the system font is inherited.
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window._apply_initial_window_size()
    window.show()
    return app.exec()
