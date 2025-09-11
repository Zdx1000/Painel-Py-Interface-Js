const API_BASE = "http://127.0.0.1:8765"; // iniciado pelo app desktop

async function fetchDia(dateStr){
	const url = `${API_BASE}/api/dia?date=${encodeURIComponent(dateStr)}`;
	const res = await fetch(url);
	if(!res.ok) throw new Error("Erro ao buscar dia");
	return res.json();
}

function setText(id, val){
	const el = document.getElementById(id);
	if(el) el.textContent = String(val);
}

function renderList(listId, items){
	const ul = document.getElementById(listId);
	if(!ul) return;
	ul.innerHTML = "";
	const frag = document.createDocumentFragment();
	for(const it of items){
		const li = document.createElement("li");
		li.className = "li-veh";
		const label = document.createElement("span");
		label.className = "label";
		label.textContent = it.veiculo || "—";

		const wrap = document.createElement("span");
		wrap.className = "barWrap";
		const fill = document.createElement("span");
		fill.className = "fill";
		let pct = 0;
		try{ pct = Math.max(0, Math.min(100, parseInt(it.porcentagem,10) || 0)); }catch{}
		fill.style.width = pct + "%";
		wrap.appendChild(fill);

		const pctEl = document.createElement("span");
		pctEl.className = "pct";
		pctEl.textContent = pct + "%";

		li.appendChild(label);
		li.appendChild(wrap);
		li.appendChild(pctEl);
		frag.appendChild(li);
	}
	ul.appendChild(frag);
}

function renderObs(objs){
	const wrap = document.getElementById("obs_list");
	if(!wrap) return;
	wrap.innerHTML = "";
	if(!objs || objs.length === 0){
		wrap.innerHTML = '<div class="muted">Sem observações do dia.</div>';
		return;
	}
	for(const o of objs){
		const p = document.createElement("div");
		p.className = "obsItem";
		p.textContent = o;
		wrap.appendChild(p);
	}
}

async function carregarDia(){
	const input = document.getElementById("datePick");
	const val = input.value;
	if(!val){
		alert("Selecione uma data.");
		return;
	}
	try{
		const data = await fetchDia(val);
		const t = data.totals || {};
		setText("v_agendados", t.paletes_agendados ?? 0);
		setText("v_produzidos", t.paletes_produzidos ?? 0);
		setText("v_total_fichas", t.total_fichas ?? 0);
		setText("v_finalizadas", t.fichas_finalizadas ?? 0);
		setText("v_paletes_pend", t.paletes_pendentes ?? 0);

		setText("v_desc_qtd", (data.descargas_c3 && data.descargas_c3.qtd) ?? 0);
		renderList("list_descargas", (data.descargas_c3 && data.descargas_c3.itens) || []);

		setText("v_carr_qtd", (data.carregamentos_c3 && data.carregamentos_c3.qtd) ?? 0);
		renderList("list_carreg", (data.carregamentos_c3 && data.carregamentos_c3.itens) || []);

		setText("v_pend_qtd", (data.veiculos_pendentes && data.veiculos_pendentes.qtd) ?? 0);
		renderList("list_pend", (data.veiculos_pendentes && data.veiculos_pendentes.itens) || []);

	// Fichas antecipadas (itens são veículos antecipados)
	setText("v_antec_qtd", (data.antecipados && data.antecipados.qtd) ?? 0);
	renderList("list_antec", (data.antecipados && data.antecipados.itens) || []);

		renderObs(data.observacoes || []);

	// Progresso do dia (Paletes Produzidos / Agendados)
		const total = Math.max(0, parseInt(t.paletes_agendados||0,10));
		const feitoRaw = Math.max(0, parseInt(t.paletes_produzidos||0,10));
		const feito = Math.min(total || 0, feitoRaw);
		const pct = total > 0 ? Math.round((feito/total)*100) : 0;
	setText("prog_total", total);
		setText("prog_done", feitoRaw);
	setText("prog_pct", pct);
	const bar = document.getElementById("prog_fill");
	if(bar) bar.style.width = pct + "%";

		// Extra quando produziu acima do agendado
		const extraBlock = document.getElementById("extra_block");
		const extra = feitoRaw - total;
		if(extraBlock){
			if(extra > 0 && total > 0){
				const extraPct = Math.round((extra/total)*100);
				setText("prog_extra_pct", extraPct);
				setText("prog_extra_pct2", extraPct);
				const extraFill = document.getElementById("prog_extra_fill");
				if(extraFill){
					// limite visual de 100% para a barra extra
					const width = Math.max(5, Math.min(100, extraPct));
					extraFill.style.width = width + "%";
				}
				extraBlock.style.display = "block";
			}else{
				extraBlock.style.display = "none";
			}
		}
	}catch(e){
		console.error(e);
		alert("Erro ao carregar dados do dia. Certifique-se de que a aplicação desktop está aberta.");
	}
}

document.addEventListener("DOMContentLoaded", () => {
	// Default: hoje no formato YYYY-MM-DD (São Paulo)
	const d = new Date();
	const yyyy = d.getFullYear();
	const mm = String(d.getMonth()+1).padStart(2, "0");
	const dd = String(d.getDate()).padStart(2, "0");
	const today = `${yyyy}-${mm}-${dd}`;
	const input = document.getElementById("datePick");
	input.value = today;
	document.getElementById("loadDay").addEventListener("click", carregarDia);
	carregarDia();
});

