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
    # Migração leve: garante coluna fichas_antecipadas na tabela metricas
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
    except Exception:
        # Silencioso: se falhar, assume base nova
        pass


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
