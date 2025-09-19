const API_BASE = "http://127.0.0.1:8765"; // iniciado pelo app desktop
let MODE_TEMPORAL = false;

async function fetchDia(dateStr){
	const url = `${API_BASE}/api/dia?date=${encodeURIComponent(dateStr)}`;
	const res = await fetch(url);
	if(!res.ok) throw new Error("Erro ao buscar dia");
	return res.json();
}

// Busca dados agregados por período [start, end] inclusivo
async function fetchPeriodo(startStr, endStr){
	const url = `${API_BASE}/api/periodo?start=${encodeURIComponent(startStr)}&end=${encodeURIComponent(endStr)}`;
	const res = await fetch(url);
	if(!res.ok) throw new Error("Erro ao buscar período");
	return res.json();
}

function toYmd(d){
	const yyyy = d.getFullYear();
	const mm = String(d.getMonth()+1).padStart(2, "0");
	const dd = String(d.getDate()).padStart(2, "0");
	return `${yyyy}-${mm}-${dd}`;
}

async function fetchPeriodoFallback(startStr, endStr){
	// Faz loop por dias chamando /api/dia
	const start = new Date(startStr + 'T00:00:00');
	const end = new Date(endStr + 'T00:00:00');
	const out = [];
	if(isNaN(start) || isNaN(end) || start > end) return out;
	for(let d = new Date(start); d <= end; d.setDate(d.getDate()+1)){
		const ymd = toYmd(d);
		try{
			const resp = await fetchDia(ymd);
			const t = resp.totals || {};
			out.push({
				date: ymd,
				paletes_agendados: Number(t.paletes_agendados)||0,
				paletes_produzidos: Number(t.paletes_produzidos)||0,
			});
		}catch{
			out.push({ date: ymd, paletes_agendados: 0, paletes_produzidos: 0 });
		}
	}
	return out;
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
		if(typeof it.quantidade === 'number'){
			pctEl.textContent = `${it.quantidade} -> ${pct}%`;
		}else{
			pctEl.textContent = pct + "%";
		}

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
		// Total de quantidades (Descargas C3)
		try {
			const dItems = (data.descargas_c3 && data.descargas_c3.itens) || [];
			const sumDesc = dItems.reduce((acc, it) => acc + (parseInt(it.quantidade,10)||0), 0);
			const elSD = document.getElementById('sum_desc_qtd');
			if(elSD) elSD.textContent = `Total de paletes Descarregado C3: ${sumDesc}`;
		} catch {}

		setText("v_carr_qtd", (data.carregamentos_c3 && data.carregamentos_c3.qtd) ?? 0);
		renderList("list_carreg", (data.carregamentos_c3 && data.carregamentos_c3.itens) || []);
		// Total de quantidades (Carregamentos C3)
		try {
			const cItems = (data.carregamentos_c3 && data.carregamentos_c3.itens) || [];
			const sumCarr = cItems.reduce((acc, it) => acc + (parseInt(it.quantidade,10)||0), 0);
			const elSC = document.getElementById('sum_carr_qtd');
			if(elSC) elSC.textContent = `Total de paletes Carregados C3: ${sumCarr}`;
		} catch {}

		setText("v_pend_qtd", (data.veiculos_pendentes && data.veiculos_pendentes.qtd) ?? 0);
		renderList("list_pend", (data.veiculos_pendentes && data.veiculos_pendentes.itens) || []);
		// Total de quantidades (SOBRAS)
		try {
			const pItems = (data.veiculos_pendentes && data.veiculos_pendentes.itens) || [];
			const sumPend = pItems.reduce((acc, it) => acc + (parseInt(it.quantidade,10)||0), 0);
			const elSP = document.getElementById('sum_pend_qtd');
			if(elSP) elSP.textContent = `Total de SOBRAS: ${sumPend}`;
		} catch {}

	// Fichas antecipadas (itens são veículos antecipados)
	setText("v_antec_qtd", (data.antecipados && data.antecipados.qtd) ?? 0);
	renderList("list_antec", (data.antecipados && data.antecipados.itens) || []);
	// Total de quantidades (Fichas)
	try {
		const aItems = (data.antecipados && data.antecipados.itens) || [];
		const sumAnt = aItems.reduce((acc, it) => acc + (parseInt(it.quantidade,10)||0), 0);
		const elSA = document.getElementById('sum_antec_qtd');
		if(elSA) elSA.textContent = `Total de Paletes: ${sumAnt}`;
	} catch {}

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

		// Progresso do dia (Fichas finalizadas / Total de fichas)
		const fichasTotal = Math.max(0, parseInt(t.total_fichas||0,10));
		const fichasFeitasRaw = Math.max(0, parseInt(t.fichas_finalizadas||0,10));
		const fichasFeitas = Math.min(fichasTotal||0, fichasFeitasRaw);
		const fichasPctReal = fichasTotal > 0 ? Math.round((fichasFeitasRaw / fichasTotal) * 100) : 0; // pode ultrapassar 100
		const fichasPct = fichasTotal > 0 ? Math.round((fichasFeitas / fichasTotal) * 100) : 0;
		setText("fichas_total", fichasTotal);
		setText("fichas_done", fichasFeitasRaw);
		setText("fichas_pct", fichasPct);
		const fichasBar = document.getElementById("fichas_fill");
		if(fichasBar) {
			fichasBar.style.width = fichasPct + "%";
			fichasBar.classList.remove("bar-red", "bar-yellow", "bar-green", "bar-green-strong");
			if(fichasPctReal > 100){
				fichasBar.classList.add("bar-green-strong");
			}else if(fichasPct <= 70){
				fichasBar.classList.add("bar-red");
			}else if(fichasPct <= 90){
				fichasBar.classList.add("bar-yellow");
			}else{
				fichasBar.classList.add("bar-green");
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

	// Botão: Gráfico temporal (placeholder)
	const btnTemporal = document.getElementById("openTemporal");
	if(btnTemporal){
		btnTemporal.addEventListener("click", async () => {
			const dailySectionCards = document.getElementById('cards');
			const dailySectionLists = document.querySelector('section.lists');
			const temporalSection = document.getElementById('temporal_section');
			const titleEl = document.getElementById('pageTitle');
			const controls = document.getElementById('temporalControls');
			const dateInput = document.getElementById('datePick');
			const dateLabel = document.querySelector('label[for="datePick"]');
			const btnLoadDay = document.getElementById('loadDay');
			if(!MODE_TEMPORAL){
				// Entrar no modo temporal
				MODE_TEMPORAL = true;
				if(dailySectionCards) dailySectionCards.style.display = 'none';
				if(dailySectionLists) dailySectionLists.style.display = 'none';
				if(temporalSection) temporalSection.style.display = 'grid';
				if(controls) controls.style.display = 'inline-flex';
				if(titleEl) titleEl.textContent = 'Apresentação Gráfica — Recebimento CAD UDI';
				btnTemporal.textContent = 'Apresentação diária';
				// Oculta controles de seleção diária (label e botão Carregar; e também o input para limpar o head)
				if(dateLabel) dateLabel.style.display = 'none';
				if(dateInput) dateInput.style.display = 'none';
				if(btnLoadDay) btnLoadDay.style.display = 'none';
				// Preenche período padrão (últimos 7 dias)
				const end = new Date();
				const start = new Date(); start.setDate(end.getDate()-6);
				document.getElementById('rangeStart').value = toYmd(start);
				document.getElementById('rangeEnd').value = toYmd(end);
				// Auto-carregar período
				const clickEvt = new Event('click');
				document.getElementById('loadRange').dispatchEvent(clickEvt);
			}else{
				// Sair do modo temporal (voltar à diária)
				MODE_TEMPORAL = false;
				if(temporalSection) temporalSection.style.display = 'none';
				if(controls) controls.style.display = 'none';
				if(dailySectionCards) dailySectionCards.style.display = 'grid';
				if(dailySectionLists) dailySectionLists.style.display = 'grid';
				btnTemporal.textContent = 'Grafico temporal';
				// Restaura os controles diários no head
				if(dateLabel) dateLabel.style.display = '';
				if(dateInput) dateInput.style.display = '';
				if(btnLoadDay) btnLoadDay.style.display = '';
				// Atualiza o título de volta para diária com a data atual escolhida
				try{ await carregarDia(); }catch{}
			}
		});
	}

	const btnLoadRange = document.getElementById('loadRange');
	if(btnLoadRange){
		btnLoadRange.addEventListener('click', async () => {
			const s = document.getElementById('rangeStart').value;
			const e = document.getElementById('rangeEnd').value;
			if(!s || !e){
				alert('Informe o período (Entre ... e ...)');
				return;
			}
			try{
				let data;
				try{
					data = await fetchPeriodo(s, e);
				}catch{
					data = await fetchPeriodoFallback(s, e);
				}
				// Espera-se formato: [{date: 'YYYY-MM-DD', paletes_agendados: n, paletes_produzidos: n}, ...]
				const categories = [];
				const serieLine = [];
				const serieCol = [];
				const serieDesc = [];
				const serieCarr = [];
				for(const row of (data || [])){
					categories.push(row.date);
					serieLine.push(Number(row.paletes_agendados) || 0);
					serieCol.push(Number(row.paletes_produzidos) || 0);
					serieDesc.push(Number(row.descargas_c3) || 0);
					serieCarr.push(Number(row.carregamentos_c3) || 0);
				}

				// Colorir colunas com thresholds baseado em porcentagem diária (produzidos/agendados)
				const colors = serieCol.map((v, i) => {
					const total = Math.max(0, Number(serieLine[i]) || 0);
					const pct = total > 0 ? Math.round((v/total)*100) : 0;
					if(pct <= 70) return '#dc2626'; // vermelho
					if(pct <= 90) return '#f59e0b'; // amarelo
					return '#16a34a'; // verde
				});

				const el = document.querySelector('#temporal_chart');
				if(!el){ return; }
				if(window.__apexTemporal){
					try{ window.__apexTemporal.destroy(); }catch{}
				}
				// Montar series, com colunas coloridas por ponto
				const colData = categories.map((x, i) => ({ x, y: serieCol[i], fillColor: colors[i] }));
				const lineData = categories.map((x, i) => ({ x, y: serieLine[i] }));

				// Usar mesmo range de eixo Y para as duas séries para comparação direta
				const allVals = [...serieLine, ...serieCol];
				let yMax = 0;
				for(const v of allVals){ yMax = Math.max(yMax, Number(v)||0); }
				if(!isFinite(yMax) || yMax <= 0){ yMax = 1; }

				const options = {
					chart:{ type:'line', height: 360, stacked: false, toolbar:{show:true}, background: 'transparent', foreColor: '#cbd5e1' },
					theme:{ mode: 'dark', palette: 'palette10' },
					title:{ text: undefined },
					xaxis:{
						categories,
						labels:{ rotate: -25, style:{ colors: '#cbd5e1', fontSize: '12px' } },
						axisBorder:{ color:'#374151' },
						axisTicks:{ color:'#374151' }
					},
					yaxis:[
						{ seriesName:'Agendados', title:{text:'Agendados', style:{ color:'#9ca3af' }}, labels:{ style:{ colors:'#cbd5e1' }}, min:0, max: yMax },
						{ opposite:true, seriesName:'Produzidos', title:{text:'Produzidos', style:{ color:'#9ca3af' }}, labels:{ style:{ colors:'#cbd5e1' }}, min:0, max: yMax }
					],
					legend:{ position:'top', labels:{ colors:'#e5e7eb' } },
					stroke:{ width:[3,0], curve:'smooth' },
					markers:{ size:3, hover:{ size:6 } },
					grid:{ borderColor:'#1f2937', strokeDashArray:3 },
					plotOptions:{ bar:{ columnWidth:'55%', borderRadius: 2 } },
					dataLabels:{ enabled:false },
					series:[
						{ name:'Agendados (SIRF)', type:'line', data: lineData },
						{ name:'Produzidos (WMS)', type:'column', data: colData }
					],
					colors: ['#60a5fa', '#3b82f6'],
					fill:{ opacity:1 },
					distributed: true,
					tooltip:{
						shared:true,
						intersect:false,
						theme:'dark',
						custom: function({series, seriesIndex, dataPointIndex, w}){
							const date = w.globals.categoryLabels[dataPointIndex] || '';
							const ag = (series[0] && series[0][dataPointIndex]) || 0;
							const pr = (series[1] && series[1][dataPointIndex]) || 0;
							const pct = ag > 0 ? Math.round((pr/ag)*100) : 0;
							const [y,m,d] = String(date).split('-');
							const dateFmt = (y && m && d) ? `${d}/${m}/${y}` : date;
							return `
								<div class="apx-tip" style="background:#0b1220;border:1px solid #1f2937;color:#e5e7eb;padding:8px 10px;border-radius:6px;min-width:180px">
									<div style="font-weight:600;margin-bottom:6px;color:#93c5fd">${dateFmt}</div>
									<div style="display:flex;justify-content:space-between;gap:8px"><span>Agendados (SIRF)</span><span style="color:#93c5fd">${ag}</span></div>
									<div style="display:flex;justify-content:space-between;gap:8px"><span>Produzidos (WMS)</span><span style="color:${pct<=70?'#fca5a5':(pct<=90?'#fcd34d':'#86efac')}">${pr} (${pct}%)</span></div>
								</div>
							`;
						}
					}
				};
				// Gráfico Total (somatório do período) - Agendados vs Produzidos
				try{ if(window.__apexTemporalTotal){ window.__apexTemporalTotal.destroy(); } }catch{}
					const totalAg = serieLine.reduce((a,b)=>a+(Number(b)||0),0);
					const totalPr = serieCol.reduce((a,b)=>a+(Number(b)||0),0);
				const totalPct = totalAg>0 ? Math.round((totalPr/totalAg)*100) : 0;
					const totalSum = totalAg + totalPr;
					const totalDiff = totalPr - totalAg;
				const elTotal = document.querySelector('#temporal_total');
				if(elTotal){
						const optTotal = {
							chart:{ type:'bar', height:360, stacked:true, stackType:'100%', background:'transparent', foreColor:'#cbd5e1',
								animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } }
							},
							theme:{ mode:'dark' },
							title:{ text: undefined },
							xaxis:{ categories:['Total'], labels:{ style:{ colors:'#cbd5e1' } }, axisBorder:{ color:'#374151' }, axisTicks:{ color:'#374151' } },
							yaxis:{ min:0, max:100, tickAmount:5, labels:{ style:{ colors:'#cbd5e1' }, formatter:(v)=> `${Math.round(v)}%` } },
							plotOptions:{ bar:{ columnWidth:'60%', borderRadius:6, borderRadiusApplication:'end' } },
							dataLabels:{ enabled:true, formatter:(val,opts)=>{
								const idx = opts.seriesIndex;
								const tot = totalSum;
								if(tot<=0) return '0%';
								const pctAg = Math.round((totalAg/tot)*100);
								const pctPr = 100 - pctAg;
								return `${idx===0 ? pctAg : pctPr}%`;
							}, style:{ colors:['#e5e7eb'], fontSize:'12px', fontWeight:700 }, dropShadow:{ enabled:true, top:1, left:0, blur:2 } },
						series:[
							{ name:'Agendados', data:[ totalAg ] },
							{ name:'Produzidos', data:[ totalPr ] }
						],
							colors:['#60a5fa','#3b82f6'],
							fill:{ type:'gradient', gradient:{ shade:'dark', type:'vertical', shadeIntensity:0.25, gradientToColors:['#93c5fd','#60a5fa'], inverseColors:false, opacityFrom:0.9, opacityTo:0.95, stops:[0,90,100] } },
							states:{ hover:{ filter:{ type:'darken', value:0.7 } }, active:{ allowMultipleDataPointsSelection:true } },
							legend:{ show:true, position:'top', labels:{ colors:'#e5e7eb' } }, grid:{ borderColor:'#1f2937', strokeDashArray:3 },
						tooltip:{
							theme:'dark',
								custom: ({series, seriesIndex, dataPointIndex, w}) => {
								const ag = totalAg;
								const pr = totalPr;
								const tot = ag + pr;
								const pctAg = tot>0 ? Math.round((ag/tot)*100) : 0;
								const pctPr = 100 - pctAg;
									const diff = pr - ag;
									const diffColor = diff < 0 ? '#fca5a5' : (diff === 0 ? '#fcd34d' : '#86efac');
									const cAg = (w && w.globals && w.globals.colors) ? w.globals.colors[0] : '#60a5fa';
									const cPr = (w && w.globals && w.globals.colors) ? w.globals.colors[1] : '#3b82f6';
									return `
										<div class="apx-tip" style="background:#0b1220;border:1px solid #1f2937;color:#e5e7eb;padding:10px 12px;border-radius:10px;min-width:220px;box-shadow:0 6px 18px rgba(0,0,0,.35)">
											<div style="font-weight:700;margin-bottom:8px;color:#93c5fd">Total (somatório do período)</div>
											<div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cPr};margin-right:6px"></span>Produzidos</span><span style="color:#93c5fd">${Intl.NumberFormat('pt-BR').format(pr)} (${pctPr}%)</span></div>
											<div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cAg};margin-right:6px"></span>Agendados</span><span style="color:#93c5fd">${Intl.NumberFormat('pt-BR').format(ag)} (${pctAg}%)</span></div>
											<div style="display:flex;justify-content:space-between;gap:8px;margin-top:4px"><span>Diferença</span><span style="color:${diffColor}">${Intl.NumberFormat('pt-BR').format(diff)}</span></div>
											<div style="margin-top:8px;border-top:1px solid #1f2937;padding-top:8px;display:flex;justify-content:space-between;gap:8px"><span>Soma</span><span>${Intl.NumberFormat('pt-BR').format(tot)}</span></div>
										</div>
									`;
							}
						}
					};
					window.__apexTemporalTotal = new ApexCharts(elTotal, optTotal);
					window.__apexTemporalTotal.render();
				}
				window.__apexTemporal = new ApexCharts(el, options);
				window.__apexTemporal.render();

				// ===== Gráfico temporal C3 =====
				const elC3 = document.querySelector('#temporal_chart_c3');
				if(elC3){
					if(window.__apexTemporalC3){ try{ window.__apexTemporalC3.destroy(); }catch{} }
					// Removida lógica de cores por faixa no C3; usar cor uniforme padrão da série
					const colDataC3 = categories.map((x,i)=>({x, y: serieCarr[i]}));
					const lineDataC3 = categories.map((x,i)=>({x, y: serieDesc[i]}));
					const allValsC3 = [...serieDesc, ...serieCarr];
					let yMaxC3 = 0; for(const v of allValsC3){ yMaxC3 = Math.max(yMaxC3, Number(v)||0); }
					if(!isFinite(yMaxC3) || yMaxC3 <= 0){ yMaxC3 = 1; }
					const optionsC3 = {
						chart:{
							type:'line', height: 360, stacked:false, toolbar:{show:true}, background:'transparent', foreColor:'#cbd5e1',
							animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } },
							dropShadow:{ enabled:true, enabledOnSeries:[0], top:2, left:0, blur:4, color:'#000000', opacity:0.2 }
						},
						theme:{ mode:'dark', palette:'palette10' },
						title:{ text: undefined },
						xaxis:{ categories, labels:{ rotate:-25, style:{ colors:'#cbd5e1', fontSize:'12px' } }, axisBorder:{ color:'#374151' }, axisTicks:{ color:'#374151' } },
						yaxis:[
							{ seriesName:'Descargas C3', title:{text:'Descargas C3', style:{ color:'#9ca3af' }}, labels:{ style:{ colors:'#cbd5e1' }, formatter: (val)=> Intl.NumberFormat('pt-BR').format(Math.round(val)) }, min:0, max:yMaxC3 },
							{ opposite:true, seriesName:'Carregamentos C3', title:{text:'Carregamentos C3', style:{ color:'#9ca3af' }}, labels:{ style:{ colors:'#cbd5e1' }, formatter: (val)=> Intl.NumberFormat('pt-BR').format(Math.round(val)) }, min:0, max:yMaxC3 }
						],
						legend:{ position:'top', labels:{ colors:'#e5e7eb' } },
						stroke:{ width:[3,0], curve:'smooth', lineCap:'round' },
						markers:{ size:4, strokeWidth:2, strokeColors:'#0b1220', hover:{ size:7 } },
						grid:{ borderColor:'#1f2937', strokeDashArray:3 },
						plotOptions:{ bar:{ columnWidth:'50%', borderRadius:4 } }, dataLabels:{ enabled:false },
						series:[
							{ name:'Qtd Descarga C3', type:'line', data: lineDataC3 },
							{ name:'Qtd Carregamento C3', type:'column', data: colDataC3 }
						],
						colors:['#60a5fa', '#2563eb'],
						fill:{
							opacity:1,
							type:'gradient',
							gradient:{ shade:'dark', type:'vertical', shadeIntensity:0.25, gradientToColors:['#93c5fd', '#60a5fa'], inverseColors:false, opacityFrom:0.9, opacityTo:0.95, stops:[0,90,100] }
						},
						distributed:false,
						tooltip:{
							shared:true, intersect:false, theme:'dark',
							custom: function({series, dataPointIndex, w}){
								const date = w.globals.categoryLabels[dataPointIndex] || '';
								const de = (series[0] && series[0][dataPointIndex]) || 0;
								const ca = (series[1] && series[1][dataPointIndex]) || 0;
								const pct = de > 0 ? Math.round((ca/de)*100) : 0;
								const [y,m,d] = String(date).split('-');
								const dateFmt = (y && m && d) ? `${d}/${m}/${y}` : date;
								return `
									<div class="apx-tip" style="background:#0b1220;border:1px solid #1f2937;color:#e5e7eb;padding:8px 10px;border-radius:6px;min-width:200px">
										<div style="font-weight:600;margin-bottom:6px;color:#93c5fd">${dateFmt}</div>
										<div style="display:flex;justify-content:space-between;gap:8px"><span>Qtd Descarga C3</span><span style="color:#93c5fd">${de}</span></div>
										<div style="display:flex;justify-content:space-between;gap:8px"><span>Qtd Carregamento C3</span><span>${ca} (${pct}%)</span></div>
									</div>
								`;
							}
						}
					};
					// Gráfico Total (somatório do período) - Descargas vs Carregamentos C3
					try{ if(window.__apexTemporalTotalC3){ window.__apexTemporalTotalC3.destroy(); } }catch{}
					const totalDe = serieDesc.reduce((a,b)=>a+(Number(b)||0),0);
					const totalCa = serieCarr.reduce((a,b)=>a+(Number(b)||0),0);
					const totalPctC3 = totalDe>0 ? Math.round((totalCa/totalDe)*100) : 0;
					const elTotalC3 = document.querySelector('#temporal_total_c3');
					if(elTotalC3){
						const optTotalC3 = {
							chart:{ type:'bar', height:360, stacked:true, stackType:'100%', background:'transparent', foreColor:'#cbd5e1',
								animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } }
							},
							theme:{ mode:'dark' },
							title:{ text: undefined },
							xaxis:{ categories:['Total'], labels:{ style:{ colors:'#cbd5e1' } }, axisBorder:{ color:'#374151' }, axisTicks:{ color:'#374151' } },
							yaxis:{ min:0, max:100, tickAmount:5, labels:{ style:{ colors:'#cbd5e1' }, formatter:(v)=> `${Math.round(v)}%` } },
							plotOptions:{ bar:{ columnWidth:'60%', borderRadius:6, borderRadiusApplication:'end' } },
							dataLabels:{ enabled:true, formatter:(val,opts)=>{
								const idx = opts.seriesIndex;
								const tot = totalDe + totalCa;
								if(tot<=0) return '0%';
								const pctDe = Math.round((totalDe/tot)*100);
								const pctCa = 100 - pctDe;
								return `${idx===0 ? pctDe : pctCa}%`;
							}, style:{ colors:['#e5e7eb'], fontSize:'12px', fontWeight:700 }, dropShadow:{ enabled:true, top:1, left:0, blur:2 } },
							series:[
								{ name:'Descargas C3', data:[ totalDe ] },
								{ name:'Carregamentos C3', data:[ totalCa ] }
							],
							colors:['#60a5fa','#2563eb'],
							fill:{ type:'gradient', gradient:{ shade:'dark', type:'vertical', shadeIntensity:0.25, gradientToColors:['#93c5fd','#60a5fa'], inverseColors:false, opacityFrom:0.9, opacityTo:0.95, stops:[0,90,100] } },
							states:{ hover:{ filter:{ type:'darken', value:0.7 } }, active:{ allowMultipleDataPointsSelection:true } },
							legend:{ show:true, position:'top', labels:{ colors:'#e5e7eb' } }, grid:{ borderColor:'#1f2937', strokeDashArray:3 },
							tooltip:{
								theme:'dark',
								custom: ({series, seriesIndex, dataPointIndex, w}) => {
									const de = totalDe;
									const ca = totalCa;
									const tot = de + ca;
									const pctDe = tot>0 ? Math.round((de/tot)*100) : 0;
									const pctCa = 100 - pctDe;
									const cDe = (w && w.globals && w.globals.colors) ? w.globals.colors[0] : '#60a5fa';
									const cCa = (w && w.globals && w.globals.colors) ? w.globals.colors[1] : '#2563eb';
									return `
										<div class="apx-tip" style="background:#0b1220;border:1px solid #1f2937;color:#e5e7eb;padding:10px 12px;border-radius:10px;min-width:220px;box-shadow:0 6px 18px rgba(0,0,0,.35)">
											<div style="font-weight:700;margin-bottom:8px;color:#93c5fd">Total (somatório do período)</div>
											<div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cCa};margin-right:6px"></span>Carregamentos C3</span><span style="color:#93c5fd">${Intl.NumberFormat('pt-BR').format(ca)} (${pctCa}%)</span></div>
											<div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cDe};margin-right:6px"></span>Descargas C3</span><span style="color:#93c5fd">${Intl.NumberFormat('pt-BR').format(de)} (${pctDe}%)</span></div>
											<div style="margin-top:8px;border-top:1px solid #1f2937;padding-top:8px;display:flex;justify-content:space-between;gap:8px"><span>Soma</span><span>${Intl.NumberFormat('pt-BR').format(tot)}</span></div>
										</div>
									`;
								}
							}
						};
						window.__apexTemporalTotalC3 = new ApexCharts(elTotalC3, optTotalC3);
						window.__apexTemporalTotalC3.render();
					}
					window.__apexTemporalC3 = new ApexCharts(elC3, optionsC3);
					window.__apexTemporalC3.render();
				}
			}catch(err){
				console.error(err);
				alert('Erro ao carregar dados do período.');
			}
		});
	}

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

