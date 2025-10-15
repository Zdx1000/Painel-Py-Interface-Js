from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from ..db.database import get_session
from datetime import timezone, timedelta
from ..db.repository import (
    MetricaRepository,
    VeiculoPendenteRepository,
    VeiculoDescargaC3Repository,
    VeiculoCarregamentoC3Repository,
)
from sqlalchemy import select
from ..db.models import (
    Metrica,
    VeiculoPendente,
    VeiculoDescargaC3,
    VeiculoAntecipado,
    VeiculoCarregamentoC3,
)


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict | list) -> None:
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    # CORS básico para permitir acesso a partir de file:// e http://localhost
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class ApiHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # pragma: no cover - silencia logs no console
        return

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == "/api/health":
            return _json_response(self, 200, {"status": "ok"})

        if path == "/api/metricas":
            qs = parse_qs(parsed.query or "")
            try:
                page = int(qs.get("page", ["1"])[0])
            except ValueError:
                page = 1
            try:
                page_size = int(qs.get("page_size", ["20"])[0])
            except ValueError:
                page_size = 20
            page = max(1, page)
            page_size = max(1, min(200, page_size))

            # Carrega do banco
            cm = get_session()
            session = next(cm)
            try:
                repo = MetricaRepository(session)
                total = repo.count()
                total_pages = max(1, (total + page_size - 1) // page_size)
                if page > total_pages:
                    page = total_pages
                offset = (page - 1) * page_size
                items = []
                for m in repo.list_page(limit=page_size, offset=offset):
                    # criado_em em America/Sao_Paulo
                    try:
                        from zoneinfo import ZoneInfo
                        dt = m.criado_em
                        if getattr(dt, "tzinfo", None) is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        criado_sp = dt.astimezone(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="minutes")
                    except Exception:
                        criado_sp = (m.criado_em).isoformat(timespec="minutes")
                    items.append({
                        "id": m.id,
                        "paletes_agendados": m.paletes_agendados,
                        "paletes_produzidos": m.paletes_produzidos,
                        "total_veiculos": m.total_veiculos,
                        "veiculos_finalizados": m.veiculos_finalizados,
                        "fichas_antecipadas": getattr(m, "fichas_antecipadas", 0),
                        "observacao": getattr(m, "observacao", None),
                        "descargas_c3": m.descargas_c3,
                        "carregamentos_c3": m.carregamentos_c3,
                        "chamado_granel": m.chamado_granel,
                        "paletizada": m.paletizada,
                        "veiculos_pendentes": m.veiculos_pendentes,
                        "paletes_pendentes": m.paletes_pendentes,
                        "criado_em": criado_sp,
                    })
                return _json_response(self, 200, {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "items": items,
                })
            finally:
                session.close()

        if path == "/api/dia":
            qs = parse_qs(parsed.query or "")
            date_str = (qs.get("date", [""])[0] or "").strip()
            if not date_str:
                return _json_response(self, 400, {"error": "parâmetro 'date' obrigatório (YYYY-MM-DD)"})
            # Interpreta a data como foi salva (naive) sem conversão de fuso
            try:
                y, m, d = [int(x) for x in date_str.split("-")]
                start_utc = datetime(y, m, d, 0, 0, 0)
                end_utc = datetime(y, m, d, 23, 59, 59, 999000)
            except Exception:
                return _json_response(self, 400, {"error": "data inválida, use YYYY-MM-DD"})

            cm = get_session()
            session = next(cm)
            try:
                # Buscar metricas no intervalo
                rows = session.execute(
                    select(Metrica).where(Metrica.criado_em >= start_utc, Metrica.criado_em <= end_utc)
                ).scalars().all()
                if not rows:
                    return _json_response(self, 200, {
                        "date": date_str,
                        "totals": {
                            "paletes_agendados": 0,
                            "paletes_produzidos": 0,
                            "total_fichas": 0,
                            "fichas_finalizadas": 0,
                            "descargas_c3": 0,
                            "carregamentos_c3": 0,
                            "chamado_granel": 0,
                            "paletizada": 0,
                            "paletes_pendentes": 0,
                            "veiculos_pendentes": 0,
                            "fichas_antecipadas": 0,
                        },
                        "observacoes": [],
                        "descargas_c3": {"qtd": 0, "itens": []},
                        "carregamentos_c3": {"qtd": 0, "itens": []},
                        "veiculos_pendentes": {"qtd": 0, "itens": []},
                        "antecipados": {"qtd": 0, "itens": []},
                    })

                ids = [m.id for m in rows]
                totals = {
                    "paletes_agendados": sum(m.paletes_agendados for m in rows),
                    "paletes_produzidos": sum(m.paletes_produzidos for m in rows),
                    "total_fichas": sum(m.total_veiculos for m in rows),
                    "fichas_finalizadas": sum(m.veiculos_finalizados for m in rows),
                    "descargas_c3": sum(m.descargas_c3 for m in rows),
                    "carregamentos_c3": sum(m.carregamentos_c3 for m in rows),
                    "chamado_granel": sum(m.chamado_granel for m in rows),
                    "paletizada": sum(m.paletizada for m in rows),
                    "paletes_pendentes": sum(m.paletes_pendentes for m in rows),
                    "veiculos_pendentes": sum(m.veiculos_pendentes for m in rows),
                    "fichas_antecipadas": sum(getattr(m, "fichas_antecipadas", 0) for m in rows),
                }
                observacoes = [m.observacao for m in rows if getattr(m, "observacao", None)]

                # Carregar listas relacionadas do dia (com base nos ids)
                vp = session.execute(
                    select(VeiculoPendente).where(VeiculoPendente.metrica_id.in_(ids))
                ).scalars().all()
                vd = session.execute(
                    select(VeiculoDescargaC3).where(VeiculoDescargaC3.metrica_id.in_(ids))
                ).scalars().all()
                va = session.execute(
                    select(VeiculoAntecipado).where(VeiculoAntecipado.metrica_id.in_(ids))
                ).scalars().all()
                vc = session.execute(
                    select(VeiculoCarregamentoC3).where(VeiculoCarregamentoC3.metrica_id.in_(ids))
                ).scalars().all()

                payload = {
                    "date": date_str,
                    "totals": totals,
                    "observacoes": observacoes,
                    "descargas_c3": {
                        "qtd": totals["descargas_c3"],
                        "itens": [{"metrica_id": x.metrica_id, "veiculo": x.veiculo, "porcentagem": int(x.porcentagem), "quantidade": int(getattr(x, 'quantidade', 0))} for x in vd],
                    },
                    "carregamentos_c3": {
                        "qtd": totals["carregamentos_c3"],
                        "itens": [{"metrica_id": x.metrica_id, "veiculo": x.veiculo, "porcentagem": int(x.porcentagem), "quantidade": int(getattr(x, 'quantidade', 0))} for x in vc],
                    },
                    "veiculos_pendentes": {
                        "qtd": totals["veiculos_pendentes"],
                        "itens": [{"metrica_id": x.metrica_id, "veiculo": x.veiculo, "porcentagem": int(x.porcentagem), "quantidade": int(getattr(x, 'quantidade', 0))} for x in vp],
                    },
                    "antecipados": {
                        "qtd": totals["fichas_antecipadas"],
                        "itens": [{"metrica_id": x.metrica_id, "veiculo": x.veiculo, "porcentagem": int(x.porcentagem), "quantidade": int(getattr(x, 'quantidade', 0))} for x in va],
                    },
                }
                return _json_response(self, 200, payload)
            finally:
                session.close()

        if path == "/api/periodo":
            qs = parse_qs(parsed.query or "")
            start_str = (qs.get("start", [""])[0] or "").strip()
            end_str = (qs.get("end", [""])[0] or "").strip()
            if not start_str or not end_str:
                return _json_response(self, 400, {"error": "parâmetros 'start' e 'end' são obrigatórios (YYYY-MM-DD)"})
            try:
                sy, sm, sd = [int(x) for x in start_str.split("-")]
                ey, em, ed = [int(x) for x in end_str.split("-")]
                start_utc = datetime(sy, sm, sd, 0, 0, 0)
                end_utc = datetime(ey, em, ed, 23, 59, 59, 999000)
            except Exception:
                return _json_response(self, 400, {"error": "datas inválidas, use YYYY-MM-DD"})
            if start_utc > end_utc:
                return _json_response(self, 400, {"error": "'start' deve ser menor ou igual a 'end'"})

            cm = get_session()
            session = next(cm)
            try:
                rows = session.execute(
                    select(Metrica).where(Metrica.criado_em >= start_utc, Metrica.criado_em <= end_utc)
                ).scalars().all()
                if not rows:
                    return _json_response(self, 200, [])

                # Agrupa por dia (naive date de criado_em)
                agg: dict[str, dict[str, int]] = {}
                for m in rows:
                    d = m.criado_em.date().isoformat()
                    cur = agg.setdefault(d, {
                        "paletes_agendados": 0,
                        "paletes_produzidos": 0,
                        "descargas_c3": 0,
                        "carregamentos_c3": 0,
                    })
                    cur["paletes_agendados"] += int(m.paletes_agendados or 0)
                    cur["paletes_produzidos"] += int(m.paletes_produzidos or 0)
                    cur["descargas_c3"] += int(m.descargas_c3 or 0)
                    cur["carregamentos_c3"] += int(m.carregamentos_c3 or 0)

                out = [
                    {
                        "date": d,
                        "paletes_agendados": v["paletes_agendados"],
                        "paletes_produzidos": v["paletes_produzidos"],
                        "descargas_c3": v["descargas_c3"],
                        "carregamentos_c3": v["carregamentos_c3"],
                    }
                    for d, v in sorted(agg.items(), key=lambda kv: kv[0])
                ]
                return _json_response(self, 200, out)
            finally:
                session.close()

        if path.startswith("/api/metricas/") and path.endswith("/veiculos"):
            parts = path.split("/")
            try:
                metrica_id = int(parts[3])
            except Exception:
                return _json_response(self, 400, {"error": "id inválido"})
            cm = get_session()
            session = next(cm)
            try:
                vrepo = VeiculoPendenteRepository(session)
                rows = vrepo.list_by_metrica(metrica_id)
                items = [{"veiculo": r.veiculo, "porcentagem": int(r.porcentagem), "quantidade": int(getattr(r, 'quantidade', 0))} for r in rows]
                return _json_response(self, 200, {"items": items})
            finally:
                session.close()


        if path.startswith("/api/metricas/") and path.endswith("/descargas-c3"):
            parts = path.split("/")
            try:
                metrica_id = int(parts[3])
            except Exception:
                return _json_response(self, 400, {"error": "id inválido"})
            cm = get_session()
            session = next(cm)
            try:
                drepo = VeiculoDescargaC3Repository(session)
                rows = drepo.list_by_metrica(metrica_id)
                items = [{"veiculo": r.veiculo, "porcentagem": int(r.porcentagem), "quantidade": int(getattr(r, 'quantidade', 0))} for r in rows]
                return _json_response(self, 200, {"items": items})
            finally:
                session.close()

        if path.startswith("/api/metricas/") and path.endswith("/carregamentos-c3"):
            parts = path.split("/")
            try:
                metrica_id = int(parts[3])
            except Exception:
                return _json_response(self, 400, {"error": "id inválido"})
            cm = get_session()
            session = next(cm)
            try:
                crepo = VeiculoCarregamentoC3Repository(session)
                rows = crepo.list_by_metrica(metrica_id)
                items = [{"veiculo": r.veiculo, "porcentagem": int(r.porcentagem), "quantidade": int(getattr(r, 'quantidade', 0))} for r in rows]
                return _json_response(self, 200, {"items": items})
            finally:
                session.close()

        return _json_response(self, 404, {"error": "not found"})



class ApiServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self._server = ThreadingHTTPServer((host, port), ApiHandler)
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._server.serve_forever, name="ApiServer", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            self._server.shutdown()
        except Exception:
            pass


__all__ = ["ApiServer"]
