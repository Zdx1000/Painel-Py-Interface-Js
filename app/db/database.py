from __future__ import annotations
from pathlib import Path
import os
import shutil
import sys
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .models import Base



def _get_executable_dir() -> Path:
    """Retorna o diretório do executável (EXE ou script principal)."""
    if getattr(sys, 'frozen', False):
        # PyInstaller/auto-py-to-exe
        return Path(sys.executable).parent
    else:
        # Script Python normal
        return Path(__file__).resolve().parent.parent.parent

EXE_DIR = _get_executable_dir()
DB_PATH = EXE_DIR / "app.db"

# Migração: se existir banco antigo em app/data/app.db e não existir no novo local, mover
try:
    old_path = Path(__file__).resolve().parent.parent / "data" / "app.db"
    if old_path.exists() and not DB_PATH.exists():
        shutil.copy2(old_path, DB_PATH)
except Exception:
    pass

DATABASE_URL = f"sqlite:///{DB_PATH}"  # usa banco no diretório do executável

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def init_db() -> None:
    from .models import Base  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Migração leve: garante colunas novas na tabela metricas
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(metricas)")).fetchall()
            cols = {r[1] for r in rows}
            if "fichas_antecipadas" not in cols:
                conn.execute(text("ALTER TABLE metricas ADD COLUMN fichas_antecipadas INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            if "observacao" not in cols:
                conn.execute(text("ALTER TABLE metricas ADD COLUMN observacao TEXT NULL"))
                try:
                    conn.commit()
                except Exception:
                    pass
            if "chamado_granel" not in cols:
                conn.execute(text("ALTER TABLE metricas ADD COLUMN chamado_granel INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            if "paletizada" not in cols:
                conn.execute(text("ALTER TABLE metricas ADD COLUMN paletizada INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            # Migração leve para veiculos_descarga_c3.quantidade
            rows_vd = conn.execute(text("PRAGMA table_info(veiculos_descarga_c3)")).fetchall()
            cols_vd = {r[1] for r in rows_vd}
            if "quantidade" not in cols_vd:
                conn.execute(text("ALTER TABLE veiculos_descarga_c3 ADD COLUMN quantidade INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            # Migração leve para veiculos_carregamento_c3.quantidade
            rows_vc = conn.execute(text("PRAGMA table_info(veiculos_carregamento_c3)")).fetchall()
            cols_vc = {r[1] for r in rows_vc}
            if "quantidade" not in cols_vc:
                conn.execute(text("ALTER TABLE veiculos_carregamento_c3 ADD COLUMN quantidade INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            # Migração leve para veiculos_pendentes.quantidade
            rows_vp = conn.execute(text("PRAGMA table_info(veiculos_pendentes)")).fetchall()
            cols_vp = {r[1] for r in rows_vp}
            if "quantidade" not in cols_vp:
                conn.execute(text("ALTER TABLE veiculos_pendentes ADD COLUMN quantidade INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
            # Migração leve para veiculos_antecipados.quantidade
            rows_va = conn.execute(text("PRAGMA table_info(veiculos_antecipados)")).fetchall()
            cols_va = {r[1] for r in rows_va}
            if "quantidade" not in cols_va:
                conn.execute(text("ALTER TABLE veiculos_antecipados ADD COLUMN quantidade INTEGER NOT NULL DEFAULT 0"))
                try:
                    conn.commit()
                except Exception:
                    pass
    except Exception:
        # Silencioso: se falhar, assume base nova
        pass


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
