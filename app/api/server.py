from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from ..db.database import get_session
from ..db.repository import MetricaRepository, VeiculoPendenteRepository


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
                    items.append({
                        "id": m.id,
                        "paletes_agendados": m.paletes_agendados,
                        "paletes_produzidos": m.paletes_produzidos,
                        "total_veiculos": m.total_veiculos,
                        "veiculos_finalizados": m.veiculos_finalizados,
                        "descargas_c3": m.descargas_c3,
                        "carregamentos_c3": m.carregamentos_c3,
                        "veiculos_pendentes": m.veiculos_pendentes,
                        "paletes_pendentes": m.paletes_pendentes,
                        "criado_em": (m.criado_em if isinstance(m.criado_em, str) else m.criado_em.isoformat(timespec="minutes")),
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
                items = [{"veiculo": r.veiculo, "porcentagem": int(r.porcentagem)} for r in rows]
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
