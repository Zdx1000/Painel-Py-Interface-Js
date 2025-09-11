from __future__ import annotations

# Paleta base
# - Fundo: quase preto
# - Superfícies: cinza-azulado escuro
# - Texto: branco suave
# - Acento: azul

DARK_QSS = r"""
/* Base */
* { font-family: 'Segoe UI', Roboto, Arial; }
QWidget { background-color: #0d1117; color: #e6eef5; }
QToolTip { color: #e6eef5; background-color: #1b2230; border: 1px solid #2a3446; }

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
  background-color: #121826; color: #e6eef5;
  border: 1px solid #263143; border-radius: 8px; padding: 8px 10px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
  border: 1px solid #3d8bff;
}
QComboBox QAbstractItemView {
  background-color: #121826; color: #e6eef5; selection-background-color: #1c5fe6; selection-color: #ffffff;
  border: 1px solid #263143;
}

/* Botões */
QPushButton {
  background-color: #2f81f7; color: #ffffff; border: none; border-radius: 8px;
  padding: 8px 14px; font-weight: 600;
}
QPushButton:hover { background-color: #4c97ff; }
QPushButton:pressed { background-color: #1d6fe0; }
QPushButton:disabled { background-color: #3a4660; color: #9aa8bd; }

/* Botão perigoso (excluir) */
QPushButton#danger { background-color: #e5484d; }
QPushButton#danger:hover { background-color: #ff5c62; }
QPushButton#danger:pressed { background-color: #c73a40; }
/* Botão do cabeçalho (verde escuro) */
QPushButton#headerBtn {
  color: #ffffff;
  border-radius: 12px;
  padding: 8px 16px;
  font-weight: 700;
  letter-spacing: 0.2px;
  border: 1px solid #2e8b57; /* verde borda */
  background-color: #1e7a3f; /* fallback */
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #2aa052, stop:1 #1e7a3f);
}
QPushButton#headerBtn:hover {
  border-color: #3fb46d;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #33b761, stop:1 #238a45);
}
QPushButton#headerBtn:pressed {
  border-color: #1b5e34;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #238a45, stop:1 #1b5e34);
}
QPushButton#headerBtn:disabled { background: #3a4660; color: #9aa8bd; border-color: #3a4660; }

/* Tabela */
QTableView {
  background-color: #0f1522; alternate-background-color: #111a2b; gridline-color: #24324a;
  selection-background-color: #1c5fe6; selection-color: #ffffff; border: 1px solid #223047; border-radius: 8px;
}
QHeaderView::section {
  background-color: #101827; color: #d7e3f4; border: 1px solid #223047; padding: 8px;
}
QTableCornerButton::section { background-color: #101827; border: 1px solid #223047; }

/* Barras de rolagem */
QScrollBar:vertical { background: #0f1522; width: 10px; margin: 0px; }
QScrollBar::handle:vertical { background: #2a3b57; min-height: 30px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #35507b; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal { background: #0f1522; height: 10px; margin: 0px; }
QScrollBar::handle:horizontal { background: #2a3b57; min-width: 30px; border-radius: 5px; }
QScrollBar::handle:horizontal:hover { background: #35507b; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* GroupBoxes, frames sutis */
QGroupBox { border: 1px solid #223047; border-radius: 8px; margin-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }

/* Dialog buttons */
QDialogButtonBox QPushButton { min-width: 96px; }
/* Título do app */
QLabel#appTitle {
  font-family: "Arial Black", "Segoe UI", Arial;
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  padding: 10px 0 6px 0;
  letter-spacing: 0.5px;
}
/* Container do cabeçalho */
QWidget#appHeader {
  background-color: #000000;
  border: 1px solid #223047;
  border-radius: 12px;
}

/* Observação: destaque sutil e melhor leitura */
QTextEdit#obsEdit {
  background-color: #0f1522;
  border: 1px solid #2b3a55;
  border-radius: 10px;
  padding: 10px 12px;
  selection-background-color: #1c5fe6;
}
QTextEdit#obsEdit:focus {
  border: 1px solid #2aa052; /* tom verde sutil para indicar foco */
  /* Qt Style Sheets não suportam box-shadow; usamos uma borda mais espessa */
  border-width: 2px;
}
QTextEdit#obsEdit QScrollBar:vertical { background: transparent; width: 8px; }
QTextEdit#obsEdit QScrollBar::handle:vertical { background: #31466b; border-radius: 4px; }
QTextEdit#obsEdit QScrollBar::handle:vertical:hover { background: #3a5887; }
"""


__all__ = ["DARK_QSS"]
