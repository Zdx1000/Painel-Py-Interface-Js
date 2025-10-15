from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
  QComboBox,
  QDoubleSpinBox,
  QGraphicsDropShadowEffect,
  QLineEdit,
  QSpinBox,
  QTextEdit,
  QWidget,
)

# Paleta base clara com acento azul-escuro
# - Fundo: cinza muito claro
# - Superfícies: branco / azul neutro claro
# - Texto: cinza-azulado escuro
# - Acentos: azul-escuro

LIGHT_QSS = r"""
/* Base */
* { font-family: 'Segoe UI', 'Roboto', Arial; }
QWidget { background-color: #f4f7fb; color: #1b2534; }
QToolTip {
  color: #0f172a;
  background-color: #e8ecf5;
  border: 1px solid #c3d0ee;
  padding: 6px 10px;
}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
  background-color: #ffffff;
  color: #0f172a;
  border: 1px solid #c0c9dc;
  border-radius: 8px;
  padding: 8px 10px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
  border: 1px solid #1d4ed8;
}
QLineEdit[invalid="true"], QSpinBox[invalid="true"], QDoubleSpinBox[invalid="true"],
QComboBox[invalid="true"], QTextEdit[invalid="true"] {
  border: 1px solid #f97316;
  background-color: #fff7ed;
}
QLineEdit[success="true"], QSpinBox[success="true"], QDoubleSpinBox[success="true"],
QComboBox[success="true"], QTextEdit[success="true"] {
  border: 1px solid #0ea5e9;
  background-color: #f0f9ff;
}
QComboBox QAbstractItemView {
  background-color: #fbfcff;
  color: #0f172a;
  selection-background-color: #d6e3ff;
  selection-color: #0f172a;
  border: 1px solid #c0c9dc;
}

/* Botões */
QPushButton {
  background-color: #1e3a8a;
  color: #ffffff;
  border: 1px solid #193274;
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 600;
}
QPushButton:hover {
  background-color: #2747a3;
  border-color: #1f3e8f;
}
QPushButton:pressed {
  background-color: #1a3070;
  border-color: #16285f;
}
QPushButton:disabled {
  background-color: #d1d7e6;
  color: #8a97b7;
  border-color: #c5ccdd;
}
QPushButton[variant="ghost"] {
  background-color: transparent;
  color: #1e3a8a;
  border: 1px solid rgba(30, 58, 138, 0.35);
}
QPushButton[variant="ghost"]:hover {
  background-color: rgba(59, 130, 246, 0.08);
  border-color: rgba(30, 64, 175, 0.55);
}
QPushButton[variant="ghost"]:pressed {
  background-color: rgba(30, 58, 138, 0.18);
  border-color: rgba(30, 58, 138, 0.65);
}

/* Botão perigoso (excluir) */
QPushButton#danger {
  background-color: #d92d20;
  border-color: #b2251a;
}
QPushButton#danger:hover {
  background-color: #f04438;
  border-color: #d0372b;
}
QPushButton#danger:pressed {
  background-color: #b2251a;
  border-color: #8f1d15;
}

/* Botão do cabeçalho */
QPushButton#headerBtn {
  color: #ffffff;
  border-radius: 12px;
  padding: 8px 18px;
  font-weight: 700;
  letter-spacing: 0.2px;
  border: 1px solid #1d4ed8;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #2a5ade, stop:1 #1e3a8a);
}
QPushButton#headerBtn:hover {
  border-color: #2d64f0;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #3b6cf0, stop:1 #2644a3);
}
QPushButton#headerBtn:pressed {
  border-color: #1c3e9a;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #2246ae, stop:1 #1a3270);
}
QPushButton#headerBtn:disabled {
  background: #d1d7e6;
  color: #8a97b7;
  border-color: #c5ccdd;
}

/* Labels, títulos e chips */
QLabel#appTitle {
  font-family: 'Segoe UI Semibold', 'Segoe UI', Arial;
  font-size: 26px;
  font-weight: 700;
  color: #102a6b;
  padding: 12px 0 4px 0;
  letter-spacing: 0.4px;
}
QLabel#dataRefLabel {
  padding: 6px 12px;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #e7edff, stop:1 #d6e0ff);
  border: 1px solid #b9c6eb;
  border-radius: 8px;
  color: #1c2d55;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.6px;
}
QLabel.sectionTitle {
  font-size: 14px;
  font-weight: 600;
  color: #213766;
  text-transform: uppercase;
  letter-spacing: 1.6px;
}
QLabel#metricTitle {
  font-size: 13px;
  font-weight: 600;
  color: #3b4d73;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
QLabel#metricValue {
  font-size: 28px;
  font-weight: 700;
  color: #0f1d3a;
  letter-spacing: 0.4px;
}
QLabel#metricTimestamp {
  font-size: 12px;
  color: #5b6b8d;
}
QLabel.status-ok {
  color: #0f766e;
  background-color: #ecfdf3;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #a4e2cf;
}
QLabel.status-alert {
  color: #b54708;
  background-color: #fef3c7;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #f4ce74;
}
QLabel.status-error {
  color: #b42318;
  background-color: #fee2e2;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #fca5a5;
}
QLabel.status-neutral {
  color: #1e3a8a;
  background-color: #e0e7ff;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #c7d2fe;
}

/* Cards e containers */
QWidget#cardSurface, QFrame#cardSurface {
  background-color: #ffffff;
  border: 1px solid #d8dfec;
  border-radius: 12px;
}
QWidget#cardSurface[interactive="true"], QFrame#cardSurface[interactive="true"] {
  border-color: #c0d0f2;
}
QWidget#cardSurface[interactive="true"]:hover, QFrame#cardSurface[interactive="true"]:hover {
  border-color: #a5bdf5;
  background-color: #f4f7ff;
}
QWidget#appHeader {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #f1f5ff, stop:1 #e3ecff);
  border: 1px solid #c5d3f3;
  border-radius: 16px;
}

/* Tabela */
QTableView {
  background-color: #ffffff;
  alternate-background-color: #f6f8fd;
  gridline-color: #d3dbef;
  selection-background-color: #dbe5ff;
  selection-color: #0f172a;
  border: 1px solid #c6cfe4;
  border-radius: 10px;
}
QTableView::item:selected:active {
  background-color: #c7d7ff;
}
QTableView::item:hover {
  background-color: #eef3ff;
}
QHeaderView::section {
  background-color: #edf2ff;
  color: #1b2b4b;
  border: 1px solid #c6cfe4;
  padding: 8px;
  font-weight: 600;
}
QTableCornerButton::section {
  background-color: #edf2ff;
  border: 1px solid #c6cfe4;
}

/* Barras de rolagem */
QScrollBar:vertical {
  background: #f0f3fb;
  width: 12px;
  margin: 0px;
  border-radius: 6px;
}
QScrollBar::handle:vertical {
  background: #c7d2eb;
  min-height: 30px;
  border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
  background: #aebce2;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
  height: 0;
}

QScrollBar:horizontal {
  background: #f0f3fb;
  height: 12px;
  margin: 0px;
  border-radius: 6px;
}
QScrollBar::handle:horizontal {
  background: #c7d2eb;
  min-width: 30px;
  border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
  background: #aebce2;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
  width: 0;
}

/* GroupBoxes, frames sutis */
QGroupBox {
  border: 1px solid #d8dfec;
  border-radius: 10px;
  margin-top: 16px;
  background-color: #ffffff;
}
QGroupBox::title {
  subcontrol-origin: margin;
  left: 12px;
  padding: 0 6px;
  color: #213766;
  font-weight: 600;
}

/* Dialog buttons */
QDialogButtonBox QPushButton {
  min-width: 100px;
}


/* QTextEdit observação */
QTextEdit#obsEdit {
  background-color: #ffffff;
  border: 1px solid #c0c9dc;
  border-radius: 10px;
  padding: 10px 12px;
  selection-background-color: #dbe5ff;
  selection-color: #0f172a;
}
QTextEdit#obsEdit:focus {
  border: 1px solid #1d4ed8;
}
QTextEdit#obsEdit QScrollBar:vertical {
  background: transparent;
  width: 10px;
}
QTextEdit#obsEdit QScrollBar::handle:vertical {
  background: #c7d2eb;
  border-radius: 5px;
}
QTextEdit#obsEdit QScrollBar::handle:vertical:hover {
  background: #aebce2;
}

/* Toast-like feedback label */
QLabel#toastLabel {
  background-color: rgba(15, 23, 42, 0.9);
  color: #f8fafc;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 600;
}
"""

APP_QSS = LIGHT_QSS


_FocusColorKey = Tuple[str, str]


def _make_color(rgb: str, alpha: float) -> QColor:
  color = QColor(rgb)
  color.setAlphaF(max(0.0, min(1.0, alpha)))
  return color


class _FocusShadowFilter(QObject):
  """Ativa sombra via QGraphicsDropShadowEffect somente quando o widget está focado."""

  def __init__(
    self,
    *,
    blur_radius: float,
    x_offset: float,
    y_offset: float,
    colors: Sequence[Tuple[_FocusColorKey, QColor]],
    parent: QObject | None = None,
  ) -> None:
    super().__init__(parent)
    self._blur_radius = blur_radius
    self._x_off = x_offset
    self._y_off = y_offset
    self._color_map = dict(colors)

  def _color_for(self, widget: QWidget) -> QColor:
    if bool(widget.property("invalid")):
      return self._color_map[("state", "invalid")]
    if bool(widget.property("success")):
      return self._color_map[("state", "success")]
    return self._color_map[("state", "neutral")]

  def _apply_shadow(self, widget: QWidget) -> None:
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
      effect = QGraphicsDropShadowEffect(widget)
      widget.setGraphicsEffect(effect)
    effect.setBlurRadius(self._blur_radius)
    effect.setXOffset(self._x_off)
    effect.setYOffset(self._y_off)
    effect.setColor(self._color_for(widget))

  def _remove_shadow(self, widget: QWidget) -> None:
    widget.setGraphicsEffect(None)

  def eventFilter(self, obj: QObject, event: QEvent) -> bool:
    if not isinstance(obj, QWidget):
      return False

    if event.type() == QEvent.FocusIn:
      self._apply_shadow(obj)
    elif event.type() == QEvent.FocusOut:
      self._remove_shadow(obj)
    elif event.type() == QEvent.DynamicPropertyChange:
      dyn_event = event  # type: ignore[assignment]
      if isinstance(dyn_event, QDynamicPropertyChangeEvent) and obj.hasFocus():
        self._apply_shadow(obj)
    return False


def enable_focus_shadow(
  widget: QWidget,
  *,
  neutral_color: str = "#1d4ed8",
  success_color: str = "#0ea5e9",
  invalid_color: str = "#f97316",
  alpha: float = 0.35,
  blur_radius: float = 28.0,
  x_offset: float = 0.0,
  y_offset: float = 6.0,
) -> None:
  """Instala sombra focada usando eventos para reproduzir e refinar o efeito do antigo box-shadow."""

  colors = (
    (("state", "neutral"), _make_color(neutral_color, alpha)),
    (("state", "success"), _make_color(success_color, alpha)),
    (("state", "invalid"), _make_color(invalid_color, alpha)),
  )
  flt = _FocusShadowFilter(
    blur_radius=blur_radius,
    x_offset=x_offset,
    y_offset=y_offset,
    colors=colors,
    parent=widget,
  )
  widget.installEventFilter(flt)
  store: List[_FocusShadowFilter]
  store = getattr(widget, "_focus_shadow_filters", [])
  store.append(flt)
  setattr(widget, "_focus_shadow_filters", store)


INPUT_WIDGETS: Tuple[type[QWidget], ...] = (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit)


def enable_focus_shadow_for_children(
  container: QWidget,
  *,
  widgets: Iterable[QWidget] | None = None,
  include_types: Tuple[type[QWidget], ...] = INPUT_WIDGETS,
  **shadow_kwargs,
) -> None:
  """Aplica sombras elegantes a todos os campos de entrada do container, opcionalmente com overrides."""

  targets: Iterable[QWidget]
  if widgets is not None:
    targets = widgets
  else:
    found: List[QWidget] = []
    for widget_type in include_types:
      found.extend(container.findChildren(widget_type))
    targets = found

  for child in targets:
    enable_focus_shadow(child, **shadow_kwargs)


__all__ = [
  "LIGHT_QSS",
  "APP_QSS",
  "enable_focus_shadow",
  "enable_focus_shadow_for_children",
  "INPUT_WIDGETS",
]
