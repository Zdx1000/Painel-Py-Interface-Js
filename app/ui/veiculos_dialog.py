from __future__ import annotations
from typing import Iterable, List, Tuple, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from .theme import APP_QSS


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
        self.resize(600, 420)
        self.setMinimumWidth(600)
        self.setMaximumWidth(600)
        self.setMinimumHeight(420)
        self.setMaximumHeight(420)
        self.setStyleSheet(APP_QSS)
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
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QtWidgets.QLabel(title)
        header.setObjectName("metricTitle")
        header.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(header)

        # Editor de entrada (oculto em read-only)
        editor_card = QtWidgets.QFrame()
        editor_card.setObjectName("cardSurface")
        editor_card.setProperty("interactive", True)
        editor_card_lay = QtWidgets.QVBoxLayout(editor_card)
        editor_card_lay.setContentsMargins(18, 18, 18, 12)
        editor_card_lay.setSpacing(10)

        self.editor = QtWidgets.QWidget()
        e_lay = QtWidgets.QHBoxLayout(self.editor)
        e_lay.setSpacing(10)
        self.veh_input = QtWidgets.QLineEdit(); self.veh_input.setPlaceholderText("Veículo")
        self.qty_input = QtWidgets.QSpinBox(); self.qty_input.setRange(0, 100000); self.qty_input.setPrefix("Qtd ")
        self.pct_input = QtWidgets.QSpinBox(); self.pct_input.setRange(0, 100); self.pct_input.setSuffix(" %")
        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.clicked.connect(self._on_add)
        # Botão cancelar edição (invisível por padrão)
        self.btn_cancel_edit = QtWidgets.QPushButton("Cancelar")
        self.btn_cancel_edit.setProperty("variant", "ghost")
        self.btn_cancel_edit.setVisible(False)
        self.btn_cancel_edit.clicked.connect(self._cancel_edit)
        try:
            style = self.btn_cancel_edit.style()
            style.unpolish(self.btn_cancel_edit)
            style.polish(self.btn_cancel_edit)
        except Exception:
            pass
        e_lay.addWidget(self.veh_input, 1)
        e_lay.addWidget(self.qty_input)
        e_lay.addWidget(self.pct_input)
        e_lay.addWidget(self.btn_add)
        e_lay.addWidget(self.btn_cancel_edit)
        editor_card_lay.addWidget(self.editor)
        layout.addWidget(editor_card)
        self._apply_card_shadow(editor_card, blur=24, y_offset=8, alpha=26)

        # Tabela
        table_card = QtWidgets.QFrame()
        table_card.setObjectName("cardSurface")
        table_card_lay = QtWidgets.QVBoxLayout(table_card)
        table_card_lay.setContentsMargins(18, 18, 18, 18)
        table_card_lay.setSpacing(12)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Veículo", "Qtd", "%", "Editação e Exclusão"])
        self.table.horizontalHeader().setStretchLastSection(True)
        try:
            self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        except Exception:
            pass
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table_card_lay.addWidget(self.table, 1)
        layout.addWidget(table_card, 1)
        self._apply_card_shadow(table_card, blur=26, y_offset=10, alpha=26)

        # Botões padrão
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.button(QtWidgets.QDialogButtonBox.Ok).setMinimumWidth(96)
        cancel_btn = btns.button(QtWidgets.QDialogButtonBox.Cancel)
        if cancel_btn is not None:
            cancel_btn.setMinimumWidth(96)
            cancel_btn.setProperty("variant", "ghost")
            try:
                style = cancel_btn.style()
                style.unpolish(cancel_btn)
                style.polish(cancel_btn)
            except Exception:
                pass
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        if self._read_only:
            self.editor.hide()
            btns.button(QtWidgets.QDialogButtonBox.Ok).setText("Fechar")
            btns.button(QtWidgets.QDialogButtonBox.Cancel).hide()

        self._refresh_table()

    def _apply_card_shadow(self, widget: QtWidgets.QWidget, *, blur: int = 24, y_offset: int = 8, alpha: int = 28) -> None:
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(0)
            shadow.setYOffset(y_offset)
            shadow.setColor(QtGui.QColor(15, 23, 42, alpha))
            widget.setGraphicsEffect(shadow)
        except Exception:
            pass

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
                btn_edit.setProperty("variant", "ghost")
                try:
                    style = btn_edit.style()
                    style.unpolish(btn_edit)
                    style.polish(btn_edit)
                except Exception:
                    pass
                btn_edit.clicked.connect(lambda _=False, r=i: self._on_edit(r))
                btn_del = QtWidgets.QPushButton("Remover")
                btn_del.setObjectName("danger")
                btn_del.setToolTip("Remover este veículo")
                btn_del.clicked.connect(lambda _=False, r=i: self._on_remove(r))
                hl.addWidget(btn_edit)
                hl.addWidget(btn_del)
            else:
                badge = QtWidgets.QLabel("Somente visualização")
                badge.setObjectName("tableHint")
                badge.setAlignment(QtCore.Qt.AlignCenter)
                badge.setMinimumWidth(120)
                hl.addWidget(badge)
            actions.setLayout(hl)
            self.table.setCellWidget(i, 3, actions)
