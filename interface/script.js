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

// Estado de observações editadas somente no visual (por data ISO yyyy-mm-dd)
// Armazenaremos HTML (string) para preservar formatação rich-text
const OBS_VISUAL = new Map();

async function carregarDia(){
	const input = document.getElementById("datePick");
	const val = input.value;
	if(!val){
		alert("Selecione uma data.");
		return;
	}
	// Atualiza título com a data selecionada (DD/MM/AAAA)
	const [y,m,d] = val.split("-");
	const titleEl = document.getElementById("pageTitle");
	if(titleEl){
		titleEl.textContent = `Apresentação diária — Recebimento CAD UDI (${d}/${m}/${y})`;
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

		// Observações: prioriza edição visual se existir para a data
		const visual = OBS_VISUAL.get(val);
		if(typeof visual === "string"){ // render HTML salvo
			const wrap = document.getElementById("obs_list");
			if(wrap){
				wrap.innerHTML = visual;
			}
		}else{
			const obsToShow = data.observacoes || [];
			renderObs(obsToShow);
		}

	// Progresso do dia (Paletes Produzidos / Agendados)
		const total = Math.max(0, parseInt(t.paletes_agendados||0,10));
		const feitoRaw = Math.max(0, parseInt(t.paletes_produzidos||0,10));
		const feito = Math.min(total || 0, feitoRaw);
		const pct = total > 0 ? Math.round((feito/total)*100) : 0;
	setText("prog_total", total);
		setText("prog_done", feitoRaw);
	setText("prog_pct", pct);
	const bar = document.getElementById("prog_fill");
	if(bar) {
		bar.style.width = pct + "%";
		bar.classList.remove("bar-red", "bar-yellow", "bar-green");
		if(pct <= 70){
			bar.classList.add("bar-red");
		}else if(pct <= 90){
			bar.classList.add("bar-yellow");
		}else{
			bar.classList.add("bar-green");
		}
	}

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

		// Comparativo Descargas x Carregamentos (valores absolutos)
		const dcA = Math.max(0, parseInt(t.descargas_c3||0,10));
		const dcB = Math.max(0, parseInt(t.carregamentos_c3||0,10));
		const dcMax = Math.max(1, dcA, dcB);
		setText("dual_dc_val_a", dcA);
		setText("dual_dc_val_b", dcB);
		const dcFillA = document.getElementById("dual_dc_fill_a");
		const dcFillB = document.getElementById("dual_dc_fill_b");
		if(dcFillA) dcFillA.style.width = Math.round((dcA/dcMax)*100) + "%";
		if(dcFillB) dcFillB.style.width = Math.round((dcB/dcMax)*100) + "%";

		// Donut para o mesmo comparativo
		const sumDC = Math.max(0, dcA + dcB);
		const donut = document.getElementById("donut_dc");
		const la = document.getElementById("donut_dc_a");
		const lb = document.getElementById("donut_dc_b");
		const pa = document.getElementById("donut_dc_pct_a");
		const pb = document.getElementById("donut_dc_pct_b");
		if(donut){
			let pctA = 0, pctB = 0;
			if(sumDC > 0){
				pctA = Math.round((dcA / sumDC) * 100);
				pctB = 100 - pctA; // evita arredondamento somar 101
			}else{
				pctA = 0; pctB = 0;
			}
			const angle = Math.round((pctA/100) * 360);
			donut.style.setProperty("--angA", angle + "deg");
			if(la) la.textContent = String(dcA);
			if(lb) lb.textContent = String(dcB);
			if(pa) pa.textContent = pctA + "%";
			if(pb) pb.textContent = pctB + "%";
		}

		// Comparativo Veículos pendentes x Fichas antecipadas (valores absolutos)
		const vpA = Math.max(0, parseInt((data.veiculos_pendentes && data.veiculos_pendentes.qtd) || 0, 10));
		const vpB = Math.max(0, parseInt((data.antecipados && data.antecipados.qtd) || 0, 10));
		const vpMax = Math.max(1, vpA, vpB);
		setText("dual_vp_val_a", vpA);
		setText("dual_vp_val_b", vpB);
		const vpFillA = document.getElementById("dual_vp_fill_a");
		const vpFillB = document.getElementById("dual_vp_fill_b");
		if(vpFillA) vpFillA.style.width = Math.round((vpA/vpMax)*100) + "%";
		if(vpFillB) vpFillB.style.width = Math.round((vpB/vpMax)*100) + "%";

		// Donut para Veículos pendentes x Fichas antecipadas
		const sumVP = Math.max(0, vpA + vpB);
		const donutVP = document.getElementById("donut_vp");
		const laVP = document.getElementById("donut_vp_a");
		const lbVP = document.getElementById("donut_vp_b");
		if(donutVP){
			let pctA2 = 0;
			if(sumVP > 0){
				pctA2 = Math.round((vpA / sumVP) * 100);
			}else{
				pctA2 = 0;
			}
			const angle2 = Math.round((pctA2/100) * 360);
			donutVP.style.setProperty("--angA", angle2 + "deg");
			if(laVP) laVP.textContent = String(vpA);
			if(lbVP) lbVP.textContent = String(vpB);
		}

		// Progresso do dia (Fichas finalizadas / Total de fichas) e extra = Paletes Pendentes
		const fichasTotal = Math.max(0, parseInt(t.total_fichas||0,10));
		const fichasFeitasRaw = Math.max(0, parseInt(t.fichas_finalizadas||0,10));
		const fichasFeitas = Math.min(fichasTotal||0, fichasFeitasRaw);
		const fichasPct = fichasTotal > 0 ? Math.round((fichasFeitas / fichasTotal) * 100) : 0;
		setText("fichas_total", fichasTotal);
		setText("fichas_done", fichasFeitasRaw);
		setText("fichas_pct", fichasPct);
		const fichasBar = document.getElementById("fichas_fill");
		if(fichasBar) {
			fichasBar.style.width = fichasPct + "%";
			fichasBar.classList.remove("bar-red", "bar-yellow", "bar-green");
			if(fichasPct <= 70){
				fichasBar.classList.add("bar-red");
			}else if(fichasPct <= 90){
				fichasBar.classList.add("bar-yellow");
			}else{
				fichasBar.classList.add("bar-green");
			}
		}
		const fichasExtraBlock = document.getElementById("fichas_extra_block");
		if(fichasExtraBlock){
			const pend = Math.max(0, parseInt(t.paletes_pendentes||0,10));
			if(pend > 0 && fichasTotal > 0){
				const extraPct = Math.round((pend / fichasTotal) * 100);
				setText("fichas_extra_pct", extraPct);
				const fExtraFill = document.getElementById("fichas_extra_fill");
				if(fExtraFill){ fExtraFill.style.width = Math.min(100, Math.max(5, extraPct)) + "%"; }
				fichasExtraBlock.style.display = "block";
			} else {
				fichasExtraBlock.style.display = "none";
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

	// Toggle editor de observação (rich-text)
	const editBtn = document.getElementById("editObs");
	const editor = document.getElementById("obs_editor");
	const rte = document.getElementById("obs_rte");
	const save = document.getElementById("obs_save");
	const cancel = document.getElementById("obs_cancel");
	const toolbar = document.getElementById("obs_toolbar");
	const colorInput = document.getElementById("rte_color");
	const bgInput = document.getElementById("rte_bg");
	const fontSel = document.getElementById("rte_font");
	const sizeSel = document.getElementById("rte_size");
	const clearBtn = document.getElementById("rte_clear");
	editBtn.addEventListener("click", () => {
		if(editor.style.display === "none"){ // abrir
			// carrega HTML atual (visual se houver, senão gerar HTML a partir da lista atual)
			const date = document.getElementById("datePick").value;
			const visual = OBS_VISUAL.get(date);
			if(typeof visual === "string"){
				rte.innerHTML = visual;
			}else{
				const items = Array.from(document.querySelectorAll('#obs_list .obsItem')).map(x => `<p>${x.textContent.trim()}</p>`);
				rte.innerHTML = items.join("");
			}
			editor.style.display = "block";
			window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
		} else { // fechar
			editor.style.display = "none";
		}
	});
	
	save.addEventListener("click", () => {
		const date = document.getElementById("datePick").value;
		const html = rte.innerHTML;
		OBS_VISUAL.set(date, html);
		const wrap = document.getElementById("obs_list");
		if(wrap){ wrap.innerHTML = html; }
		editor.style.display = "none";
	});

	cancel.addEventListener("click", () => {
		editor.style.display = "none";
	});

	// Toolbar handlers
	toolbar.addEventListener("click", (ev) => {
		const btn = ev.target.closest('button');
		if(!btn) return;
		const cmd = btn.getAttribute('data-cmd');
		const val = btn.getAttribute('data-val');
		if(!cmd) return;
		if(cmd === 'formatBlock'){
			document.execCommand(cmd, false, val);
		}else{
			document.execCommand(cmd, false, null);
		}
		rte.focus();
	});

	colorInput.addEventListener('input', () => {
		document.execCommand('foreColor', false, colorInput.value);
		rte.focus();
	});
	bgInput.addEventListener('input', () => {
		document.execCommand('hiliteColor', false, bgInput.value);
		rte.focus();
	});
	fontSel.addEventListener('change', () => {
		document.execCommand('fontName', false, fontSel.value);
		rte.focus();
	});
	sizeSel.addEventListener('change', () => {
		const sz = parseInt(sizeSel.value,10);
		if(sz){
			// Mapear px aproximado para 1-7 (legacy), depois normalizar via inline style
			document.execCommand('fontSize', false, '4'); // aplica tamanho base
			// ajustar spans gerados
			Array.from(rte.querySelectorAll('font[size]')).forEach(el => {
				el.removeAttribute('size');
				el.style.fontSize = sz+'px';
			});
		}
		rte.focus();
	});
	clearBtn.addEventListener('click', () => {
		rte.innerHTML = '';
		rte.focus();
	});
	carregarDia();
});

