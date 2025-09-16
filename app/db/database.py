from __future__ import annotations
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .models import Base



DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

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
