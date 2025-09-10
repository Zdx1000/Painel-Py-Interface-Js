const API_BASE = "http://127.0.0.1:8765"; // iniciado pelo app desktop

const state = {
	page: 1,
	pageSize: 20,
	totalPages: 1,
};

async function fetchMetricas() {
	const url = `${API_BASE}/api/metricas?page=${state.page}&page_size=${state.pageSize}`;
	const res = await fetch(url);
	if (!res.ok) throw new Error("Erro ao buscar dados");
	return res.json();
}


function renderTable(items) {
	const tbody = document.querySelector("#tbl tbody");
	tbody.innerHTML = "";
	const frag = document.createDocumentFragment();
	for (const m of items) {
		const tr = document.createElement("tr");
		const cols = [
			m.id,
			m.paletes_agendados,
			m.paletes_produzidos,
			m.total_veiculos,
			m.veiculos_finalizados,
			m.descargas_c3,
			m.carregamentos_c3,
			m.veiculos_pendentes,
			m.paletes_pendentes,
			(m.fichas_antecipadas ?? 0),
			formatDate(m.criado_em),
		];
		for (const c of cols) {
			const td = document.createElement("td");
			td.textContent = c;
			tr.appendChild(td);
		}
		frag.appendChild(tr);
	}
	tbody.appendChild(frag);
}

function formatDate(iso) {
	try {
		const d = new Date(iso);
		const dd = String(d.getDate()).padStart(2, "0");
		const mm = String(d.getMonth()+1).padStart(2, "0");
		const yy = d.getFullYear();
		const hh = String(d.getHours()).padStart(2, "0");
		const mi = String(d.getMinutes()).padStart(2, "0");
		return `${dd}/${mm}/${yy} ${hh}:${mi}`;
	} catch { return iso; }
}

async function refresh() {
	try {
		const data = await fetchMetricas();
		state.totalPages = data.total_pages;
		state.page = data.page; // pode ajustar se pediu além do limite
		renderTable(data.items);
		document.getElementById("pageInfo").textContent = `Página ${state.page} de ${state.totalPages}`;
		document.getElementById("prevBtn").disabled = state.page <= 1;
		document.getElementById("nextBtn").disabled = state.page >= state.totalPages;
	} catch (e) {
		console.error(e);
		document.querySelector("#tbl tbody").innerHTML = `<tr><td colspan="10">Erro ao carregar. Abra a aplicação desktop para iniciar a API local.</td></tr>`;
	}
}

document.addEventListener("DOMContentLoaded", () => {
	const pageSizeSel = document.getElementById("pageSize");
	pageSizeSel.addEventListener("change", () => {
		state.pageSize = parseInt(pageSizeSel.value, 10) || 20;
		state.page = 1;
		refresh();
	});
	document.getElementById("prevBtn").addEventListener("click", () => {
		if (state.page > 1) { state.page--; refresh(); }
	});
	document.getElementById("nextBtn").addEventListener("click", () => {
		if (state.page < state.totalPages) { state.page++; refresh(); }
	});
	// inicial
	refresh();
});

