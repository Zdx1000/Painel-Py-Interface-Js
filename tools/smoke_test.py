import sys
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import init_db, get_session
from app.db.repository import MetricaRepository

if __name__ == "__main__":
    init_db()
    s = next(get_session())
    repo = MetricaRepository(s)
    r = repo.add(
        paletes_agendados=1,
        paletes_produzidos=2,
        total_veiculos=3,
        veiculos_finalizados=1,
        fichas_antecipadas=0,
        observacao=None,
        descargas_c3=1,
        carregamentos_c3=1,
        veiculos_pendentes=2,
        paletes_pendentes=5,
    )
    print("INSERTED", r.id)
    print("COUNT", len(repo.list()))

