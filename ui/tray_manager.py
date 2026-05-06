"""
System Tray Manager for Prism Desktop.
Uses QSystemTrayIcon (native Qt) for reliable click handling across all
desktop environments, including KDE/SNI where pystray's left-click
delivery is unreliable.
"""

import sys
from io import BytesIO
from typing import Callable, Optional

from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QObject, Qt, pyqtSignal, QRect
from core.i18n import tr, on_language_changed


class TraySignals(QObject):
    """Qt signals for tray icon events."""
    left_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()


class TrayManager:
    """Manages the system tray icon using QSystemTrayIcon."""

    def __init__(
        self,
        on_left_click: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
        theme: str = 'dark',
    ):
        self.on_left_click = on_left_click
        self.on_settings = on_settings
        self.on_quit = on_quit
        self.theme = theme

        self._tray: Optional[QSystemTrayIcon] = None
        self._menu: Optional[QMenu] = None
        self._show_action = None
        self._quit_action = None

        # Qt signals (same interface as before — callers connect to these)
        self.signals = TraySignals()

        if on_left_click:
            self.signals.left_clicked.connect(on_left_click)
        if on_settings:
            self.signals.settings_clicked.connect(on_settings)
        if on_quit:
            self.signals.quit_clicked.connect(on_quit)

    # ------------------------------------------------------------------
    # Icon creation (PIL → QIcon)
    # ------------------------------------------------------------------

    def create_icon_image(self, size: int = 64) -> Image.Image:
        """Create a stylized AetherDesk monogram tray icon."""
        scale = 4
        canvas_size = size * scale
        image = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        bg_color = (18, 24, 40, 255)
        beam_left = (63, 208, 255, 255)
        beam_right = (74, 124, 255, 255)
        bridge = (245, 248, 255, 255)

        if self.theme != 'dark':
            bg_color = (245, 248, 252, 255)
            beam_left = (0, 152, 204, 255)
            beam_right = (45, 93, 226, 255)
            bridge = (32, 42, 62, 255)

        bg_pad    = 1 * scale
        bg_radius = 10 * scale
        if hasattr(draw, 'rounded_rectangle'):
            draw.rounded_rectangle(
                [bg_pad, bg_pad, canvas_size - bg_pad, canvas_size - bg_pad],
                radius=bg_radius,
                fill=bg_color,
            )
        else:
            draw.rectangle(
                [bg_pad, bg_pad, canvas_size - bg_pad, canvas_size - bg_pad],
                fill=bg_color,
            )

        left_beam = [
            (52 * scale, 210 * scale),
            (112 * scale, 44 * scale),
            (152 * scale, 44 * scale),
            (98 * scale, 210 * scale),
        ]
        right_beam = [
            (158 * scale, 44 * scale),
            (198 * scale, 44 * scale),
            (204 * scale, 62 * scale),
            (144 * scale, 210 * scale),
        ]
        bridge_rect = [
            106 * scale,
            128 * scale,
            162 * scale,
            152 * scale,
        ]

        draw.polygon(left_beam, fill=beam_left)
        draw.polygon(right_beam, fill=beam_right)
        draw.rounded_rectangle(bridge_rect, radius=8 * scale, fill=bridge)

        resampler = getattr(Image, 'Resampling', Image).LANCZOS
        return image.resize((size, size), resampler)

    def _to_qicon(self, pil_image: Image.Image) -> QIcon:
        """Convert a PIL Image to a QIcon."""
        buf = BytesIO()
        pil_image.save(buf, format='PNG')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        return QIcon(pixmap)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Create and show the tray icon. Must be called from the Qt main thread."""
        qicon = self._to_qicon(self.create_icon_image())

        self._tray = QSystemTrayIcon(qicon)
        self._tray.setToolTip(tr("tray.tooltip"))

        # Context menu (shown on right-click).
        # WA_TranslucentBackground lets the rounded corners actually clip;
        # without it Qt draws the border-radius visually but the window stays
        # rectangular underneath.
        self._menu = QMenu()
        self._menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._menu.setStyleSheet(self._menu_stylesheet())
        self._show_action = self._menu.addAction(tr("tray.show_dashboard"))
        self._show_action.triggered.connect(self.signals.left_clicked)
        self._menu.addSeparator()
        self._quit_action = self._menu.addAction(tr("tray.quit"))
        self._quit_action.triggered.connect(self.signals.quit_clicked)

        self._tray.setContextMenu(self._menu)

        # activated covers left-click (Trigger), double-click (DoubleClick),
        # and middle-click (MiddleClick) — all toggle the dashboard.
        self._tray.activated.connect(self._on_activated)

        self._tray.show()
        on_language_changed(self.refresh_texts)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handle tray icon activation (left-click, double-click, etc.)."""
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
            QSystemTrayIcon.ActivationReason.MiddleClick,
        ):
            self.signals.left_clicked.emit()

    def stop(self):
        """Hide and destroy the tray icon."""
        if self._tray:
            self._tray.hide()
            self._tray = None

    # ------------------------------------------------------------------
    # Updates
    # ------------------------------------------------------------------

    def set_theme(self, theme: str):
        """Update the icon and menu colours for the current theme."""
        self.theme = theme
        if self._tray:
            self._tray.setIcon(self._to_qicon(self.create_icon_image()))
        if self._menu:
            self._menu.setStyleSheet(self._menu_stylesheet())

    def update_title(self, title: str):
        """Update the tray icon tooltip."""
        if self._tray:
            self._tray.setToolTip(title)

    def refresh_texts(self):
        if self._tray:
            self._tray.setToolTip(tr("tray.tooltip"))
        if self._show_action:
            self._show_action.setText(tr("tray.show_dashboard"))
        if self._quit_action:
            self._quit_action.setText(tr("tray.quit"))

    def geometry(self) -> QRect:
        """Return the tray icon geometry when available."""
        if self._tray:
            return self._tray.geometry()
        return QRect()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _menu_stylesheet(self) -> str:
        """Return a theme-aware stylesheet for the tray context menu."""
        if self.theme == 'dark':
            bg        = '#1e1e1e'
            fg        = '#ffffff'
            highlight = '#0078d4'
            hl_text   = '#ffffff'
            border    = '#555555'
            separator = '#444444'
        else:
            bg        = '#ffffff'
            fg        = '#1e1e1e'
            highlight = '#0078d4'
            hl_text   = '#ffffff'
            border    = '#d1d1d1'
            separator = '#e0e0e0'

        return (
            f"QMenu {{"
            f"  background-color: {bg};"
            f"  color: {fg};"
            f"  border: 1px solid {border};"
            f"  border-radius: 8px;"
            f"  padding: 4px;"
            f"}}"
            f"QMenu::item {{"
            f"  padding: 5px 20px 5px 12px;"
            f"  border-radius: 5px;"
            f"  margin: 1px 4px;"
            f"}}"
            f"QMenu::item:selected {{"
            f"  background-color: {highlight};"
            f"  color: {hl_text};"
            f"}}"
            f"QMenu::separator {{"
            f"  height: 1px;"
            f"  background: {separator};"
            f"  margin: 4px 8px;"
            f"}}"
        )
