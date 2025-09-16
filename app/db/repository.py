from __future__ import annotations
from typing import Sequence

from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from .models import Metrica, VeiculoPendente, VeiculoDescargaC3, VeiculoAntecipado, VeiculoCarregamentoC3



class MetricaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self,
        paletes_agendados: int,
        paletes_produzidos: int,
        total_veiculos: int,
        veiculos_finalizados: int,
        fichas_antecipadas: int,
        observacao: str | None,
        descargas_c3: int,
        carregamentos_c3: int,
        veiculos_pendentes: int,
        paletes_pendentes: int,
        *,
        criado_em=None,
    ) -> Metrica:
        # Se criado_em for fornecido (datetime naive ou timezone aware), usar direto
        kwargs = dict(
            paletes_agendados=paletes_agendados,
            paletes_produzidos=paletes_produzidos,
            total_veiculos=total_veiculos,
            veiculos_finalizados=veiculos_finalizados,
            fichas_antecipadas=fichas_antecipadas,
            observacao=observacao,
            descargas_c3=descargas_c3,
            carregamentos_c3=carregamentos_c3,
            veiculos_pendentes=veiculos_pendentes,
            paletes_pendentes=paletes_pendentes,
        )
        if criado_em is not None:
            kwargs["criado_em"] = criado_em
        novo = Metrica(**kwargs)
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
        self.session.execute(delete(VeiculoDescargaC3).where(VeiculoDescargaC3.metrica_id == metrica_id))
        self.session.execute(delete(VeiculoAntecipado).where(VeiculoAntecipado.metrica_id == metrica_id))
        self.session.execute(delete(VeiculoCarregamentoC3).where(VeiculoCarregamentoC3.metrica_id == metrica_id))
        self.session.delete(m)
        self.session.commit()
        return True


class VeiculoPendenteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, metrica_id: int, veiculo: str, porcentagem: int, quantidade: int | None = None) -> VeiculoPendente:
        v = VeiculoPendente(
            metrica_id=metrica_id,
            veiculo=veiculo,
            porcentagem=porcentagem,
            quantidade=(quantidade if quantidade is not None else 0),
        )
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


class VeiculoDescargaC3Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, metrica_id: int, veiculo: str, porcentagem: int, quantidade: int | None = None) -> VeiculoDescargaC3:
        v = VeiculoDescargaC3(
            metrica_id=metrica_id,
            veiculo=veiculo,
            porcentagem=porcentagem,
            quantidade=(quantidade if quantidade is not None else 0),
        )
        self.session.add(v)
        self.session.commit()
        self.session.refresh(v)
        return v

    def list_by_metrica(self, metrica_id: int):
        stmt = (
            select(VeiculoDescargaC3)
            .where(VeiculoDescargaC3.metrica_id == metrica_id)
            .order_by(VeiculoDescargaC3.criado_em.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, item_id: int) -> bool:
        v = self.session.get(VeiculoDescargaC3, item_id)
        if not v:
            return False
        self.session.delete(v)
        self.session.commit()
        return True


class VeiculoAntecipadoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, metrica_id: int, veiculo: str, porcentagem: int, quantidade: int | None = None) -> VeiculoAntecipado:
        v = VeiculoAntecipado(
            metrica_id=metrica_id,
            veiculo=veiculo,
            porcentagem=porcentagem,
            quantidade=(quantidade if quantidade is not None else 0),
        )
        self.session.add(v)
        self.session.commit()
        self.session.refresh(v)
        return v

    def list_by_metrica(self, metrica_id: int):
        stmt = (
            select(VeiculoAntecipado)
            .where(VeiculoAntecipado.metrica_id == metrica_id)
            .order_by(VeiculoAntecipado.criado_em.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, item_id: int) -> bool:
        v = self.session.get(VeiculoAntecipado, item_id)
        if not v:
            return False
        self.session.delete(v)
        self.session.commit()
        return True


class VeiculoCarregamentoC3Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, metrica_id: int, veiculo: str, porcentagem: int, quantidade: int | None = None) -> VeiculoCarregamentoC3:
        v = VeiculoCarregamentoC3(
            metrica_id=metrica_id,
            veiculo=veiculo,
            porcentagem=porcentagem,
            quantidade=(quantidade if quantidade is not None else 0),
        )
        self.session.add(v)
        self.session.commit()
        self.session.refresh(v)
        return v

    def list_by_metrica(self, metrica_id: int):
        stmt = (
            select(VeiculoCarregamentoC3)
            .where(VeiculoCarregamentoC3.metrica_id == metrica_id)
            .order_by(VeiculoCarregamentoC3.criado_em.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, item_id: int) -> bool:
        v = self.session.get(VeiculoCarregamentoC3, item_id)
        if not v:
            return False
        self.session.delete(v)
        self.session.commit()
        return True
