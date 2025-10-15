from __future__ import annotations
import sys
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets
from datetime import timezone, timedelta

from ..db.database import init_db, get_session
from ..db.repository import MetricaRepository
from .veiculos_dialog import VeiculosDialog
from ..db.repository import (
    VeiculoPendenteRepository,
    VeiculoDescargaC3Repository,
    VeiculoAntecipadoRepository,
    VeiculoCarregamentoC3Repository,
)
from pydantic import BaseModel, field_validator, ValidationError
from .theme import APP_QSS
from ..api.server import ApiServer
from sqlalchemy import select
from ..db.models import Metrica, VeiculoPendente, VeiculoDescargaC3, VeiculoAntecipado
from PySide6.QtCore import QEasingCurve, QEvent



class MetricaTableModel(QtCore.QAbstractTableModel):
    HEADERS = [
        "ID",
        "Paletes Agendados",
        "Paletes Produzidos",
        "Total de fichas",
        "Fichas finalizadas",
        "Descargas (C3)",
        "Carregamentos (C3)",
        "Chamado Granel",
        "Paletizada",
        "Veículos Pendentes",
        "Paletes Pendentes",
        "Fichas antecipadas",
        "Criado em",
        "Editação e Exclusão",
    ]

    def __init__(self, rows: list[tuple]) -> None:
        super().__init__()
        self._rows = rows

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:  # type: ignore[override]
        return len(self._rows)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            return self._rows[index.row()][index.column()]
        if role == QtCore.Qt.ForegroundRole:
            try:
                value = self._rows[index.row()][index.column()]
            except Exception:
                value = None
            if index.column() in (9, 10) and isinstance(value, (int, float)) and value > 0:
                return QtGui.QColor(190, 18, 60)
            if index.column() in (4,) and isinstance(value, (int, float)) and value >= 0:
                return QtGui.QColor(16, 94, 67)
        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):  # type: ignore[override]
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_rows(self, rows: list[tuple]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class InteractiveHighlightDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, view: QtWidgets.QTableView, interactive_cols: set[int]):
        super().__init__(view)
        self.view = view
        self._interactive_cols = set(interactive_cols)
        self._hover_index: QtCore.QModelIndex | None = None
        self._hoverProgress = 0.0
        self._anim = QtCore.QPropertyAnimation(self, b"hoverProgress")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def setHoveredIndex(self, idx: QtCore.QModelIndex | None):
        was_interactive = self._is_interactive(self._hover_index)
        self._hover_index = idx if (idx and idx.isValid()) else None
        now_interactive = self._is_interactive(self._hover_index)
        # anima quando entra/sai de uma célula interativa
        if now_interactive and self._hoverProgress < 1.0:
            self._start_anim(self._hoverProgress, 1.0)
        elif not now_interactive and self._hoverProgress > 0.0:
            self._start_anim(self._hoverProgress, 0.0)
        v = self.view
        if v and v.viewport():
            v.viewport().update()

    def _start_anim(self, start: float, end: float):
        try:
            self._anim.stop()
            self._anim.setStartValue(start)
            self._anim.setEndValue(end)
            self._anim.start()
        except Exception:
            self._hoverProgress = end

    def _is_interactive(self, idx: QtCore.QModelIndex | None) -> bool:
        return bool(idx and idx.isValid() and idx.column() in self._interactive_cols)

    @QtCore.Property(float)
    def hoverProgress(self) -> float:  # type: ignore[override]
        return self._hoverProgress

    @hoverProgress.setter
    def hoverProgress(self, v: float) -> None:  # type: ignore[override]
        self._hoverProgress = max(0.0, min(1.0, float(v)))
        if self.view and self.view.viewport():
            self.view.viewport().update()

    def helpEvent(self, event: QtWidgets.QHelpEvent, view: QtWidgets.QAbstractItemView, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> bool:  # type: ignore[override]
        if self._is_interactive(index):
            title = None
            try:
                mdl = view.model()
                title = mdl.headerData(index.column(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            except Exception:
                title = None
            tip = f"Dê dois cliques para ver {title}" if title else "Dê dois cliques para abrir detalhes"
            QtWidgets.QToolTip.showText(event.globalPos(), tip)
            return True
        return super().helpEvent(event, view, option, index)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:  # type: ignore[override]
        # Pintura padrão
        super().paint(painter, option, index)
        if index.column() not in self._interactive_cols:
            return
        # Calcular hover do item
        hovered = bool(option.state & QtWidgets.QStyle.State_MouseOver)
        base = QtGui.QColor(29, 78, 216)  # ~#1d4ed8
        alpha = int(36 + 84 * (self._hoverProgress if hovered else 0.25))
        tint = QtGui.QColor(base.red(), base.green(), base.blue(), alpha)
        r = option.rect.adjusted(2, 2, -2, -2)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setBrush(tint)
        painter.setPen(QtGui.QPen(QtGui.QColor(base.red(), base.green(), base.blue(), int(alpha * 0.9)), 1))
        painter.drawRoundedRect(r, 6, 6)
        try:
            icon = self.view.style().standardIcon(QtWidgets.QStyle.SP_ArrowForward)
            pix = icon.pixmap(12, 12)
            if not pix.isNull():
                x = r.right() - pix.width() - 8
                y = r.center().y() - pix.height() // 2
                painter.drawPixmap(QtCore.QPoint(x, y), pix)
        except Exception:
            pass
        painter.restore()



class ExpandingTextEdit(QtWidgets.QTextEdit):
    """QTextEdit com animação suave de expansão ao focar."""
    def __init__(self, *args, collapsed_height: int = 56, expanded_height: int = 160, **kwargs):
        super().__init__(*args, **kwargs)
        self._collapsed_h = collapsed_height
        self._expanded_h = expanded_height
        # Política de tamanho e altura inicial via maximumHeight para permitir animação
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumHeight(40)
        self.setMaximumHeight(self._collapsed_h)
        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)
        # Melhora leitura com quebra de palavras
        try:
            self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        except Exception:
            pass
        # Animação
        self._anim = QtCore.QPropertyAnimation(self, b"maximumHeight")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

    def _animate_to(self, h: int) -> None:
        try:
            self._anim.stop()
            self._anim.setStartValue(self.maximumHeight())
            self._anim.setEndValue(h)
            self._anim.start()
        except Exception:
            # Fallback imediato sem animação
            self.setMaximumHeight(h)

    def focusInEvent(self, e: QtGui.QFocusEvent) -> None:  # type: ignore[override]
        self._animate_to(self._expanded_h)
        super().focusInEvent(e)

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:  # type: ignore[override]
        super().focusOutEvent(e)
        self._animate_to(self._collapsed_h)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # Ícone e título da janela
        self.setWindowTitle("🧠 Métricas de Operação")
        try:
            # Caso queira usar um arquivo de ícone futuramente coloque em assets/icon.png
            from pathlib import Path as _P
            icon_path = _P(__file__).resolve().parents[2] / "assets" / "icon.png"
            if icon_path.exists():
                self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        except Exception:
            pass
        self.resize(900, 680)
        self.setMinimumWidth(900)
        self.setMaximumWidth(900)
        self.setMinimumHeight(680)
        self.setMaximumHeight(680)
        self.setStyleSheet(APP_QSS)
        self._overview_labels = {}
        self._overview_config = {}
        self._overview_timestamp = None
        self._overview_cards = []
        self._overview_grid = None

        # Campos de métricas
        self.paletes_agendados = QtWidgets.QSpinBox(); self.paletes_agendados.setRange(0, 10_000)
        self.paletes_produzidos = QtWidgets.QSpinBox(); self.paletes_produzidos.setRange(0, 10_000)
        self.total_veiculos = QtWidgets.QSpinBox(); self.total_veiculos.setRange(0, 10_000)
        self.veiculos_finalizados = QtWidgets.QSpinBox(); self.veiculos_finalizados.setRange(0, 10_000)
        self.descargas_c3 = QtWidgets.QSpinBox(); self.descargas_c3.setRange(0, 10_000)
        self.carregamentos_c3 = QtWidgets.QSpinBox(); self.carregamentos_c3.setRange(0, 10_000)
        self.chamado_granel = QtWidgets.QSpinBox(); self.chamado_granel.setRange(0, 10_000)
        self.chamado_granel.setToolTip("Informe a quantidade de chamados para granel no período")
        self.paletizada = QtWidgets.QSpinBox(); self.paletizada.setRange(0, 10_000)
        self.paletizada.setToolTip("Informe a quantidade de itens paletizados no período")
        self.veiculos_pendentes = QtWidgets.QSpinBox(); self.veiculos_pendentes.setRange(0, 10_000)
        self.fichas_antecipadas = QtWidgets.QSpinBox(); self.fichas_antecipadas.setRange(0, 10_000)
        self.btn_edit_veics = QtWidgets.QPushButton("Editar Veículos…")
        self.btn_edit_veics.clicked.connect(self.on_edit_veiculos)
        self.paletes_pendentes = QtWidgets.QSpinBox(); self.paletes_pendentes.setRange(0, 10_000)
        try:
            # Campos derivados: apenas visualização
            self.descargas_c3.setReadOnly(True)
            self.descargas_c3.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.descargas_c3.setToolTip("Atualizado automaticamente pela quantidade de itens em 'Editar Descargas C3…'")

            self.carregamentos_c3.setReadOnly(True)
            self.carregamentos_c3.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.carregamentos_c3.setToolTip("Atualizado automaticamente pela quantidade de itens em 'Editar Carregamentos C3…'")

            self.veiculos_pendentes.setReadOnly(True)
            self.veiculos_pendentes.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.veiculos_pendentes.setToolTip("Atualizado automaticamente pela quantidade de itens em 'Editar Veículos…'")

            self.fichas_antecipadas.setReadOnly(True)
            self.fichas_antecipadas.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.fichas_antecipadas.setToolTip("Atualizado automaticamente pela quantidade de itens em 'Editar Antecipados…'")

            self.paletes_pendentes.setReadOnly(True)
            self.paletes_pendentes.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.paletes_pendentes.setToolTip("Calculado automaticamente pela soma de Veículos pendentes (Total de Paletes)")
        except Exception:
            pass
        # Campo Observação (expansível ao foco)
        self.observacao = ExpandingTextEdit()
        self.observacao.setObjectName("obsEdit")
        self.observacao.setPlaceholderText("Observação (clique para expandir)")
        self.observacao.setToolTip("Campo livre para observações deste registro")
        # Efeito de sombra sutil
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(22)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QtGui.QColor(15, 23, 42, 60))
            self.observacao.setGraphicsEffect(shadow)
        except Exception:
            pass

        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.clicked.connect(self.on_add)
        self.btn_del = QtWidgets.QPushButton("Excluir Selecionado")
        self.btn_del.setObjectName("danger")
        self.btn_del.clicked.connect(self.on_delete)
        # Botão Exportar
        self.btn_export = QtWidgets.QPushButton("Exportar")
        self.btn_export.clicked.connect(self.on_export)
        # Campo de data de referência para inserir métricas em dias passados/futuros
        self.date_ref = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_ref.setCalendarPopup(True)
        self.date_ref.setDisplayFormat("dd/MM/yyyy")
        self.date_ref.setToolTip("Data que representa estas métricas ao clicar em Adicionar")

        # Alturas mínimas para controles
        for w in (
            self.paletes_agendados,
            self.paletes_produzidos,
            self.total_veiculos,
            self.veiculos_finalizados,
            self.descargas_c3,
            self.carregamentos_c3,
            self.chamado_granel,
            self.paletizada,
            self.veiculos_pendentes,
            self.fichas_antecipadas,
            self.paletes_pendentes,
            self.btn_edit_veics,
            self.btn_add,
            self.btn_del,
            self.btn_export,
        ):
            w.setMinimumHeight(34)
        self.date_ref.setMinimumHeight(34)
        self.lbl_data_ref = QtWidgets.QLabel("Data referência")
        self.lbl_data_ref.setObjectName("dataRefLabel")
        self.lbl_data_ref.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_data_ref.setMinimumHeight(34)
        # Altura mínima para o campo de observação já é controlada pela classe

        form = QtWidgets.QFrame()
        form.setObjectName("cardSurface")
        grid = QtWidgets.QGridLayout(form)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)
        grid.setContentsMargins(24, 20, 24, 16)
        self._apply_card_shadow(form, blur=30, y_offset=12, alpha=28)
        # Coluna 3 (onde fica Observação) ocupa mais espaço
        grid.setColumnStretch(3, 1)
        # Linha 0: Paletes na Agenda | Paletes Produzidos
        grid.addWidget(QtWidgets.QLabel("Qtd Paletes na Agenda"), 0, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.paletes_agendados, 0, 1)
        grid.addWidget(QtWidgets.QLabel("Qtd Paletes Produzidos"), 0, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.paletes_produzidos, 0, 3)
        # Linha 1: Total de Veículos | Veículos finalizados
        grid.addWidget(QtWidgets.QLabel("Total de fichas"), 1, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.total_veiculos, 1, 1)
        grid.addWidget(QtWidgets.QLabel("Fichas finalizadas"), 1, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.veiculos_finalizados, 1, 3)
        # Linha 2: Descargas (C3) | Carregamentos (C3)
        grid.addWidget(QtWidgets.QLabel("Qtd Descargas (C3)"), 2, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # Wrap Descargas (C3) + botão editor
        desc_row = QtWidgets.QHBoxLayout(); desc_row.setSpacing(8)
        self.btn_edit_descargas = QtWidgets.QPushButton("Editar Descargas C3…")
        self.btn_edit_descargas.clicked.connect(self.on_edit_descargas)
        desc_row.addWidget(self.descargas_c3)
        desc_row.addWidget(self.btn_edit_descargas)
        desc_wrap = QtWidgets.QWidget(); desc_wrap.setLayout(desc_row)
        grid.addWidget(desc_wrap, 2, 1)
        grid.addWidget(QtWidgets.QLabel("Qtd Carregamentos (C3)"), 2, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # Wrap Carregamentos (C3) + botão editor
        carg_row = QtWidgets.QHBoxLayout(); carg_row.setSpacing(8)
        self.btn_edit_carg = QtWidgets.QPushButton("Editar Carregamentos C3…")
        self.btn_edit_carg.clicked.connect(self.on_edit_carregamentos)
        carg_row.addWidget(self.carregamentos_c3)
        carg_row.addWidget(self.btn_edit_carg)
        carg_wrap = QtWidgets.QWidget(); carg_wrap.setLayout(carg_row)
        grid.addWidget(carg_wrap, 2, 3)
        # Linha 3: Paletes Pendentes | Veículos pendentes (com botão editor)
        veic_row = QtWidgets.QHBoxLayout()
        veic_row.setSpacing(8)
        veic_row.addWidget(self.veiculos_pendentes)
        veic_row.addWidget(self.btn_edit_veics)
        veic_wrap = QtWidgets.QWidget(); veic_wrap.setLayout(veic_row)
        grid.addWidget(QtWidgets.QLabel("Paletes Pendentes"), 3, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.paletes_pendentes, 3, 1)
        grid.addWidget(QtWidgets.QLabel("Veículos pendentes"), 3, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(veic_wrap, 3, 3)
        # Linha 4: Fichas antecipadas (com editor de veículos antecipados)
        grid.addWidget(QtWidgets.QLabel("Fichas antecipadas"), 4, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ant_row = QtWidgets.QHBoxLayout(); ant_row.setSpacing(8)
        self.btn_edit_antecipados = QtWidgets.QPushButton("Editar Antecipados…")
        self.btn_edit_antecipados.clicked.connect(self.on_edit_antecipados)
        ant_row.addWidget(self.fichas_antecipadas)
        ant_row.addWidget(self.btn_edit_antecipados)
        ant_wrap = QtWidgets.QWidget(); ant_wrap.setLayout(ant_row)
        grid.addWidget(ant_wrap, 4, 1)
        # Observação à direita de Fichas antecipadas
        grid.addWidget(QtWidgets.QLabel("Observação"), 4, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.observacao, 4, 3)
        # Linha 5: Chamado Granel | Paletizada
        grid.addWidget(QtWidgets.QLabel("Veículo Granel"), 5, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.chamado_granel, 5, 1)
        grid.addWidget(QtWidgets.QLabel("Veículo Paletizada"), 5, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(self.paletizada, 5, 3)

        self.date_ref.setMaximumWidth(150)

        # Table
        self.table = QtWidgets.QTableView()
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        # QTableView não possui setUniformRowHeights; desliga quebra de linha para ganho de performance
        self.table.setWordWrap(False)
        self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table.doubleClicked.connect(self.on_table_double_click)
        # Destaque interativo nas colunas com ação de duplo clique
        self.table.setMouseTracking(True)
        self._interactive_cols = {5, 6, 9, 11, 13}
        self._delegate = InteractiveHighlightDelegate(self.table, self._interactive_cols)
        self.table.setItemDelegate(self._delegate)
        # Atualiza hover/cursor dinamicamente
        self.table.viewport().installEventFilter(self)

        # Barra de paginação
        pager = QtWidgets.QHBoxLayout()
        pager.setContentsMargins(0, 0, 0, 0)
        pager.setSpacing(10)
        pager_left = QtWidgets.QHBoxLayout(); pager_left.setSpacing(6)
        pager_left.addWidget(QtWidgets.QLabel("Mostrar"))
        self.page_size = QtWidgets.QComboBox()
        self.page_size.addItems(["20", "40", "60", "80", "100"])
        self.page_size.setCurrentText("20")
        self.page_size.currentTextChanged.connect(self.on_page_size_changed)
        pager_left.addWidget(self.page_size)
        pager_left.addWidget(QtWidgets.QLabel("registros"))
        pager.addLayout(pager_left)
        pager.addStretch(1)
        self.btn_prev = QtWidgets.QPushButton("Anterior")
        self.btn_prev.clicked.connect(self.on_prev_page)
        self.lbl_page = QtWidgets.QLabel("Página 1 de 1")
        self.btn_next = QtWidgets.QPushButton("Próxima")
        self.btn_next.clicked.connect(self.on_next_page)
        self._set_button_variant(self.btn_prev, "ghost")
        self._set_button_variant(self.btn_next, "ghost")
        pager.addWidget(self.btn_prev)
        pager.addWidget(self.lbl_page)
        pager.addWidget(self.btn_next)
        pager_w = QtWidgets.QWidget(); pager_w.setLayout(pager)

        # Barra de comandos
        self.toggle_view_btn = QtWidgets.QPushButton("Tabela")
        self.toggle_view_btn.setMinimumHeight(34)
        self.toggle_view_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggle_view_btn.setToolTip("Ver registros em tabela")
        self.toggle_view_btn.clicked.connect(self.on_toggle_view)
        self._set_button_variant(self.toggle_view_btn, "ghost")

        command_bar = QtWidgets.QFrame()
        command_bar.setObjectName("cardSurface")
        command_bar.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        cmd_layout = QtWidgets.QHBoxLayout(command_bar)
        cmd_layout.setContentsMargins(24, 12, 24, 12)
        cmd_layout.setSpacing(18)

        actions_wrap = QtWidgets.QWidget()
        actions_layout = QtWidgets.QHBoxLayout(actions_wrap)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(12)
        for btn in (self.btn_add, self.btn_del, self.btn_export):
            btn.setMinimumWidth(70)
            actions_layout.addWidget(btn)
        cmd_layout.addWidget(actions_wrap, 0, QtCore.Qt.AlignLeft)

        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.VLine)
        divider.setFrameShadow(QtWidgets.QFrame.Plain)
        divider.setStyleSheet("color: rgba(15, 23, 42, 40);")
        divider.setFixedHeight(34)
        cmd_layout.addWidget(divider)

        date_widget = QtWidgets.QWidget()
        date_layout = QtWidgets.QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(8)
        date_layout.addWidget(self.lbl_data_ref)
        self.date_ref.setMinimumWidth(160)
        self.date_ref.setMaximumWidth(200)
        date_layout.addWidget(self.date_ref)
        cmd_layout.addWidget(date_widget, 0, QtCore.Qt.AlignVCenter)

        cmd_layout.addStretch(1)
        self.toggle_view_btn.setMinimumWidth(140)
        cmd_layout.addWidget(self.toggle_view_btn, 0, QtCore.Qt.AlignRight)
        self._apply_card_shadow(command_bar, blur=20, y_offset=6, alpha=24)
        self._command_bar = command_bar

        # Layou
        central = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(central)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)
        # Cabeçalho do painel (container centralizado)
        header_container = QtWidgets.QWidget()
        header_container.setObjectName("appHeader")
        header_layout = QtWidgets.QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 12, 20, 12)
        header_layout.setSpacing(8)
        header = QtWidgets.QLabel("<span style='font-size:15px;'>🧠 Controle de registro Recebimento <strong>[ Banco de dados ]</strong></span>")
        header.setObjectName("appTitle")
        header.setAlignment(QtCore.Qt.AlignCenter)
        btn_grafico = QtWidgets.QPushButton("Gráfico apresentação")
        btn_grafico.setObjectName("headerBtn")
        btn_grafico.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_grafico.setToolTip("Abrir gráficos (index.html)")
        btn_grafico.clicked.connect(self.open_index_html)
        btn_grafico.setMinimumHeight(36)
        btn_grafico.setMinimumWidth(120)
        try:
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
            btn_grafico.setIcon(icon)
        except Exception:
            pass
        header_layout.addStretch(1)
        header_layout.addWidget(header, 0, QtCore.Qt.AlignCenter)
        header_layout.addStretch(1)
        header_layout.addWidget(btn_grafico, 0, QtCore.Qt.AlignRight)
        lay.addWidget(header_container, alignment=QtCore.Qt.AlignHCenter)
        self._header_container = header_container
        overview_panel = self._build_overview_panel()
        lay.addWidget(overview_panel)
        lay.addWidget(self._command_bar)

        alimentacao_page = QtWidgets.QWidget()
        alimentacao_layout = QtWidgets.QVBoxLayout(alimentacao_page)
        alimentacao_layout.setContentsMargins(0, 0, 0, 0)
        alimentacao_layout.setSpacing(16)
        alimentacao_layout.addWidget(form)

        tabela_page = QtWidgets.QWidget()
        tabela_layout = QtWidgets.QVBoxLayout(tabela_page)
        tabela_layout.setContentsMargins(0, 0, 0, 0)
        tabela_layout.setSpacing(12)
        tabela_layout.addWidget(self.table, 1)
        tabela_layout.addWidget(pager_w)

        self._view_stack = QtWidgets.QStackedWidget()
        self._view_stack.addWidget(alimentacao_page)
        self._view_stack.addWidget(tabela_page)
        lay.addWidget(self._view_stack, 1)
        self.setCentralWidget(central)
        self._relayout_overview_cards()

        # Inicia API local para uso pela interface web
        self._api = ApiServer()
        try:
            self._api.start()
        except Exception:
            pass

        # Repo/session
        init_db()
        self._session_cm = get_session()
        self._session = next(self._session_cm)
        self.repo = MetricaRepository(self._session)
        self.veic_repo = VeiculoPendenteRepository(self._session)
        self.desc_repo = VeiculoDescargaC3Repository(self._session)
        self.antec_repo = VeiculoAntecipadoRepository(self._session)
        self.carg_repo = VeiculoCarregamentoC3Repository(self._session)

        # buffers temporários antes de salvar (veiculo, quantidade, porcentagem)
        self._buffer_veiculos = []
        self._buffer_descargas = []
        self._buffer_antecipados = []
        self._buffer_carregamentos = []

        # Estado de paginação
        self._page_size_val = int(self.page_size.currentText())
        self._current_page = 1

        self.model = MetricaTableModel([])
        self.table.setModel(self.model)
        self._columns_sized = False
        self._apply_fast_column_layout()
        self.refresh()

    def _build_overview_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        panel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        layout.addLayout(grid)
        self._overview_grid = grid
        self._overview_cards.clear()
        self._overview_labels.clear()
        self._overview_config.clear()
        metrics = [
            ("Paletes Produzidos", "paletes_produzidos", 2),
            ("Fichas finalizadas", "veiculos_finalizados", 4),
            ("Veículos pendentes", "veiculos_pendentes", 9),
            ("Paletes pendentes", "paletes_pendentes", 10),
        ]
        for title, key, idx in metrics:
            card, value_label = self._create_metric_card(title)
            self._overview_cards.append(card)
            self._overview_labels[key] = value_label
            self._overview_config[key] = idx
        self._relayout_overview_cards()
        self._overview_timestamp = QtWidgets.QLabel("Última atualização: —")
        self._overview_timestamp.setObjectName("metricTimestamp")
        layout.addWidget(self._overview_timestamp, 0, QtCore.Qt.AlignRight)
        return panel

    def _create_metric_card(self, title: str) -> tuple[QtWidgets.QFrame, QtWidgets.QLabel]:
        card = QtWidgets.QFrame()
        card.setObjectName("cardSurface")
        card.setMinimumWidth(160)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(6)
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("metricTitle")
        value_label = QtWidgets.QLabel("—")
        value_label.setObjectName("metricValue")
        value_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch(1)
        self._apply_card_shadow(card, blur=26, y_offset=8, alpha=28)
        return card, value_label

    def _apply_card_shadow(self, widget: QtWidgets.QWidget, *, blur: int = 24, y_offset: int = 8, alpha: int = 32) -> None:
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(0)
            shadow.setYOffset(y_offset)
            shadow.setColor(QtGui.QColor(15, 23, 42, alpha))
            widget.setGraphicsEffect(shadow)
        except Exception:
            pass

    def _set_button_variant(self, button: QtWidgets.QAbstractButton | None, variant: str) -> None:
        if button is None:
            return
        button.setProperty("variant", variant)
        try:
            style = button.style()
            style.unpolish(button)
            style.polish(button)
        except Exception:
            pass

    def _fmt_metric(self, value: int | None) -> str:
        if value is None:
            return "—"
        try:
            return f"{int(value):,}".replace(",", ".")
        except Exception:
            return str(value)

    def _update_overview_from_rows(self, rows: list[tuple]) -> None:
        if not self._overview_labels:
            return
        data = {key: None for key in self._overview_config.keys()}
        timestamp = "—"
        if rows:
            latest = rows[0]
            for key, idx in self._overview_config.items():
                try:
                    data[key] = latest[idx]
                except Exception:
                    data[key] = None
            if len(latest) > 12:
                raw = latest[12]
                if isinstance(raw, str) and raw:
                    timestamp = raw
        for key, label in self._overview_labels.items():
            label.setText(self._fmt_metric(data.get(key)))
        if self._overview_timestamp is not None:
            self._overview_timestamp.setText(f"Última atualização: {timestamp}")

    def _relayout_overview_cards(self, available_width: int | None = None) -> None:
        if not self._overview_grid or not self._overview_cards:
            return
        grid = self._overview_grid
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().setParent(grid.parentWidget())
        total_cards = len(self._overview_cards)
        if available_width is None:
            available_width = self.centralWidget().width() if self.centralWidget() else self.width()
        min_card = 220
        columns = max(1, min(total_cards, max(1, available_width // min_card)))
        for index, card in enumerate(self._overview_cards):
            row = index // columns
            col = index % columns
            grid.addWidget(card, row, col)
        for col in range(columns):
            grid.setColumnStretch(col, 1)

    def open_index_html(self) -> None:
        from pathlib import Path
        try:
            root = Path(__file__).resolve().parents[2]
            index = root / "interface" / "index.html"
            if index.exists():
                QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(index)))
            else:
                QtWidgets.QMessageBox.warning(self, "Arquivo não encontrado", f"Não achei: {index}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro ao abrir", str(e))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # type: ignore[override]
        try:
            self._session.close()
        except Exception:
            pass
        try:
            if hasattr(self, "_api") and self._api:
                self._api.stop()
        except Exception:
            pass
        event.accept()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # type: ignore[override]
        try:
            cw = self.centralWidget().width() if self.centralWidget() else self.width()
            desired = int(max(200, cw * 0.95))
            if hasattr(self, "_header_container") and self._header_container:
                self._header_container.setFixedWidth(desired)
            self._relayout_overview_cards(cw)
        except Exception:
            pass
        super().resizeEvent(event)

    def refresh(self) -> None:
        # Atualiza total e páginas
        total = self.repo.count()
        per_page = max(1, int(self._page_size_val))
        total_pages = max(1, (total + per_page - 1) // per_page)
        # Garante página válida
        if self._current_page > total_pages:
            self._current_page = total_pages
        if self._current_page < 1:
            self._current_page = 1
        offset = (self._current_page - 1) * per_page

        rows = []
        for m in self.repo.list_page(limit=per_page, offset=offset):
            # Agora criado_em já está salvo como data referência (midnight) ou horário real local
            try:
                dt = m.criado_em
                if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
                    criado_fmt = dt.strftime("%d/%m/%Y")
                else:
                    criado_fmt = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                criado_fmt = str(m.criado_em)
            rows.append(
                (
                    m.id,
                    m.paletes_agendados,
                    m.paletes_produzidos,
                    m.total_veiculos,
                    m.veiculos_finalizados,
                    m.descargas_c3,
                    m.carregamentos_c3,
                    m.chamado_granel,
                    m.paletizada,
                    m.veiculos_pendentes,
                    m.paletes_pendentes,
                    getattr(m, "fichas_antecipadas", 0),
                    criado_fmt,
                    "Editar | Excluir",
                )
            )
        self.model.set_rows(rows)
        # Atualiza barra de paginação
        self.lbl_page.setText(f"Página {self._current_page} de {total_pages}")
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(self._current_page < total_pages)
        self._update_overview_from_rows(rows)

    def _apply_fast_column_layout(self) -> None:
        if getattr(self, "_columns_sized", False):
            return
        header = self.table.horizontalHeader()
        fm = self.table.fontMetrics()
        try:
            for i, text in enumerate(MetricaTableModel.HEADERS):
                w = fm.horizontalAdvance(text) + 28
                self.table.setColumnWidth(i, w)
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Interactive)
            header.setStretchLastSection(True)
        finally:
            self._columns_sized = True

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:  # type: ignore[override]
        if obj is self.table.viewport() and event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.Leave):
            if event.type() == QtCore.QEvent.Leave:
                self._delegate.setHoveredIndex(None)
                self.table.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                pos = event.pos()  # type: ignore[attr-defined]
                idx = self.table.indexAt(pos)
                self._delegate.setHoveredIndex(idx if idx.isValid() else None)
                if idx.isValid() and idx.column() in self._interactive_cols:
                    self.table.viewport().setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                else:
                    self.table.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        return super().eventFilter(obj, event)
    def on_page_size_changed(self, text: str) -> None:
        try:
            self._page_size_val = int(text)
        except ValueError:
            self._page_size_val = 20
        self._current_page = 1
        self.refresh()

    def on_prev_page(self) -> None:
        self._current_page = max(1, self._current_page - 1)
        self.refresh()

    def on_next_page(self) -> None:
        # O refresh recalcula total_pages; aqui apenas incrementa e valida lá
        self._current_page += 1
        self.refresh()

    def on_toggle_view(self) -> None:
        if not hasattr(self, "_view_stack") or self._view_stack is None:
            return
        current = self._view_stack.currentIndex()
        if current == 0:
            self._view_stack.setCurrentIndex(1)
            if hasattr(self, "toggle_view_btn") and self.toggle_view_btn:
                self.toggle_view_btn.setText("Alimentação")
                self.toggle_view_btn.setToolTip("Voltar para o painel de alimentação")
            self.refresh()
        else:
            self._view_stack.setCurrentIndex(0)
            if hasattr(self, "toggle_view_btn") and self.toggle_view_btn:
                self.toggle_view_btn.setText("Tabela")
                self.toggle_view_btn.setToolTip("Ver registros em tabela")

    def on_add(self) -> None:
        class Payload(BaseModel):
            paletes_agendados: int
            paletes_produzidos: int
            total_veiculos: int
            veiculos_finalizados: int
            fichas_antecipadas: int
            observacao: str | None
            descargas_c3: int
            carregamentos_c3: int
            chamado_granel: int
            paletizada: int
            veiculos_pendentes: int

            @field_validator(
                "paletes_agendados",
                "paletes_produzidos",
                "total_veiculos",
                "veiculos_finalizados",
                "fichas_antecipadas",
                "descargas_c3",
                "carregamentos_c3",
                "chamado_granel",
                "paletizada",
                "veiculos_pendentes",
            )
            @classmethod
            def non_negative(cls, v: int) -> int:
                if v < 0:
                    raise ValueError("Valor não pode ser negativo")
                return v

        data = {
            "paletes_agendados": int(self.paletes_agendados.value()),
            "paletes_produzidos": int(self.paletes_produzidos.value()),
            "total_veiculos": int(self.total_veiculos.value()),
            "veiculos_finalizados": int(self.veiculos_finalizados.value()),
            "fichas_antecipadas": int(self.fichas_antecipadas.value()),
            "observacao": (self.observacao.toPlainText().strip() or None),
            "descargas_c3": int(self.descargas_c3.value()),
            "carregamentos_c3": int(self.carregamentos_c3.value()),
            "chamado_granel": int(self.chamado_granel.value()),
            "paletizada": int(self.paletizada.value()),
            "veiculos_pendentes": int(self.veiculos_pendentes.value()),
        }

        try:
            payload = Payload(**data)
        except ValidationError as ve:
            QtWidgets.QMessageBox.warning(self, "Dados inválidos", "\n".join([e['msg'] for e in ve.errors()]))
            return

        # Define criado_em exatamente como a Data referência (00:00 local) sem converter para UTC
        # Assim o valor armazenado no banco corresponde 1:1 ao dia escolhido.
        from datetime import datetime
        qd = self.date_ref.date()
        criado_em = datetime(qd.year(), qd.month(), qd.day(), 0, 0, 0)

        try:
            created = self.repo.add(
                paletes_agendados=payload.paletes_agendados,
                paletes_produzidos=payload.paletes_produzidos,
                total_veiculos=payload.total_veiculos,
                veiculos_finalizados=payload.veiculos_finalizados,
                fichas_antecipadas=payload.fichas_antecipadas,
                observacao=payload.observacao,
                descargas_c3=payload.descargas_c3,
                carregamentos_c3=payload.carregamentos_c3,
                chamado_granel=payload.chamado_granel,
                paletizada=payload.paletizada,
                veiculos_pendentes=payload.veiculos_pendentes,
                criado_em=criado_em,
            )
            # Salva veículos pendentes vinculados à métrica criada (agora com quantidade)
            for veiculo, qtd, pct in self._buffer_veiculos:
                try:
                    self.veic_repo.add(created.id, veiculo, int(pct), quantidade=int(qtd))
                except Exception:
                    # continua, mas informa depois
                    pass
            # Salva veículos de Descarga C3 vinculados
            for veiculo, qtd, pct in self._buffer_descargas:
                try:
                    self.desc_repo.add(created.id, veiculo, int(pct), quantidade=int(qtd))
                except Exception:
                    pass
            # Salva veículos antecipados vinculados (agora com quantidade)
            for veiculo, qtd, pct in self._buffer_antecipados:
                try:
                    self.antec_repo.add(created.id, veiculo, int(pct), quantidade=int(qtd))
                except Exception:
                    pass
            # Salva veículos de Carregamento C3 vinculados
            for veiculo, qtd, pct in self._buffer_carregamentos:
                try:
                    self.carg_repo.add(created.id, veiculo, int(pct), quantidade=int(qtd))
                except Exception:
                    pass
        except Exception as e:  # pragma: no cover
            QtWidgets.QMessageBox.critical(self, "Erro ao salvar", str(e))
            return

        for w in (
            self.paletes_agendados,
            self.paletes_produzidos,
            self.total_veiculos,
            self.veiculos_finalizados,
            self.descargas_c3,
            self.carregamentos_c3,
            self.chamado_granel,
            self.paletizada,
            self.veiculos_pendentes,
            self.fichas_antecipadas,
            self.paletes_pendentes,
        ):
            w.setValue(0)
        self.observacao.setPlainText("")
        self._buffer_veiculos = []
        self._buffer_descargas = []
        self._buffer_antecipados = []
        self._buffer_carregamentos = []
        # Após inserir, volta para a primeira página (mais recentes)
        self._current_page = 1
        self.refresh()

    def on_edit_veiculos(self) -> None:
        # Abre o diálogo de edição para preencher veículos pendentes no buffer (mantendo quantidade)
        dlg = VeiculosDialog(self, initial=self._buffer_veiculos, read_only=False, title="Editar Veículos Pendentes")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            norm: list[tuple[str, int, int]] = []
            for tup in dlg.get_rows():
                try:
                    if len(tup) == 3:
                        v, q, pct = tup  # type: ignore[misc]
                        norm.append((str(v), int(q), int(pct)))
                    elif len(tup) == 2:
                        v, pct = tup  # type: ignore[misc]
                        norm.append((str(v), 0, int(pct)))
                except Exception:
                    continue
            self._buffer_veiculos = norm
            # Alimenta automaticamente Veículos pendentes com a contagem de linhas
            try:
                self.veiculos_pendentes.setValue(len(self._buffer_veiculos))
            except Exception:
                pass
            # Atualiza prévia de Paletes Pendentes (soma das quantidades no buffer)
            try:
                total_pal = sum(int(q or 0) for _v, q, _p in norm)
                self.paletes_pendentes.setValue(int(total_pal))
            except Exception:
                pass

    def on_edit_descargas(self) -> None:
        # Abre diálogo para editar veículos de Descarga C3 no buffer
        dlg = VeiculosDialog(self, initial=self._buffer_descargas, read_only=False, title="Veículos Descarga C3")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self._buffer_descargas = dlg.get_rows()
            # Alimenta automaticamente a Qtd Descargas (C3) com a contagem de linhas
            try:
                self.descargas_c3.setValue(len(self._buffer_descargas))
            except Exception:
                pass

    def on_edit_antecipados(self) -> None:
        # Abre diálogo para editar veículos antecipados no buffer (mantendo quantidade)
        dlg = VeiculosDialog(self, initial=self._buffer_antecipados, read_only=False, title="Veículos Antecipados")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            norm: list[tuple[str, int, int]] = []
            for tup in dlg.get_rows():
                try:
                    if len(tup) == 3:
                        v, q, pct = tup  # type: ignore[misc]
                        norm.append((str(v), int(q), int(pct)))
                    elif len(tup) == 2:
                        v, pct = tup  # type: ignore[misc]
                        norm.append((str(v), 0, int(pct)))
                except Exception:
                    continue
            self._buffer_antecipados = norm
            # Alimenta automaticamente Fichas antecipadas com a contagem de linhas
            try:
                self.fichas_antecipadas.setValue(len(self._buffer_antecipados))
            except Exception:
                pass

    def on_edit_carregamentos(self) -> None:
        # Abre diálogo para editar veículos de Carregamento C3 no buffer
        dlg = VeiculosDialog(self, initial=self._buffer_carregamentos, read_only=False, title="Veículos Carregamento C3")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self._buffer_carregamentos = dlg.get_rows()
            # Alimenta automaticamente a Qtd Carregamentos (C3) com a contagem de linhas
            try:
                self.carregamentos_c3.setValue(len(self._buffer_carregamentos))
            except Exception:
                pass

    def on_table_double_click(self, index: QtCore.QModelIndex) -> None:
        if not index.isValid():
            return
        col = index.column()
        row = index.row()
        metrica_id = int(self.model._rows[row][0])
        # Coluna de ações
        if col == 13:
            self._show_actions_menu(row, metrica_id, index)
            return
        # Descargas (C3) coluna 5 abre veículos de descarga C3
        if col == 5:
            items = self.desc_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Descargas C3 (Métrica {metrica_id})")
            dlg.exec()
            return
        # Veículos Pendentes coluna 7 (0-based)
        if col == 9:
            items = self.veic_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Veículos Pendentes (Métrica {metrica_id})")
            dlg.exec()
            return
        # Fichas antecipadas coluna 9 (0-based)
        if col == 11:
            items = self.antec_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Veículos Antecipados (Métrica {metrica_id})")
            dlg.exec()
            return
        # Carregamentos (C3) coluna 6 (0-based)
        if col == 6:
            items = self.carg_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Carregamentos C3 (Métrica {metrica_id})")
            dlg.exec()

    def on_delete(self) -> None:
        idx = self.table.currentIndex()
        if not idx.isValid():
            QtWidgets.QMessageBox.information(self, "Seleção", "Selecione uma linha para excluir.")
            return
        row = idx.row()
        metrica_id = self.model._rows[row][0]
        ok = self.repo.delete(int(metrica_id))
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Exclusão", "Registro não encontrado.")
        # Se exclusão afetar última página, refresh ajusta a página atual
        self.refresh()

    # ==== Fluxo de Ações (Editar/Excluir) na tabela ====
    def _show_actions_menu(self, row: int, metrica_id: int, index: QtCore.QModelIndex) -> None:
        menu = QtWidgets.QMenu(self)
        act_edit = menu.addAction("Editar…")
        act_del = menu.addAction("Excluir…")
        pos = self.table.viewport().mapToGlobal(self.table.visualRect(index).bottomLeft())
        action = menu.exec(pos)
        if action is act_edit:
            self._edit_record(metrica_id)
        elif action is act_del:
            self._delete_record(metrica_id)

    def _delete_record(self, metrica_id: int) -> None:
        resp = QtWidgets.QMessageBox.question(
            self,
            "Excluir registro",
            f"Tem certeza que deseja excluir o registro ID {metrica_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if resp != QtWidgets.QMessageBox.Yes:
            return
        ok = self.repo.delete(int(metrica_id))
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Exclusão", "Registro não encontrado.")
        self.refresh()

    def _edit_record(self, metrica_id: int) -> None:
        # Carrega registro e respectivos detalhes em memória
        m = self.repo.get(int(metrica_id))
        if not m:
            QtWidgets.QMessageBox.warning(self, "Edição", "Registro não encontrado.")
            return
        # Preenche formulário com dados do registro
        self.paletes_agendados.setValue(int(m.paletes_agendados))
        self.paletes_produzidos.setValue(int(m.paletes_produzidos))
        self.total_veiculos.setValue(int(m.total_veiculos))
        self.veiculos_finalizados.setValue(int(m.veiculos_finalizados))
        self.descargas_c3.setValue(int(m.descargas_c3))
        self.carregamentos_c3.setValue(int(m.carregamentos_c3))
        self.chamado_granel.setValue(int(getattr(m, "chamado_granel", 0)))
        self.paletizada.setValue(int(getattr(m, "paletizada", 0)))
        self.veiculos_pendentes.setValue(int(m.veiculos_pendentes))
        self.fichas_antecipadas.setValue(int(getattr(m, "fichas_antecipadas", 0)))
        self.paletes_pendentes.setValue(int(m.paletes_pendentes))
        self.observacao.setPlainText(m.observacao or "")
        # Data referência = data do registro
        try:
            from PySide6 import QtCore as _QtC
            d = _QtC.QDate(m.criado_em.year, m.criado_em.month, m.criado_em.day)
            self.date_ref.setDate(d)
        except Exception:
            pass
        # Buffers com listas do registro para permitir regravação
        veics = self.veic_repo.list_by_metrica(m.id)
        self._buffer_veiculos = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in veics]
        descs = self.desc_repo.list_by_metrica(m.id)
        self._buffer_descargas = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in descs]
        ants = self.antec_repo.list_by_metrica(m.id)
        self._buffer_antecipados = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in ants]
        cars = self.carg_repo.list_by_metrica(m.id)
        self._buffer_carregamentos = [(it.veiculo, int(getattr(it, 'quantidade', 0)), int(it.porcentagem)) for it in cars]

        # Troca botão Adicionar -> Salvar alterações e guarda id em edição
        self._editing_id = int(m.id)
        self.btn_add.setText("Salvar alterações")
        try:
            self.btn_add.clicked.disconnect()
        except Exception:
            pass
        self.btn_add.clicked.connect(self.on_save_edit)

    def on_save_edit(self) -> None:
        mid = getattr(self, "_editing_id", None)
        if not mid:
            return
        # Validação simples e coleta
        paletes_agendados = int(self.paletes_agendados.value())
        paletes_produzidos = int(self.paletes_produzidos.value())
        total_veiculos = int(self.total_veiculos.value())
        veiculos_finalizados = int(self.veiculos_finalizados.value())
        fichas_antecipadas = int(self.fichas_antecipadas.value())
        descargas_c3 = int(self.descargas_c3.value())
        carregamentos_c3 = int(self.carregamentos_c3.value())
        chamado_granel = int(self.chamado_granel.value())
        paletizada = int(self.paletizada.value())
        veiculos_pendentes = int(self.veiculos_pendentes.value())
        observacao = (self.observacao.toPlainText().strip() or None)
        # Atualiza métrica principal
        from datetime import datetime as _dt
        qd = self.date_ref.date()
        criado_em = _dt(qd.year(), qd.month(), qd.day(), 0, 0, 0)
        ok = self.repo.update(
            mid,
            paletes_agendados=paletes_agendados,
            paletes_produzidos=paletes_produzidos,
            total_veiculos=total_veiculos,
            veiculos_finalizados=veiculos_finalizados,
            fichas_antecipadas=fichas_antecipadas,
            observacao=observacao,
            descargas_c3=descargas_c3,
            carregamentos_c3=carregamentos_c3,
            chamado_granel=chamado_granel,
            paletizada=paletizada,
            veiculos_pendentes=veiculos_pendentes,
            criado_em=criado_em,
        )
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Edição", "Falha ao salvar alterações.")
            return
        # Regrava listas vinculadas: remove tudo e insere do buffer atual
        try:
            self.veic_repo.delete_by_metrica(mid)
            for v, q, p in self._buffer_veiculos:
                self.veic_repo.add(mid, v, int(p), quantidade=int(q))
        except Exception:
            pass
        try:
            self.desc_repo.delete_by_metrica(mid)
            for v, q, p in self._buffer_descargas:
                self.desc_repo.add(mid, v, int(p), quantidade=int(q))
        except Exception:
            pass
        try:
            self.antec_repo.delete_by_metrica(mid)
            for v, q, p in self._buffer_antecipados:
                self.antec_repo.add(mid, v, int(p), quantidade=int(q))
        except Exception:
            pass
        try:
            self.carg_repo.delete_by_metrica(mid)
            for v, q, p in self._buffer_carregamentos:
                self.carg_repo.add(mid, v, int(p), quantidade=int(q))
        except Exception:
            pass
        # Finaliza edição: volta botão ao estado original
        try:
            self.btn_add.clicked.disconnect()
        except Exception:
            pass
        self.btn_add.setText("Adicionar")
        self.btn_add.clicked.connect(self.on_add)
        self._editing_id = None
        # Limpa campos após salvar alterações (mesmo comportamento do Adicionar)
        for w in (
            self.paletes_agendados,
            self.paletes_produzidos,
            self.total_veiculos,
            self.veiculos_finalizados,
            self.descargas_c3,
            self.carregamentos_c3,
            self.chamado_granel,
            self.paletizada,
            self.veiculos_pendentes,
            self.fichas_antecipadas,
            self.paletes_pendentes,
        ):
            w.setValue(0)
        self.observacao.setPlainText("")
        self._buffer_veiculos = []
        self._buffer_descargas = []
        self._buffer_antecipados = []
        self._buffer_carregamentos = []
        self.refresh()

    def on_export(self) -> None:
        # Escolhe o arquivo de saída
        suggested = QtCore.QDir.homePath() + "/export-metricas.xlsx"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exportar para XLSX",
            suggested,
            "Planilha Excel (*.xlsx)"
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"

        # Tenta importar openpyxl on-demand
        try:
            from openpyxl import Workbook  # type: ignore
        except Exception:
            QtWidgets.QMessageBox.critical(
                self,
                "Dependência ausente",
                "Para exportar em XLSX, instale o pacote 'openpyxl'."
            )
            return

        try:
            # Busca todos os dados diretamente via sessão
            metricas = self._session.execute(select(Metrica).order_by(Metrica.id.asc())).scalars().all()
            pendentes = self._session.execute(select(VeiculoPendente).order_by(VeiculoPendente.id.asc())).scalars().all()
            descargas = self._session.execute(select(VeiculoDescargaC3).order_by(VeiculoDescargaC3.id.asc())).scalars().all()
            antecip = self._session.execute(select(VeiculoAntecipado).order_by(VeiculoAntecipado.id.asc())).scalars().all()

            wb = Workbook()
            # Remove a planilha inicial padrão
            try:
                wb.remove(wb.active)
            except Exception:
                pass

            def add_sheet(title: str, headers: list[str], rows: list[list]):
                ws = wb.create_sheet(title=title[:31] if title else "Sheet")
                ws.append(headers)
                for r in rows:
                    ws.append(r)

            # Sheet Métricas
            add_sheet(
                "Metricas",
                [
                    "id",
                    "paletes_agendados",
                    "paletes_produzidos",
                    "total_veiculos",
                    "veiculos_finalizados",
                    "descargas_c3",
                    "carregamentos_c3",
                    "veiculos_pendentes",
                    "paletes_pendentes",
                    "fichas_antecipadas",
                    "observacao",
                    "criado_em",
                ],
                [
                    [
                        m.id,
                        m.paletes_agendados,
                        m.paletes_produzidos,
                        m.total_veiculos,
                        m.veiculos_finalizados,
                        m.descargas_c3,
                        m.carregamentos_c3,
                        m.veiculos_pendentes,
                        m.paletes_pendentes,
                        getattr(m, "fichas_antecipadas", 0),
                        (m.observacao or ""),
                        (m.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(m, "criado_em") and m.criado_em else ""),
                    ]
                    for m in metricas
                ],
            )

            # Sheet Veículos Pendentes
            add_sheet(
                "VeiculosPendentes",
                ["id", "metrica_id", "veiculo", "quantidade", "porcentagem", "criado_em"],
                [
                    [
                        v.id,
                        v.metrica_id,
                        v.veiculo,
                        int(getattr(v, "quantidade", 0)),
                        int(v.porcentagem),
                        (v.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(v, "criado_em") and v.criado_em else ""),
                    ]
                    for v in pendentes
                ],
            )

            # Sheet Descargas C3
            add_sheet(
                "DescargasC3",
                ["id", "metrica_id", "veiculo", "quantidade", "porcentagem", "criado_em"],
                [
                    [
                        d.id,
                        d.metrica_id,
                        d.veiculo,
                        int(getattr(d, "quantidade", 0)),
                        int(d.porcentagem),
                        (d.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(d, "criado_em") and d.criado_em else ""),
                    ]
                    for d in descargas
                ],
            )

            # Sheet Antecipados
            add_sheet(
                "Antecipados",
                ["id", "metrica_id", "veiculo", "quantidade", "porcentagem", "criado_em"],
                [
                    [
                        a.id,
                        a.metrica_id,
                        a.veiculo,
                        int(getattr(a, "quantidade", 0)),
                        int(a.porcentagem),
                        (a.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(a, "criado_em") and a.criado_em else ""),
                    ]
                    for a in antecip
                ],
            )

            wb.save(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro ao exportar", str(e))
            return

        QtWidgets.QMessageBox.information(self, "Exportação", f"Arquivo salvo em:\n{path}")


def run() -> int:
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
