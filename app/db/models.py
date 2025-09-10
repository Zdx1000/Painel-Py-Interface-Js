from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass




class Metrica(Base):
    __tablename__ = "metricas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paletes_agendados: Mapped[int] = mapped_column(Integer, nullable=False)
    paletes_produzidos: Mapped[int] = mapped_column(Integer, nullable=False)
    total_veiculos: Mapped[int] = mapped_column(Integer, nullable=False)
    veiculos_finalizados: Mapped[int] = mapped_column(Integer, nullable=False)
    descargas_c3: Mapped[int] = mapped_column(Integer, nullable=False)
    carregamentos_c3: Mapped[int] = mapped_column(Integer, nullable=False)
    veiculos_pendentes: Mapped[int] = mapped_column(Integer, nullable=False)
    paletes_pendentes: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Metrica id={self.id} paletes_agendados={self.paletes_agendados} paletes_produzidos={self.paletes_produzidos} "
            f"total_veiculos={self.total_veiculos} veiculos_finalizados={self.veiculos_finalizados} descargas_c3={self.descargas_c3} "
            f"carregamentos_c3={self.carregamentos_c3} veiculos_pendentes={self.veiculos_pendentes} paletes_pendentes={self.paletes_pendentes}>"
        )



class VeiculoPendente(Base):
    __tablename__ = "veiculos_pendentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metrica_id: Mapped[int] = mapped_column(Integer, ForeignKey("metricas.id", ondelete="CASCADE"), index=True, nullable=False)
    veiculo: Mapped[str] = mapped_column(String(200), nullable=False)
    porcentagem: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VeiculoPendente id={self.id} metrica_id={self.metrica_id} veiculo={self.veiculo!r} porcentagem={self.porcentagem}>"


class VeiculoDescargaC3(Base):
    __tablename__ = "veiculos_descarga_c3"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metrica_id: Mapped[int] = mapped_column(Integer, ForeignKey("metricas.id", ondelete="CASCADE"), index=True, nullable=False)
    veiculo: Mapped[str] = mapped_column(String(200), nullable=False)
    porcentagem: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VeiculoDescargaC3 id={self.id} metrica_id={self.metrica_id} veiculo={self.veiculo!r} porcentagem={self.porcentagem}>"
