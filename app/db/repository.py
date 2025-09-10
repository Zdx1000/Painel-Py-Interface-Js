from __future__ import annotations
from typing import Sequence

from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from .models import Metrica, VeiculoPendente



class MetricaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self,
        paletes_agendados: int,
        paletes_produzidos: int,
        total_veiculos: int,
        veiculos_finalizados: int,
        descargas_c3: int,
        carregamentos_c3: int,
        veiculos_pendentes: int,
        paletes_pendentes: int,
    ) -> Metrica:
        novo = Metrica(
            paletes_agendados=paletes_agendados,
            paletes_produzidos=paletes_produzidos,
            total_veiculos=total_veiculos,
            veiculos_finalizados=veiculos_finalizados,
            descargas_c3=descargas_c3,
            carregamentos_c3=carregamentos_c3,
            veiculos_pendentes=veiculos_pendentes,
            paletes_pendentes=paletes_pendentes,
        )
        self.session.add(novo)
        self.session.commit()
        self.session.refresh(novo)
        return novo

    def list(self, limit: int = 100):
        stmt = select(Metrica).order_by(Metrica.criado_em.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def list_page(self, limit: int, offset: int):
        stmt = (
            select(Metrica)
            .order_by(Metrica.criado_em.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        stmt = select(func.count()).select_from(Metrica)
        return int(self.session.execute(stmt).scalar_one())

    def delete(self, metrica_id: int) -> bool:
        m = self.session.get(Metrica, metrica_id)
        if not m:
            return False
        # Remove veículos vinculados primeiro (garante integridade no SQLite)
        self.session.execute(delete(VeiculoPendente).where(VeiculoPendente.metrica_id == metrica_id))
        self.session.delete(m)
        self.session.commit()
        return True


class VeiculoPendenteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, metrica_id: int, veiculo: str, porcentagem: int) -> VeiculoPendente:
        v = VeiculoPendente(metrica_id=metrica_id, veiculo=veiculo, porcentagem=porcentagem)
        self.session.add(v)
        self.session.commit()
        self.session.refresh(v)
        return v

    def list_by_metrica(self, metrica_id: int):
        stmt = select(VeiculoPendente).where(VeiculoPendente.metrica_id == metrica_id).order_by(VeiculoPendente.criado_em.desc())
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, veiculo_id: int) -> bool:
        v = self.session.get(VeiculoPendente, veiculo_id)
        if not v:
            return False
        self.session.delete(v)
        self.session.commit()
        return True
