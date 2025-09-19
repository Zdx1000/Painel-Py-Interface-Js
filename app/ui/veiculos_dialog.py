from __future__ import annotations
from typing import Iterable, List, Tuple, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from .theme import DARK_QSS



class VeiculosDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        initial: Optional[Iterable[Tuple[str, int] | Tuple[str, int, int]]] = None,
        read_only: bool = False,
        title: str = "Veículos Pendentes",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 420)
        self.setStyleSheet(DARK_QSS)
        self._read_only = read_only
        # Normaliza initial para lista de (veiculo, quantidade, porcentagem)
        norm_rows: List[Tuple[str, int, int]] = []
        for tup in (initial or []):
            try:
                if len(tup) == 2:  # type: ignore[arg-type]
                    veic, pct = tup  # type: ignore[misc]
                    norm_rows.append((str(veic), 0, int(pct)))
                elif len(tup) == 3:  # type: ignore[arg-type]
                    veic, qtd, pct = tup  # type: ignore[misc]
                    norm_rows.append((str(veic), int(qtd), int(pct)))
            except Exception:
                continue
        self._rows: List[Tuple[str, int, int]] = norm_rows
        # Índice da linha atualmente em edição (None quando não está editando)
        self._edit_row: Optional[int] = None

        layout = QtWidgets.QVBoxLayout(self)

        # Editor de entrada (oculto em read-only)
        self.editor = QtWidgets.QWidget()
        e_lay = QtWidgets.QHBoxLayout(self.editor)
        self.veh_input = QtWidgets.QLineEdit(); self.veh_input.setPlaceholderText("Veículo")
        self.qty_input = QtWidgets.QSpinBox(); self.qty_input.setRange(0, 100000); self.qty_input.setPrefix("Qtd ")
        self.pct_input = QtWidgets.QSpinBox(); self.pct_input.setRange(0, 100); self.pct_input.setSuffix(" %")
        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.clicked.connect(self._on_add)
        # Botão cancelar edição (invisível por padrão)
        self.btn_cancel_edit = QtWidgets.QPushButton("Cancelar")
        self.btn_cancel_edit.setVisible(False)
        self.btn_cancel_edit.clicked.connect(self._cancel_edit)
        e_lay.addWidget(self.veh_input, 1)
        e_lay.addWidget(self.qty_input)
        e_lay.addWidget(self.pct_input)
        e_lay.addWidget(self.btn_add)
        e_lay.addWidget(self.btn_cancel_edit)
        layout.addWidget(self.editor)

        # Tabela
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Veículo", "Qtd", "%", "Ações"])
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
            self.table.setColumnHidden(3, True)
            btns.button(QtWidgets.QDialogButtonBox.Ok).setText("Fechar")
            btns.button(QtWidgets.QDialogButtonBox.Cancel).hide()

        self._refresh_table()

    # Dados expostos ao chamar .exec()
    def get_rows(self) -> List[Tuple[str, int, int]]:
        return list(self._rows)

    # Eventos
    def _on_add(self) -> None:
        v = self.veh_input.text().strip()
        q = int(self.qty_input.value())
        p = int(self.pct_input.value())
        if not v:
            QtWidgets.QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do veículo.")
            return
        if p < 0 or p > 100:
            QtWidgets.QMessageBox.warning(self, "Valor inválido", "Porcentagem deve estar entre 0 e 100.")
            return
        if q < 0:
            QtWidgets.QMessageBox.warning(self, "Valor inválido", "Quantidade não pode ser negativa.")
            return
        # Se há linha em edição, atualiza; caso contrário, adiciona nova
        if self._edit_row is not None and 0 <= self._edit_row < len(self._rows):
            self._rows[self._edit_row] = (v, q, p)
            self._edit_row = None
            self.btn_add.setText("Adicionar")
            self.btn_cancel_edit.setVisible(False)
        else:
            self._rows.append((v, q, p))
        self.veh_input.clear()
        self.qty_input.setValue(0)
        self.pct_input.setValue(0)
        self._refresh_table()

    def _on_remove(self, row: int) -> None:
        if 0 <= row < len(self._rows):
            # Confirmação antes de remover
            resp = QtWidgets.QMessageBox.question(
                self,
                "Remover item",
                f"Deseja remover o veículo '{self._rows[row][0]}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if resp != QtWidgets.QMessageBox.Yes:
                return
            del self._rows[row]
            # Se remover a linha em edição, cancela a edição
            if self._edit_row is not None:
                if self._edit_row == row:
                    self._cancel_edit()
                elif self._edit_row > row:
                    # Ajusta índice de edição se necessário
                    self._edit_row -= 1
            self._refresh_table()

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:  # type: ignore[override]
        # Enter/Return: aciona Adicionar/Salvar quando editor tem foco
        if e.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self.editor.isVisible() and (self.veh_input.hasFocus() or self.qty_input.hasFocus() or self.pct_input.hasFocus()):
                self._on_add()
                return
        # ESC: cancela edição se estiver editando, senão comportamento padrão (fecha diálogo se aplicável)
        if e.key() == QtCore.Qt.Key_Escape:
            if self._edit_row is not None:
                self._cancel_edit()
                return
        super().keyPressEvent(e)

    def _on_edit(self, row: int) -> None:
        if 0 <= row < len(self._rows):
            veic, qtd, pct = self._rows[row]
            self.veh_input.setText(veic)
            self.qty_input.setValue(int(qtd))
            self.pct_input.setValue(int(pct))
            self._edit_row = int(row)
            self.btn_add.setText("Salvar")
            self.btn_cancel_edit.setVisible(True)

    def _cancel_edit(self) -> None:
        self._edit_row = None
        self.veh_input.clear()
        self.qty_input.setValue(0)
        self.pct_input.setValue(0)
        self.btn_add.setText("Adicionar")
        self.btn_cancel_edit.setVisible(False)

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self._rows))
        for i, (veic, qtd, pct) in enumerate(self._rows):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(veic))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(qtd)))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{pct}%"))
            # Ações: Editar e Remover (somente quando não for read-only)
            actions = QtWidgets.QWidget()
            hl = QtWidgets.QHBoxLayout(actions)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(6)
            if not self._read_only:
                btn_edit = QtWidgets.QPushButton("Editar")
                btn_edit.setToolTip("Editar este veículo")
                btn_edit.clicked.connect(lambda _=False, r=i: self._on_edit(r))
                btn_del = QtWidgets.QPushButton("Remover")
                btn_del.setObjectName("danger")
                btn_del.setToolTip("Remover este veículo")
                btn_del.clicked.connect(lambda _=False, r=i: self._on_remove(r))
                hl.addWidget(btn_edit)
                hl.addWidget(btn_del)
            actions.setLayout(hl)
            self.table.setCellWidget(i, 3, actions)
