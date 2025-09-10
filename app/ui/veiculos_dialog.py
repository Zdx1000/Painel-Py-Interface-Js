from __future__ import annotations
from typing import Iterable, List, Tuple, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from .theme import DARK_QSS



class VeiculosDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        initial: Optional[Iterable[Tuple[str, int]]] = None,
        read_only: bool = False,
        title: str = "Veículos Pendentes",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 420)
        self.setStyleSheet(DARK_QSS)
        self._read_only = read_only
        self._rows: List[Tuple[str, int]] = list(initial or [])

        layout = QtWidgets.QVBoxLayout(self)

        # Editor de entrada (oculto em read-only)
        self.editor = QtWidgets.QWidget()
        e_lay = QtWidgets.QHBoxLayout(self.editor)
        self.veh_input = QtWidgets.QLineEdit(); self.veh_input.setPlaceholderText("Veículo")
        self.pct_input = QtWidgets.QSpinBox(); self.pct_input.setRange(0, 100); self.pct_input.setSuffix(" %")
        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.clicked.connect(self._on_add)
        e_lay.addWidget(self.veh_input, 1)
        e_lay.addWidget(self.pct_input)
        e_lay.addWidget(self.btn_add)
        layout.addWidget(self.editor)

        # Tabela
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Veículo", "%", "Ações"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table, 1)

        # Botões padrão
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.button(QtWidgets.QDialogButtonBox.Ok).setMinimumWidth(96)
        btns.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumWidth(96)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        if self._read_only:
            self.editor.hide()
            self.table.setColumnHidden(2, True)
            btns.button(QtWidgets.QDialogButtonBox.Ok).setText("Fechar")
            btns.button(QtWidgets.QDialogButtonBox.Cancel).hide()

        self._refresh_table()

    # Dados expostos ao chamar .exec()
    def get_rows(self) -> List[Tuple[str, int]]:
        return list(self._rows)

    # Eventos
    def _on_add(self) -> None:
        v = self.veh_input.text().strip()
        p = int(self.pct_input.value())
        if not v:
            QtWidgets.QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do veículo.")
            return
        if p < 0 or p > 100:
            QtWidgets.QMessageBox.warning(self, "Valor inválido", "Porcentagem deve estar entre 0 e 100.")
            return
        self._rows.append((v, p))
        self.veh_input.clear()
        self.pct_input.setValue(0)
        self._refresh_table()

    def _on_remove(self, row: int) -> None:
        if 0 <= row < len(self._rows):
            del self._rows[row]
            self._refresh_table()

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self._rows))
        for i, (veic, pct) in enumerate(self._rows):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(veic))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{pct}%"))
            btn = QtWidgets.QPushButton("Remover")
            btn.clicked.connect(lambda _=False, r=i: self._on_remove(r))
            self.table.setCellWidget(i, 2, btn)
