from __future__ import annotations
import sys
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets
from datetime import timezone, timedelta

from ..db.database import init_db, get_session
from ..db.repository import MetricaRepository
from .veiculos_dialog import VeiculosDialog
from ..db.repository import VeiculoPendenteRepository, VeiculoDescargaC3Repository, VeiculoAntecipadoRepository
from pydantic import BaseModel, field_validator, ValidationError
from .theme import DARK_QSS
from ..api.server import ApiServer
from sqlalchemy import select
from ..db.models import Metrica, VeiculoPendente, VeiculoDescargaC3, VeiculoAntecipado



class MetricaTableModel(QtCore.QAbstractTableModel):
    HEADERS = [
        "ID",
        "Paletes Agendados",
        "Paletes Produzidos",
        "Total de fichas",
        "Fichas finalizadas",
        "Descargas (C3)",
        "Carregamentos (C3)",
        "Veículos Pendentes",
        "Paletes Pendentes",
    "Fichas antecipadas",
        "Criado em",
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
        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):  # type: ignore[override]
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_rows(self, rows: list[tuple]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ExpandingTextEdit(QtWidgets.QTextEdit):
    def __init__(self, *args, collapsed_height: int = 48, expanded_height: int = 120, **kwargs):
        super().__init__(*args, **kwargs)
        self._collapsed_h = collapsed_height
        self._expanded_h = expanded_height
        self.setFixedHeight(self._collapsed_h)
        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)

    def focusInEvent(self, e: QtGui.QFocusEvent) -> None:  # type: ignore[override]
        try:
            self.setFixedHeight(self._expanded_h)
        except Exception:
            pass
        super().focusInEvent(e)

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:  # type: ignore[override]
        super().focusOutEvent(e)
        try:
            self.setFixedHeight(self._collapsed_h)
        except Exception:
            pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Métricas de Operação")
        self.resize(1200, 720)
        self.setStyleSheet(DARK_QSS)

        # Campos de métricas
        self.paletes_agendados = QtWidgets.QSpinBox(); self.paletes_agendados.setRange(0, 10_000)
        self.paletes_produzidos = QtWidgets.QSpinBox(); self.paletes_produzidos.setRange(0, 10_000)
        self.total_veiculos = QtWidgets.QSpinBox(); self.total_veiculos.setRange(0, 10_000)
        self.veiculos_finalizados = QtWidgets.QSpinBox(); self.veiculos_finalizados.setRange(0, 10_000)
        self.descargas_c3 = QtWidgets.QSpinBox(); self.descargas_c3.setRange(0, 10_000)
        self.carregamentos_c3 = QtWidgets.QSpinBox(); self.carregamentos_c3.setRange(0, 10_000)
        self.veiculos_pendentes = QtWidgets.QSpinBox(); self.veiculos_pendentes.setRange(0, 10_000)
        self.fichas_antecipadas = QtWidgets.QSpinBox(); self.fichas_antecipadas.setRange(0, 10_000)
        self.btn_edit_veics = QtWidgets.QPushButton("Editar Veículos…")
        self.btn_edit_veics.clicked.connect(self.on_edit_veiculos)
        self.paletes_pendentes = QtWidgets.QSpinBox(); self.paletes_pendentes.setRange(0, 10_000)
        # Campo Observação (expansível ao foco)
        self.observacao = ExpandingTextEdit()
        self.observacao.setPlaceholderText("Observação (clique para expandir)")
        self.observacao.setToolTip("Campo livre para observações deste registro")

        self.btn_add = QtWidgets.QPushButton("Adicionar")
        self.btn_add.clicked.connect(self.on_add)
        self.btn_del = QtWidgets.QPushButton("Excluir Selecionado")
        self.btn_del.setObjectName("danger")
        self.btn_del.clicked.connect(self.on_delete)
        # Botão Exportar
        self.btn_export = QtWidgets.QPushButton("Exportar")
        self.btn_export.clicked.connect(self.on_export)

        # Alturas mínimas para controles
        for w in (
            self.paletes_agendados,
            self.paletes_produzidos,
            self.total_veiculos,
            self.veiculos_finalizados,
            self.descargas_c3,
            self.carregamentos_c3,
            self.veiculos_pendentes,
            self.fichas_antecipadas,
            self.paletes_pendentes,
            self.btn_edit_veics,
            self.btn_add,
            self.btn_del,
            self.btn_export,
        ):
            w.setMinimumHeight(34)
        # Altura mínima para o campo de observação já é controlada pela classe

        form = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(form)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        grid.setContentsMargins(16, 16, 16, 16)
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
        grid.addWidget(self.carregamentos_c3, 2, 3)
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

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(16)
        top.addWidget(form, 1)
        buttons = QtWidgets.QVBoxLayout()
        buttons.setSpacing(10)
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_del)
        buttons.addWidget(self.btn_export)
        buttons.addStretch(1)
        bwrap = QtWidgets.QWidget(); bwrap.setLayout(buttons)
        top.addWidget(bwrap)

        top_w = QtWidgets.QWidget()
        top_w.setLayout(top)

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
        pager.addWidget(self.btn_prev)
        pager.addWidget(self.lbl_page)
        pager.addWidget(self.btn_next)
        pager_w = QtWidgets.QWidget(); pager_w.setLayout(pager)

        # Layout
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
        header = QtWidgets.QLabel("Controle de registro Recebimento [ Banco de dados ]")
        header.setObjectName("appTitle")
        header.setAlignment(QtCore.Qt.AlignCenter)
        # Botão de gráfico (à direita)
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
        # Layout: stretch | título | stretch | botão
        header_layout.addStretch(1)
        header_layout.addWidget(header, 0, QtCore.Qt.AlignCenter)
        header_layout.addStretch(1)
        header_layout.addWidget(btn_grafico, 0, QtCore.Qt.AlignRight)
        # Adiciona centralizado; a largura será ajustada para ~95% no resizeEvent
        lay.addWidget(header_container, alignment=QtCore.Qt.AlignHCenter)
        self._header_container = header_container
        lay.addWidget(top_w)
        lay.addWidget(self.table, 1)
        lay.addWidget(pager_w)
        self.setCentralWidget(central)

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

        # buffers temporários antes de salvar
        self._buffer_veiculos = []  # type: list[tuple[str, int]]
        self._buffer_descargas = []  # type: list[tuple[str, int]]
        self._buffer_antecipados = []  # type: list[tuple[str, int]]

        # Estado de paginação
        self._page_size_val = int(self.page_size.currentText())
        self._current_page = 1

        self.model = MetricaTableModel([])
        self.table.setModel(self.model)
        self._columns_sized = False
        self._apply_fast_column_layout()
        self.refresh()

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
            # Converte criado_em (UTC) para America/Sao_Paulo
            try:
                from zoneinfo import ZoneInfo  # Python 3.9+
                dt = m.criado_em
                if getattr(dt, "tzinfo", None) is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_sp = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
                criado_fmt = dt_sp.strftime("%d/%m/%Y %H:%M")
            except Exception:
                try:
                    criado_fmt = (m.criado_em - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")
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
                    m.veiculos_pendentes,
                    m.paletes_pendentes,
                    getattr(m, "fichas_antecipadas", 0),
                    criado_fmt,
                )
            )
        self.model.set_rows(rows)
        # Atualiza barra de paginação
        self.lbl_page.setText(f"Página {self._current_page} de {total_pages}")
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(self._current_page < total_pages)

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
            veiculos_pendentes: int
            paletes_pendentes: int

            @field_validator(
                "paletes_agendados",
                "paletes_produzidos",
                "total_veiculos",
                "veiculos_finalizados",
                "fichas_antecipadas",
                "descargas_c3",
                "carregamentos_c3",
                "veiculos_pendentes",
                "paletes_pendentes",
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
            "veiculos_pendentes": int(self.veiculos_pendentes.value()),
            "paletes_pendentes": int(self.paletes_pendentes.value()),
        }

        try:
            payload = Payload(**data)
        except ValidationError as ve:
            QtWidgets.QMessageBox.warning(self, "Dados inválidos", "\n".join([e['msg'] for e in ve.errors()]))
            return

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
                veiculos_pendentes=payload.veiculos_pendentes,
                paletes_pendentes=payload.paletes_pendentes,
            )
            # Salva veículos pendentes vinculados à métrica criada
            for veiculo, pct in self._buffer_veiculos:
                try:
                    self.veic_repo.add(created.id, veiculo, int(pct))
                except Exception:
                    # continua, mas informa depois
                    pass
            # Salva veículos de Descarga C3 vinculados
            for veiculo, pct in self._buffer_descargas:
                try:
                    self.desc_repo.add(created.id, veiculo, int(pct))
                except Exception:
                    pass
            # Salva veículos antecipados vinculados
            for veiculo, pct in self._buffer_antecipados:
                try:
                    self.antec_repo.add(created.id, veiculo, int(pct))
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
            self.veiculos_pendentes,
            self.fichas_antecipadas,
            self.paletes_pendentes,
        ):
            w.setValue(0)
        self.observacao.setPlainText("")
        self._buffer_veiculos = []
        self._buffer_descargas = []
        self._buffer_antecipados = []
        # Após inserir, volta para a primeira página (mais recentes)
        self._current_page = 1
        self.refresh()

    def on_edit_veiculos(self) -> None:
        # Abre o diálogo de edição para preencher veículos pendentes no buffer
        dlg = VeiculosDialog(self, initial=self._buffer_veiculos, read_only=False, title="Editar Veículos Pendentes")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self._buffer_veiculos = dlg.get_rows()
            self.veiculos_pendentes.setValue(len(self._buffer_veiculos))

    def on_edit_descargas(self) -> None:
        # Abre diálogo para editar veículos de Descarga C3 no buffer
        dlg = VeiculosDialog(self, initial=self._buffer_descargas, read_only=False, title="Veículos Descarga C3")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self._buffer_descargas = dlg.get_rows()

    def on_edit_antecipados(self) -> None:
        # Abre diálogo para editar veículos antecipados no buffer
        dlg = VeiculosDialog(self, initial=self._buffer_antecipados, read_only=False, title="Veículos Antecipados")
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self._buffer_antecipados = dlg.get_rows()

    def on_table_double_click(self, index: QtCore.QModelIndex) -> None:
        if not index.isValid():
            return
        col = index.column()
        row = index.row()
        metrica_id = int(self.model._rows[row][0])
        # Descargas (C3) coluna 5 abre veículos de descarga C3
        if col == 5:
            items = self.desc_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Descargas C3 (Métrica {metrica_id})")
            dlg.exec()
            return
        # Veículos Pendentes coluna 7 (0-based)
        if col == 7:
            items = self.veic_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Veículos Pendentes (Métrica {metrica_id})")
            dlg.exec()
            return
        # Fichas antecipadas coluna 9 (0-based)
        if col == 9:
            items = self.antec_repo.list_by_metrica(metrica_id)
            initial = [(it.veiculo, int(it.porcentagem)) for it in items]
            dlg = VeiculosDialog(self, initial=initial, read_only=True, title=f"Veículos Antecipados (Métrica {metrica_id})")
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
                ["id", "metrica_id", "veiculo", "porcentagem", "criado_em"],
                [
                    [
                        v.id,
                        v.metrica_id,
                        v.veiculo,
                        int(v.porcentagem),
                        (v.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(v, "criado_em") and v.criado_em else ""),
                    ]
                    for v in pendentes
                ],
            )

            # Sheet Descargas C3
            add_sheet(
                "DescargasC3",
                ["id", "metrica_id", "veiculo", "porcentagem", "criado_em"],
                [
                    [
                        d.id,
                        d.metrica_id,
                        d.veiculo,
                        int(d.porcentagem),
                        (d.criado_em.strftime("%d/%m/%Y %H:%M") if hasattr(d, "criado_em") and d.criado_em else ""),
                    ]
                    for d in descargas
                ],
            )

            # Sheet Antecipados
            add_sheet(
                "Antecipados",
                ["id", "metrica_id", "veiculo", "porcentagem", "criado_em"],
                [
                    [
                        a.id,
                        a.metrica_id,
                        a.veiculo,
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
