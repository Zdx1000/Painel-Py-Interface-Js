import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import init_db, get_session
from app.db.repository import MetricaRepository, VeiculoPendenteRepository

init_db()
session = next(get_session())
met_repo = MetricaRepository(session)
veh_repo = VeiculoPendenteRepository(session)

m = met_repo.add(
    paletes_agendados=10,
    paletes_produzidos=8,
    total_veiculos=5,
    veiculos_finalizados=2,
    descargas_c3=1,
    carregamentos_c3=2,
    veiculos_pendentes=0,
    paletes_pendentes=3,
)

veh_repo.add(m.id, "Caminhão ABC-1234", 60)
veh_repo.add(m.id, "VUC XYZ-9999", 40)

items = veh_repo.list_by_metrica(m.id)
print("METRICA_ID", m.id)
print("VEICULOS", [(i.veiculo, i.porcentagem) for i in items])

ok = met_repo.delete(m.id)
print("DELETED", ok)
items_after = veh_repo.list_by_metrica(m.id)
print("REMAIN", len(items_after))

