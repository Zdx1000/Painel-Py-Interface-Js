const API_BASE = "http://127.0.0.1:8765"; // iniciado pelo app desktop
const THEME_STORAGE_KEY = "dashboardThemeStyle";
const THEME_MODE_STORAGE_KEY = "dashboardThemeMode";
const THEME_LABELS = {
	padrao: "Tema Padrão",
	oceano: "Tema Oceano",
	esmeralda: "Tema Esmeralda",
	solar: "Tema Solar",
	violeta: "Tema Violeta",
	grafite: "Tema Grafite"
};
let MODE_TEMPORAL = false;
let LAST_DAILY_DATA = null;

const TOOLTIP_ICONS = {
	calendar: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='#ffffff' stroke-width='1.8'><rect x='3' y='4.5' width='18' height='16.5' rx='2.5' ry='2.5' fill='#2563eb'/><path d='M3 9.5h18'/><path d='M8 3v3.5'/><path d='M16 3v3.5'/><circle cx='8.5' cy='13' r='1.2' fill='#ffffff'/><circle cx='12' cy='13' r='1.2' fill='#ffffff'/><circle cx='15.5' cy='13' r='1.2' fill='#ffffff'/></svg>",
	factory: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M3 21h18v-8l-5 3v-4l-5 3V7L3 9.5V21Z' fill='#0ea5e9'/><path d='M13 4c0-1.66 1.12-3 2.5-3S18 2.34 18 4v3h-5V4Z' fill='#038ac7'/><rect x='6.5' y='15' width='2.8' height='3.8' rx='0.6' fill='#ffffff'/><rect x='11' y='15' width='2.8' height='3.8' rx='0.6' fill='#ffffff'/><rect x='15.5' y='15' width='2.8' height='3.8' rx='0.6' fill='#ffffff'/></svg>",
	truck: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M3 6.5h9v9.5H3V6.5Z' fill='#f59e0b'/><path d='M12 10.5h4.6l2.8 3.4V16H12v-5.5Z' fill='#ea580c'/><circle cx='7.2' cy='17.6' r='1.9' fill='#25373f'/><circle cx='16.4' cy='17.6' r='1.9' fill='#25373f'/><path d='M6.5 5V3.8' stroke='#25373f' stroke-width='1.6' stroke-linecap='round'/><path d='M9.5 5V3.8' stroke='#25373f' stroke-width='1.6' stroke-linecap='round'/></svg>",
	warehouse: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M3 20V9.4L12 4l9 5.4V20H3Z' fill='#34d399'/><path d='M6.5 12.5h11v7.5h-11v-7.5Z' fill='#22b07d'/><rect x='8' y='14' width='3.8' height='6' fill='#ffffff'/><rect x='12.2' y='14' width='3.8' height='6' fill='#d1fae5'/></svg>",
	statUp: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M4 17 9.2 11.8l4 4 7-7' stroke='#22c55e' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/><path d='M16 8h4v4' stroke='#22c55e' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/><path d='M4 20h16' stroke='#22c55e' stroke-width='2.2' stroke-linecap='round'/></svg>",
	statDown: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M4 7 9.2 12.2l4-4 7 7' stroke='#ef4444' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/><path d='M16 16h4v-4' stroke='#ef4444' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/><path d='M4 20h16' stroke='#ef4444' stroke-width='2.2' stroke-linecap='round'/></svg>"
};

const BADGE_ICONS = {
	dashboardBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='3' y='4' width='18' height='16' rx='2.6' fill='#2563eb'/><path d='M3 9.2h18' stroke='#a5cafe' stroke-width='1.6' stroke-linecap='round'/><path d='M7.8 14.8 10.9 18l4.6-5.4 3.2 3.8' stroke='#f8fafc' stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'/></svg>",
	chartLineBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='3.2' y='3.2' width='17.6' height='17.6' rx='3.2' fill='#0ea5e9'/><path d='M7 16.5 10.8 12l2.6 2.9 4.6-6.2' stroke='#f8fafc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><path d='M6 18h12' stroke='#cffafe' stroke-width='1.6' stroke-linecap='round'/></svg>",
	calendarBadge: TOOLTIP_ICONS.calendar,
	factoryBadge: TOOLTIP_ICONS.factory,
	clipboardBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='5' y='4' width='14' height='17' rx='2.4' fill='#1d4ed8'/><path d='M10.4 4h3.2a1.6 1.6 0 0 1 1.6 1.6V7H8.8V5.6A1.6 1.6 0 0 1 10.4 4Z' fill='#1e40af'/><rect x='9' y='2.8' width='6' height='2.8' rx='1.2' fill='#f1f5f9'/><path d='M9 10.2h6' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/><path d='M9 14h6' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/><path d='M9 17.8h4' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/></svg>",
	checkBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><circle cx='12' cy='12' r='9' fill='#16a34a'/><path d='M8.4 12.6 11 15.2l4.8-6.4' stroke='#f8fafc' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/><circle cx='12' cy='12' r='9' stroke='#15803d' stroke-width='1.6'/></svg>",
	warningBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M11.2 4.1a1.6 1.6 0 0 1 1.6 0l7.8 4.4a1.6 1.6 0 0 1 .8 1.4v8.8a1.6 1.6 0 0 1-.8 1.4l-7.8 4.4a1.6 1.6 0 0 1-1.6 0l-7.8-4.4a1.6 1.6 0 0 1-.8-1.4V9.9a1.6 1.6 0 0 1 .8-1.4l7.8-4.4Z' fill='#f59e0b'/><path d='M12 7.2v6.4' stroke='#1f2937' stroke-width='1.9' stroke-linecap='round'/><circle cx='12' cy='16.8' r='1.1' fill='#1f2937'/></svg>",
	progressBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><circle cx='12' cy='12' r='9' fill='#2563eb'/><path d='M12 6.2a5.8 5.8 0 1 1-5.1 2.9' stroke='#bfdbfe' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><path d='M12 3v3.2' stroke='#f8fafc' stroke-width='2' stroke-linecap='round'/><path d='M12 12V8.4' stroke='#f8fafc' stroke-width='2.2' stroke-linecap='round'/><circle cx='12' cy='12' r='9' stroke='#1e3a8a' stroke-width='1.6'/></svg>",
	progressChecklistBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='5' y='4.2' width='14' height='15.6' rx='2.2' fill='#10b981'/><path d='M10.2 4.2H13a1.8 1.8 0 0 1 1.8 1.8v1.2H8.4V6a1.8 1.8 0 0 1 1.8-1.8Z' fill='#0d9b68'/><rect x='8.6' y='2.8' width='6.8' height='3' rx='1.4' fill='#ecfdf5'/><path d='M9 11h3.8' stroke='#d1fae5' stroke-width='1.6' stroke-linecap='round'/><path d='M9 14.4h5.2' stroke='#d1fae5' stroke-width='1.6' stroke-linecap='round'/><path d='M9 17.8h4' stroke='#d1fae5' stroke-width='1.6' stroke-linecap='round'/><path d='m14.6 11.8 1.6 1.6 3-3.6' stroke='#f8fafc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
	truckBadge: TOOLTIP_ICONS.truck,
	donutBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><circle cx='12' cy='12' r='9' fill='#1d4ed8'/><path d='M12 3a9 9 0 0 1 8.9 8.1L12 12V3Z' fill='#38bdf8'/><circle cx='12' cy='12' r='3.6' fill='#0f172a'/><circle cx='12' cy='12' r='9' stroke='#1e40af' stroke-width='1.6'/></svg>",
	editBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#1d4ed8'/><path d='m14.6 6.4 3 3L11 16.9l-3.4.6.6-3.4 6.4-7.7Z' fill='#bfdbfe'/><path d='m14.6 6.4 3 3' stroke='#1e293b' stroke-width='1.6' stroke-linecap='round'/><path d='M10.8 17.6 11 16l1.4 1.4-.9.2Z' fill='#1e293b'/></svg>",
	timelineBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='3.4' y='4' width='17.2' height='16' rx='3' fill='#0ea5e9'/><path d='M6.5 16.5h11' stroke='#cffafe' stroke-width='1.6' stroke-linecap='round'/><path d='m7 14 3.2-3.4 2.4 2.6 3.6-5 2.2 1.6' stroke='#f8fafc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><circle cx='10.2' cy='10.4' r='1.4' fill='#1e40af'/><circle cx='7' cy='14' r='1.3' fill='#1e40af'/><circle cx='12.6' cy='12.6' r='1.3' fill='#0f172a'/><circle cx='16.2' cy='8.2' r='1.3' fill='#0f172a'/></svg>",
	paletteBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M12 4a8 8 0 0 1 8 8c0 1.8-1 3.1-2.6 3.1h-1.4a1.6 1.6 0 0 0-1.6 1.6c0 1.5-1.1 2.7-2.6 2.7a8 8 0 1 1 0-16Z' fill='#2563eb'/><circle cx='9.5' cy='8.5' r='1.1' fill='#fbbf24'/><circle cx='14.2' cy='8.2' r='1.1' fill='#22c55e'/><circle cx='16.2' cy='11.2' r='1.1' fill='#f97316'/><circle cx='11.6' cy='6.8' r='1.1' fill='#f472b6'/></svg>",
	filterBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#1d4ed8'/><path d='M8 8h8l-3.6 4.7v4.6l-1.6-.8v-3.8L8 8Z' fill='#bfdbfe'/><path d='M8 8h8' stroke='#0f172a' stroke-width='1.6' stroke-linecap='round'/></svg>",
	pendingBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M11.2 4.4a1.6 1.6 0 0 1 1.6 0l7 4a1.6 1.6 0 0 1 .8 1.4v8.4a1.6 1.6 0 0 1-.8 1.4l-7 4a1.6 1.6 0 0 1-1.6 0l-7-4a1.6 1.6 0 0 1-.8-1.4V9.8a1.6 1.6 0 0 1 .8-1.4l7-4Z' fill='#f59e0b'/><path d='M12 8.4v5.4' stroke='#1f2937' stroke-width='1.9' stroke-linecap='round'/><circle cx='12' cy='16.5' r='1' fill='#1f2937'/></svg>",
	forwardBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#10b981'/><path d='m10 8 6 4-6 4V8Z' fill='#ecfdf5'/><path d='m10 8 6 4-6 4' stroke='#047857' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/><path d='M8 12h2' stroke='#ecfdf5' stroke-width='1.6' stroke-linecap='round'/></svg>",
	compareBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#2563eb'/><path d='m8 9 4 6 4-6' stroke='#bfdbfe' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/><path d='M7 14h10' stroke='#f8fafc' stroke-width='1.8' stroke-linecap='round'/><circle cx='12' cy='9' r='1.6' fill='#38bdf8'/></svg>",
	warehouseBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M4 18V9.2L12 4l8 5.2V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z' fill='#22c55e'/><path d='M7.5 12h9v8h-9v-8Z' fill='#15803d'/><path d='M9.8 13.8h2.4V18h-2.4v-4.2Z' fill='#ecfdf5'/><path d='M13.8 13.8h2.4V18h-2.4v-4.2Z' fill='#bbf7d0'/></svg>",
	downloadBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#2563eb'/><path d='M12 7.6v7.4' stroke='#f8fafc' stroke-width='2' stroke-linecap='round'/><path d='m8.8 12.4 3.2 3.4 3.2-3.4' stroke='#bfdbfe' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><path d='M8 16.8h8' stroke='#1e3a8a' stroke-width='1.6' stroke-linecap='round'/></svg>",
	uploadBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4' width='16' height='16' rx='2.8' fill='#10b981'/><path d='M12 16.4V9' stroke='#ecfdf5' stroke-width='2' stroke-linecap='round'/><path d='m8.8 11.6 3.2-3.4 3.2 3.4' stroke='#bbf7d0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/><path d='M8 16.8h8' stroke='#0f5132' stroke-width='1.6' stroke-linecap='round'/></svg>",
	noteBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='5' y='4' width='14' height='16' rx='2.4' fill='#1d4ed8'/><path d='M14.2 4v4.4H18' fill='#2563eb'/><path d='M9 11h6' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/><path d='M9 14h6' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/><path d='M9 17h4' stroke='#dbeafe' stroke-width='1.6' stroke-linecap='round'/></svg>",
	sunBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><circle cx='12' cy='12' r='4.2' fill='#fbbf24'/><path d='M12 4v2.4M12 20v-2.4M4 12h2.4M20 12h-2.4M6.7 6.7l1.7 1.7M17.3 17.3l-1.7-1.7M6.7 17.3l1.7-1.7M17.3 6.7l-1.7 1.7' stroke='#f59e0b' stroke-width='1.6' stroke-linecap='round'/></svg>",
	moonBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M14.6 3.6a7.4 7.4 0 1 0 7 10.5 6.2 6.2 0 0 1-7-10.5Z' fill='#1d4ed8'/><path d='M14.6 3.6a7.4 7.4 0 0 0 2.8 14.2' stroke='#93c5fd' stroke-width='1.6' stroke-linecap='round'/><circle cx='16.8' cy='8.4' r='0.9' fill='#93c5fd'/><circle cx='18.6' cy='11.4' r='0.7' fill='#93c5fd'/></svg>",
	stackBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M6.2 8.4 12 5.4l5.8 3-5.8 3-5.8-3Z' fill='#2563eb'/><path d='m6.2 12.2 5.8 3 5.8-3' stroke='#1e3a8a' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/><path d='M6.2 16l5.8 3 5.8-3' stroke='#60a5fa' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/><path d='m6.2 12.2 5.8-3 5.8 3-5.8 3-5.8-3Z' fill='#1d4ed8' opacity='.85'/></svg>",
	deltaBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><rect x='4' y='4.4' width='16' height='15.2' rx='2.6' fill='#f97316'/><path d='m7.6 16.4 4.4-8.8 4.4 8.8H7.6Z' stroke='#f8fafc' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/><path d='m11.2 11.2 1.6 3.2h-3.2l1.6-3.2Z' fill='#f8fafc'/><path d='M7.6 16.4h8.8' stroke='#9a3412' stroke-width='1.6' stroke-linecap='round'/></svg>",
	leaderBadge: "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M5.6 9.2 8 7.4l2.6 2.2L12 6l1.4 3.6L16 7.4l2.4 1.8-.8 7.2H6.4l-.8-7.2Z' fill='#22c55e'/><path d='M6.4 16.4h11.2l-.6 2.4H7l-.6-2.4Z' fill='#15803d'/><path d='M12 6 13.4 9.6 16 7.4l2.4 1.8-.8 7.2H6.4l-.8-7.2L8 7.4l2.6 2.2L12 6Z' stroke='#14532d' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/><path d='M9.2 18.8h5.6' stroke='#bbf7d0' stroke-width='1.4' stroke-linecap='round'/></svg>"
};

function injectIconBadges(){
	const targets = document.querySelectorAll("[data-icon]");
	targets.forEach(target => {
		const key = target.dataset.icon;
		if(!key) return;
		const iconSvg = BADGE_ICONS[key] || TOOLTIP_ICONS[key];
		let badge = target.querySelector(":scope > .icon-badge");
		if(!badge){
			badge = document.createElement("span");
			badge.className = "icon-badge";
			badge.setAttribute("aria-hidden", "true");
			target.prepend(badge);
		}
		if(!badge.hasAttribute("aria-hidden")){
			badge.setAttribute("aria-hidden", "true");
		}
		const tone = target.dataset.iconTone || "";
		const size = target.dataset.iconSize || "";
		if(tone){
			badge.setAttribute("data-tone", tone);
		}else{
			badge.removeAttribute("data-tone");
		}
		if(size){
			badge.setAttribute("data-size", size);
		}else{
			badge.removeAttribute("data-size");
		}
		if(iconSvg){
			badge.innerHTML = iconSvg;
			badge.style.display = "inline-flex";
		}else{
			badge.innerHTML = "";
			badge.style.display = "none";
		}
	});
}

function refreshTemporalIfActive(){
	if(!MODE_TEMPORAL) return;
	const btn = document.getElementById("loadRange");
	if(btn){
		setTimeout(() => {
			try{
				btn.click();
			}catch{}
		}, 16);
	}
}

function readCSSVar(varName, fallback = ""){
	const styles = getComputedStyle(document.documentElement);
	const value = styles.getPropertyValue(varName);
	return value ? value.trim() : fallback;
}

function getChartThemeColors(){
	const styles = getComputedStyle(document.documentElement);
	const pick = (name, fallback) => {
		const value = styles.getPropertyValue(name);
		return value ? value.trim() : fallback;
	};
	const text = pick("--chart-text-primary", pick("--text", "#1f2937"));
	const muted = pick("--chart-text-muted", pick("--muted", "#64748b"));
	const border = pick("--chart-border-color", pick("--border", "rgba(148,163,184,0.35)"));
	const grid = pick("--chart-grid-color", pick("--list-border-color", border));
	const tooltipBackground = pick("--chart-tooltip-bg", "#0b1220");
	const tooltipBorder = pick("--chart-tooltip-border", border);
	const tooltipText = pick("--chart-tooltip-text", text);
	const tooltipMuted = pick("--chart-tooltip-muted", muted);
	const tooltipAccent = pick("--chart-tooltip-accent", pick("--accent", text));
	const tooltipShadow = pick("--chart-tooltip-shadow", "rgba(0,0,0,0.35)");
	const annotationBackground = pick("--chart-annotation-bg", tooltipBackground);
	const annotationBorder = pick("--chart-annotation-border", tooltipBorder);
	const annotationText = pick("--chart-annotation-text", tooltipText);
	const annotationShadow = pick("--chart-annotation-shadow", tooltipShadow);
	const annotationFill = pick("--chart-annotation-fill", "rgba(96,165,250,0.22)");
	const series = {
		linePrimary: pick("--chart-series-line-primary", "#60a5fa"),
		lineSecondary: pick("--chart-series-line-secondary", "#3b82f6"),
		columnPrimary: pick("--chart-series-column-primary", "#3b82f6"),
		columnSecondary: pick("--chart-series-column-secondary", "#2563eb"),
		gradientPrimaryTo: pick("--chart-series-gradient-primary-to", "#93c5fd"),
		gradientSecondaryTo: pick("--chart-series-gradient-secondary-to", "#60a5fa"),
		totalGradientFrom: pick("--chart-total-gradient-from", "#60a5fa"),
		totalGradientTo: pick("--chart-total-gradient-to", "#93c5fd"),
		totalAltGradientFrom: pick("--chart-total-alt-gradient-from", "#3b82f6"),
		totalAltGradientTo: pick("--chart-total-alt-gradient-to", "#60a5fa"),
		markerStroke: pick("--chart-marker-stroke-color", "rgba(31,75,153,0.35)"),
		dropShadow: pick("--chart-drop-shadow-color", "rgba(0,0,0,0.2)")
	};
	const thresholds = {
		low: pick("--chart-threshold-low", "#dc2626"),
		lowSoft: pick("--chart-threshold-low-soft", "rgba(220,38,38,0.15)"),
		lowText: pick("--chart-threshold-low-text", "#fca5a5"),
		medium: pick("--chart-threshold-medium", "#f59e0b"),
		mediumSoft: pick("--chart-threshold-medium-soft", "rgba(245,158,11,0.18)"),
		mediumText: pick("--chart-threshold-medium-text", "#fcd34d"),
		high: pick("--chart-threshold-high", "#16a34a"),
		highSoft: pick("--chart-threshold-high-soft", "rgba(22,163,74,0.18)"),
		highText: pick("--chart-threshold-high-text", "#86efac"),
		warning: pick("--chart-threshold-warning", "#f97316"),
		warningSoft: pick("--chart-threshold-warning-soft", "rgba(249,115,22,0.16)")
	};
	return {
		text,
		muted,
		border,
		grid,
		tooltip:{
			background: tooltipBackground,
			border: tooltipBorder,
			text: tooltipText,
			muted: tooltipMuted,
			accent: tooltipAccent,
			shadow: tooltipShadow
		},
		annotation:{
			background: annotationBackground,
			border: annotationBorder,
			text: annotationText,
			shadow: annotationShadow,
			fill: annotationFill
		},
		series,
		thresholds
	};
}

function buildTemporalAnnotations(categories, referenceSeries, comparisonSeries, config){
	const { referenceLabel, comparisonLabel, palette } = config;
	const refValues = categories.map((_, idx) => Number(referenceSeries[idx]) || 0);
	const cmpValues = categories.map((_, idx) => Number(comparisonSeries[idx]) || 0);
	const avgRef = refValues.length ? refValues.reduce((a,b)=>a+b,0) / refValues.length : 0;
	const avgCmp = cmpValues.length ? cmpValues.reduce((a,b)=>a+b,0) / cmpValues.length : 0;
	let peakIdx = -1;
	let peakVal = -Infinity;
	let troughIdx = -1;
	let troughVal = Infinity;
	let bestDiffIdx = -1;
	let bestDiffVal = -Infinity;
	let worstDiffIdx = -1;
	let worstDiffVal = Infinity;
	cmpValues.forEach((val, idx) => {
		if(val > peakVal){ peakVal = val; peakIdx = idx; }
		if(val < troughVal){ troughVal = val; troughIdx = idx; }
		const diff = val - refValues[idx];
		if(diff > bestDiffVal){ bestDiffVal = diff; bestDiffIdx = idx; }
		if(diff < worstDiffVal){ worstDiffVal = diff; worstDiffIdx = idx; }
	});
	const fmtInt = (value) => Intl.NumberFormat('pt-BR').format(Math.round(value));
	const fmtAbs = (value) => Intl.NumberFormat('pt-BR').format(Math.abs(Math.round(value)));
	const thresholds = (palette && palette.thresholds) || {};
	const positive = thresholds.high || '#16a34a';
	const positiveSoft = thresholds.highSoft || 'rgba(22,163,74,0.18)';
	const positiveText = thresholds.highText || positive;
	const warning = thresholds.warning || '#f97316';
	const warningSoft = thresholds.warningSoft || 'rgba(249,115,22,0.16)';
	const warningText = thresholds.mediumText || warning;
	const negative = thresholds.low || '#dc2626';
	const negativeSoft = thresholds.lowSoft || 'rgba(220,38,38,0.15)';
	const negativeText = thresholds.lowText || negative;
	const markerStroke = palette.markerStroke || palette.accent || positive;
	const annotationPalette = palette.annotation || {};
	const ensureColor = (value, fallback) => {
		const color = (value || '').trim();
		if(!color || color === 'transparent' || color.includes('color-mix')){ return fallback; }
		return color;
	};
	const clamp01 = (val) => Math.max(0, Math.min(1, val));
	const toRgba = (rawColor) => {
		const color = rawColor.trim();
		if(color.startsWith('#')){
			let hex = color.slice(1);
			if(hex.length === 3){ hex = hex.split('').map((c)=>c+c).join(''); }
			if(hex.length !== 6){ return null; }
			const r = parseInt(hex.slice(0,2),16);
			const g = parseInt(hex.slice(2,4),16);
			const b = parseInt(hex.slice(4,6),16);
			if(Number.isNaN(r) || Number.isNaN(g) || Number.isNaN(b)){ return null; }
			return { r, g, b };
		}
		const rgbMatch = color.match(/^rgba?\(([^)]+)\)$/i);
		if(rgbMatch){
			const parts = rgbMatch[1].split(',').map((p)=>p.trim());
			if(parts.length < 3){ return null; }
			const [r,g,b] = parts;
			return { r: parseFloat(r), g: parseFloat(g), b: parseFloat(b) };
		}
		return null;
	};
	const withAlpha = (colorValue, alpha = 0.35, fallback = '#60a5fa') => {
		const baseColor = ensureColor(colorValue, fallback);
		const normalized = toRgba(baseColor) || toRgba(fallback);
		const a = clamp01(alpha);
		return `rgba(${(normalized?.r ?? 96)}, ${(normalized?.g ?? 165)}, ${(normalized?.b ?? 250)}, ${a})`;
	};
	const tooltipBg = ensureColor(palette.tooltipBg, 'rgba(96,165,250,0.18)');
	const tooltipTextColor = ensureColor(palette.tooltipText, '#f8fafc');
	const tooltipMutedColor = ensureColor(palette.tooltipMuted, tooltipTextColor);
	const annotationBg = ensureColor(annotationPalette.background, tooltipBg) || tooltipBg;
	const annotationBorder = ensureColor(annotationPalette.border, palette.muted || palette.accent || '#1f2937');
	const annotationText = ensureColor(annotationPalette.text, tooltipTextColor);
	const annotationMutedText = tooltipMutedColor;
	const annotationAccentText = ensureColor(palette.accent, tooltipTextColor) || tooltipTextColor;
	const annotationShadow = ensureColor(annotationPalette.shadow, palette.tooltipShadow || 'rgba(0,0,0,0.38)');
	const annotationFill = ensureColor(annotationPalette.fill, withAlpha(annotationBg, 0.45, annotationBg)) || withAlpha(annotationBg, 0.45, annotationBg);
	const basePadding = '4px 10px';
	const tint = (color, amount = 0.32, fallback) => withAlpha(color, amount, fallback || annotationFill || annotationBg);
	const mixBackground = (color, amount = 0.5) => withAlpha(color || annotationBg, amount, annotationBg);
	const applyStyle = (overrides = {}) => {
		const styled = {
			background: annotationBg,
			color: annotationText,
			fontWeight: 600,
			padding: basePadding,
			letterSpacing: '0.02em',
			...overrides
		};
		if(annotationShadow){ styled.boxShadow = `0 18px 32px ${annotationShadow}`; }
		return styled;
	};
	const annotations = { position:'front', yaxis: [], xaxis: [], points: [] };
	if(refValues.length){
		annotations.yaxis.push({
			y: avgRef,
			borderColor: annotationBorder,
			strokeDashArray: 4,
			opacity: 0.28,
			fillColor: annotationFill,
			label:{
				borderColor: annotationBorder,
				borderWidth:1,
				borderRadius:8,
				style: applyStyle({ color: annotationMutedText }),
				text: `⌀ ${referenceLabel}: ${fmtInt(avgRef)}`,
				orientation: 'horizontal',
				position: 'left',
				textAnchor: 'start',
				offsetX: -20,
				offsetY: -6
			}
		});
	}
	if(cmpValues.length){
		annotations.yaxis.push({
			y: avgCmp,
			borderColor: palette.accent || annotationBorder,
			strokeDashArray: 4,
			opacity: 0.32,
			fillColor: tint(palette.accent || annotationFill, 0.5),
			label:{
				borderColor: palette.accent || annotationBorder,
				borderWidth:1,
				borderRadius:8,
				style: applyStyle({ color: palette.accent || annotationAccentText }),
				text: `⌀ ${comparisonLabel}: ${fmtInt(avgCmp)}`,
				orientation: 'horizontal',
				position: 'right',
				textAnchor: 'start',
				offsetX: 20,
				offsetY: -6
			}
		});
	}
	if(peakIdx >= 0 && Number.isFinite(peakVal)){
		annotations.points.push({
			x: categories[peakIdx],
			y: peakVal,
			seriesIndex: 1,
			marker:{ size: 7, fillColor: positive, strokeColor: markerStroke, strokeWidth: 2 },
			label:{
				borderColor: positive,
				borderWidth:1,
				borderRadius:8,
				orientation: 'horizontal',
				textAnchor: 'middle',
				offsetY: -24,
				style: applyStyle({ background: mixBackground(positive, 0.5), color: positiveText, fontWeight:700 }),
				text: `Pico ${comparisonLabel}: ${fmtInt(peakVal)}`
			}
		});
	}
	if(troughIdx >= 0 && Number.isFinite(troughVal)){
		annotations.points.push({
			x: categories[troughIdx],
			y: troughVal,
			seriesIndex: 1,
			marker:{ size: 7, fillColor: warning, strokeColor: markerStroke, strokeWidth: 2 },
			label:{
				borderColor: warning,
				borderWidth:1,
				borderRadius:8,
				orientation: 'horizontal',
				textAnchor: 'middle',
				offsetY: 36,
				style: applyStyle({ background: mixBackground(warning, 0.45), color: warningText, fontWeight:700 }),
				text: `Ponto Crítico ${comparisonLabel}: ${fmtInt(troughVal)}`
			}
		});
	}
	if(bestDiffIdx >= 0 && bestDiffVal > 0){
		annotations.xaxis.push({
			x: categories[bestDiffIdx],
			borderColor: positive,
			strokeDashArray: 4,
			opacity: 0.32,
			fillColor: tint(positiveSoft || positive, 0.6),
			label:{
				borderColor: positive,
				borderWidth:1,
				borderRadius:8,
				style: applyStyle({ background: mixBackground(positive, 0.45), color: positiveText, fontWeight:700 }),
				text: `Maior Excedente: +${fmtInt(bestDiffVal)}`,
				orientation: 'vertical',
				offsetY: -10
			}
		});
	}
	if(worstDiffIdx >= 0 && worstDiffVal < 0){
		annotations.xaxis.push({
			x: categories[worstDiffIdx],
			borderColor: negative,
			strokeDashArray: 4,
			opacity: 0.32,
			fillColor: tint(negativeSoft || negative, 0.6),
			label:{
				borderColor: negative,
				borderWidth:1,
				borderRadius:8,
				style: applyStyle({ background: mixBackground(negative, 0.48), color: negativeText, fontWeight:700 }),
				text: `Maior Déficit: -${fmtAbs(worstDiffVal)}`,
				orientation: 'vertical',
				offsetY: 28
			}
		});
	}
	return annotations;
}

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

function setPageTitle(mainText, subText, extraText = ""){
	const titleEl = document.getElementById("pageTitle");
	if(!titleEl) return;
	const mainEl = titleEl.querySelector(".title-main");
	if(mainEl && typeof mainText === "string"){
		mainEl.textContent = mainText;
	}
	const subEl = titleEl.querySelector(".title-sub");
	if(subEl && typeof subText === "string"){
		subEl.textContent = subText;
	}
	const dividerEl = titleEl.querySelector(".title-divider");
	if(dividerEl){
		dividerEl.style.display = subText ? "" : "none";
	}
	const extraEl = document.getElementById("pageTitleExtra");
	if(extraEl){
		if(extraText){
			extraEl.textContent = extraText;
			extraEl.style.display = "inline-flex";
		}else{
			extraEl.textContent = "";
			extraEl.style.display = "none";
		}
	}
	injectIconBadges();
}

function safeSetStorage(key, value){
	try{
		localStorage.setItem(key, value);
	}catch{}
}

function safeGetStorage(key){
	try{
		return localStorage.getItem(key);
	}catch{
		return null;
	}
}

function applyThemeStyle(styleKey){
	const root = document.documentElement;
	if(!root) return;
	const normalized = styleKey || "padrao";
	root.setAttribute("data-style", normalized);
	safeSetStorage(THEME_STORAGE_KEY, normalized);
	updateThemeUI();
	refreshTemporalIfActive();
}

function applyThemeMode(modeKey){
	const root = document.documentElement;
	if(!root) return;
	const normalized = modeKey === "dark" ? "dark" : "light";
	root.setAttribute("data-mode", normalized);
	safeSetStorage(THEME_MODE_STORAGE_KEY, normalized);
	updateThemeUI();
	refreshTemporalIfActive();
}

function updateThemeUI(){
	const root = document.documentElement;
	if(!root) return;
	const currentStyle = root.getAttribute("data-style") || "padrao";
	const currentMode = root.getAttribute("data-mode") === "dark" ? "dark" : "light";
	const trigger = document.getElementById("themePickerButton");
	if(trigger){
		const label = THEME_LABELS[currentStyle] || THEME_LABELS.padrao;
		const modeLabel = currentMode === "dark" ? "Dark" : "Light";
		trigger.textContent = `${label} (${modeLabel})`;
		trigger.setAttribute("aria-label", `Selecionar tema. Atual: ${label} modo ${currentMode === "dark" ? "escuro" : "claro"}`);
	}
	const menu = document.getElementById("themePickerMenu");
	if(menu){
		menu.querySelectorAll(".theme-option").forEach(option => {
			const style = option.dataset.style;
			const isActiveStyle = style === currentStyle;
			option.classList.toggle("active", isActiveStyle);
			option.querySelectorAll("button[data-mode]").forEach(btn => {
				const mode = btn.dataset.mode === "dark" ? "dark" : "light";
				const isActive = isActiveStyle && mode === currentMode;
				btn.classList.toggle("active", isActive);
			});
		});
	}
	injectIconBadges();
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

function buildObsEmptyMarkup(){
	const icon = BADGE_ICONS.noteBadge || TOOLTIP_ICONS.calendar;
	return `
		<div class="obs-empty">
			<span class="obs-empty-icon">${icon}</span>
			<div class="obs-empty-body">
				<strong>Sem observações registradas.</strong>
				<p>Use o botão "Editar Observação" para adicionar comentários, destaques ou orientações para o time.</p>
			</div>
		</div>
	`;
}

function renderObsVisual(html){
	const wrap = document.getElementById("obs_list");
	if(!wrap) return;
	const safe = (html || "").trim();
	if(!safe){
		wrap.innerHTML = buildObsEmptyMarkup();
		return;
	}
	if(/class\s*=\s*"[^"]*obsRich[^"]*"/.test(safe) || /class\s*=\s*'[^']*obsRich[^']*'/.test(safe)){
		wrap.innerHTML = safe;
	}else{
		wrap.innerHTML = `<div class="obsRich">${safe}</div>`;
	}
}

function renderObs(objs){
	const wrap = document.getElementById("obs_list");
	if(!wrap) return;
	wrap.innerHTML = "";
	if(!objs || !objs.length){
		wrap.innerHTML = buildObsEmptyMarkup();
		return;
	}
	const timeline = document.createElement("div");
	timeline.className = "obsTimeline";
	objs.forEach((rawValue, idx) => {
		const raw = typeof rawValue === "string" ? rawValue : String(rawValue ?? "");
		const entry = document.createElement("article");
		entry.className = "obsCard";
		entry.dataset.index = String(idx + 1);
		entry.dataset.variant = (idx % 2 === 0) ? "base" : "alt";
		const icon = document.createElement("span");
		icon.className = "obsCard-icon";
		icon.innerHTML = BADGE_ICONS.noteBadge || TOOLTIP_ICONS.calendar;
		const body = document.createElement("div");
		body.className = "obsCard-body";
		const tag = document.createElement("span");
		tag.className = "obsCard-tag";
		tag.textContent = `Observação ${String(idx + 1).padStart(2, "0")}`;
		body.appendChild(tag);
		let heading = null;
		let detail = raw.trim();
		const colonMatch = detail.match(/^([^:]{3,80}):\s*(.+)$/);
		if(colonMatch){
			heading = colonMatch[1].trim();
			detail = colonMatch[2].trim();
			if(!detail){
				detail = heading;
				heading = null;
			}
		}
		if(heading){
			const title = document.createElement("h4");
			title.className = "obsCard-title";
			title.textContent = heading;
			body.appendChild(title);
		}
		const normalized = detail.replace(/\r\n/g, "\n");
		let segments = normalized.split(/\n+/).map(s => s.trim()).filter(Boolean);
		if(segments.length <= 1){
			const semi = normalized.split(/\s*;\s*/).map(s => s.trim()).filter(Boolean);
			if(semi.length > 1){
				segments = semi;
			}
		}
		if(segments.length > 1){
			const list = document.createElement("ul");
			list.className = "obsCard-list";
			segments.forEach(segment => {
				const li = document.createElement("li");
				li.textContent = segment;
				list.appendChild(li);
			});
			body.appendChild(list);
		}else{
			const textEl = document.createElement("p");
			textEl.className = "obsCard-text";
			textEl.textContent = segments[0] || normalized || raw;
			body.appendChild(textEl);
		}
		entry.appendChild(icon);
		entry.appendChild(body);
		timeline.appendChild(entry);
	});
	wrap.appendChild(timeline);
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
	const parts = val.split("-");
	if(parts.length === 3){
		const [y, m, d] = parts;
		setPageTitle("Recebimento CAD UDI", "", `(${d}/${m}/${y})`);
	}else{
		setPageTitle("Recebimento CAD UDI", "");
	}
	try{
		const data = await fetchDia(val);
		LAST_DAILY_DATA = data;
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
		if(typeof visual === "string"){
			renderObsVisual(visual);
		}else{
			renderObs(data.observacoes || []);
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
		const extraFill = document.getElementById("prog_extra_fill");
		const extra = feitoRaw - total;
		if(extraBlock){
			if(extra > 0 && total > 0){
				const extraPct = Math.round((extra/total)*100);
				setText("prog_extra_pct", extraPct);
				if(extraFill){
					// limite visual de 100% para a barra extra
					const width = Math.max(5, Math.min(100, extraPct));
					extraFill.style.width = width + "%";
					extraFill.classList.add("alert");
				}

				extraBlock.style.display = "block";
			}else{
				extraBlock.style.display = "none";
				if(extraFill){
					extraFill.style.width = "0%";
					extraFill.classList.remove("alert");
				}
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

		
		// Comparativo Veículo Granel x Veículo Paletizado
		const vgA = Math.max(0, parseInt(t.chamado_granel || 0, 10));
		const vgB = Math.max(0, parseInt(t.paletizada || 0, 10));
		const vgMax = Math.max(1, vgA, vgB);
		setText("dual_granel_val_a", vgA);
		setText("dual_granel_val_b", vgB);
		const vgFillA = document.getElementById("dual_granel_fill_a");
		const vgFillB = document.getElementById("dual_granel_fill_b");
		if(vgFillA) vgFillA.style.width = Math.round((vgA/vgMax)*100) + "%";
		if(vgFillB) vgFillB.style.width = Math.round((vgB/vgMax)*100) + "%";

		const sumVG = Math.max(0, vgA + vgB);
		const donutVG = document.getElementById("donut_granel");
		const laVG = document.getElementById("donut_granel_a");
		const lbVG = document.getElementById("donut_granel_b");
		const pctVG_A = document.getElementById("donut_granel_pct_a");
		const pctVG_B = document.getElementById("donut_granel_pct_b");
		if(donutVG){
			let pctA3 = 0, pctB3 = 0;
			if(sumVG > 0){
				pctA3 = Math.round((vgA / sumVG) * 100);
				pctB3 = 100 - pctA3;
			}
			const angle3 = Math.round((pctA3/100) * 360);
			donutVG.style.setProperty("--angA", angle3 + "deg");
			if(laVG) laVG.textContent = String(vgA);
			if(lbVG) lbVG.textContent = String(vgB);
			if(pctVG_A) pctVG_A.textContent = pctA3 + "%";
			if(pctVG_B) pctVG_B.textContent = pctB3 + "%";
		}
		setText("chip_granel_total", sumVG);
		setText("chip_granel_diff", Math.abs(vgA - vgB));
		let leaderLabel = "—";
		if(sumVG > 0){
			if(vgA === vgB){
				leaderLabel = "Empate";
			}else if(vgA > vgB){
				leaderLabel = "Granel";
			}else{
				leaderLabel = "Paletizado";
			}
		}
		setText("chip_granel_leader", leaderLabel);

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
	setPageTitle("Recebimento CAD UDI", "", `(${dd}/${mm}/${yyyy})`);

	// Inicializa tema salvo
	const root = document.documentElement;
	let initialMode = root.getAttribute("data-mode") || "light";
	let initialStyle = root.getAttribute("data-style") || "padrao";
	const storedMode = safeGetStorage(THEME_MODE_STORAGE_KEY);
	if(storedMode){
		initialMode = storedMode;
	}
	applyThemeMode(initialMode);
	const storedStyle = safeGetStorage(THEME_STORAGE_KEY);
	if(storedStyle){
		initialStyle = storedStyle;
	}
	applyThemeStyle(initialStyle);
	updateThemeUI();
	const themePicker = document.getElementById("themePicker");
	const themeButton = document.getElementById("themePickerButton");
	const themeMenu = document.getElementById("themePickerMenu");
	if(themePicker && themeButton && themeMenu){
		let hoverTimer = null;
		const closeMenu = () => {
			themePicker.classList.remove("open");
			themeButton.setAttribute("aria-expanded", "false");
		};
		const openMenu = () => {
			themePicker.classList.add("open");
			themeButton.setAttribute("aria-expanded", "true");
		};
		themeButton.addEventListener("click", () => {
			if(themePicker.classList.contains("open")){
				closeMenu();
			}else{
				openMenu();
			}
		});
		themePicker.addEventListener("mouseenter", () => {
			if(hoverTimer){
				clearTimeout(hoverTimer);
				hoverTimer = null;
			}
			openMenu();
		});
		themePicker.addEventListener("mouseleave", () => {
			hoverTimer = setTimeout(() => {
				closeMenu();
				hoverTimer = null;
			}, 160);
		});
		themeButton.addEventListener("keydown", evt => {
			if(evt.key === "ArrowDown" || evt.key === "Enter" || evt.key === " "){
				evt.preventDefault();
				openMenu();
				const firstMode = themeMenu.querySelector("button[data-mode]");
				if(firstMode){
					firstMode.focus();
				}
			}
		});
		themeMenu.addEventListener("click", evt => {
			const modeBtn = evt.target.closest("button[data-mode]");
			if(!modeBtn) return;
			const option = modeBtn.closest(".theme-option");
			if(!option) return;
			const style = option.dataset.style || "padrao";
			const mode = modeBtn.dataset.mode === "dark" ? "dark" : "light";
			applyThemeStyle(style);
			applyThemeMode(mode);
			closeMenu();
			themeButton.focus();
		});
		themeMenu.addEventListener("keydown", evt => {
			if(evt.key === "Escape"){
				evt.preventDefault();
				closeMenu();
				themeButton.focus();
			}
		});
		document.addEventListener("click", evt => {
			if(!themePicker.contains(evt.target)){
				closeMenu();
			}
		});
	}

	const chartContainers = [
		"temporal_chart",
		"temporal_total",
		"temporal_chart_c3",
		"temporal_total_c3"
	];
	chartContainers
		.map(id => document.getElementById(id))
		.filter(Boolean)
		.forEach(el => el.classList.add("chart-surface"));
	document.getElementById("loadDay").addEventListener("click", carregarDia);

	// Botão: Gráfico temporal (placeholder)
	const btnTemporal = document.getElementById("openTemporal");
	if(btnTemporal){
		btnTemporal.addEventListener("click", async () => {
			const dailySectionCards = document.getElementById('cards');
			const dailySectionLists = document.querySelector('section.lists');
			const temporalSection = document.getElementById('temporal_section');
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
				setPageTitle('Recebimento CAD UDI', '', 'Modo temporal');
				btnTemporal.textContent = 'Voltar ao painel';
				btnTemporal.dataset.icon = 'dashboardBadge';
				btnTemporal.dataset.iconTone = 'primary';
				injectIconBadges();
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
				btnTemporal.textContent = 'Gráfico temporal';
				btnTemporal.dataset.icon = 'timelineBadge';
				btnTemporal.dataset.iconTone = 'info';
				injectIconBadges();
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
			if(btnTemporal){
				btnTemporal.textContent = 'Gráfico temporal';
				btnTemporal.dataset.icon = 'timelineBadge';
				btnTemporal.dataset.iconTone = 'info';
			}
			if(!s || !e){
				alert('Informe o período (Entre ... e ...)');
				return;
			}
			injectIconBadges();
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

				const chartTheme = getChartThemeColors();
				const chartTextColor = chartTheme.text;
				const chartMutedColor = chartTheme.muted;
				const chartBorderColor = chartTheme.border;
				const chartGridColor = chartTheme.grid;
				const tooltipColors = chartTheme.tooltip;
				const seriesColors = chartTheme.series;
				const thresholdColors = chartTheme.thresholds;
				const tooltipBackground = tooltipColors.background;
				const tooltipBorder = tooltipColors.border;
				const tooltipTextColor = tooltipColors.text;
				const tooltipMutedColor = tooltipColors.muted;
				const tooltipAccentColor = tooltipColors.accent;
				const tooltipShadowColor = tooltipColors.shadow;
				const apexMode = (document.documentElement.getAttribute('data-mode') || 'light').toLowerCase() === 'dark' ? 'dark' : 'light';

				// Colorir colunas com thresholds baseado em porcentagem diária (produzidos/agendados)
				const colors = serieCol.map((v, i) => {
					const total = Math.max(0, Number(serieLine[i]) || 0);
					const pct = total > 0 ? Math.round((v/total)*100) : 0;
					if(pct <= 70) return thresholdColors.low;
					if(pct <= 90) return thresholdColors.medium;
					return thresholdColors.high;
				});

				const el = document.querySelector('#temporal_chart');
				if(!el){ return; }
				if(window.__apexTemporal){
					try{ window.__apexTemporal.destroy(); }catch{}
				}
				// Montar series, com colunas coloridas por ponto
				const colData = categories.map((x, i) => ({ x, y: serieCol[i], fillColor: colors[i] }));
				const lineData = categories.map((x, i) => ({ x, y: serieLine[i] }));
				const lineStrokeColor = seriesColors.linePrimary || tooltipAccentColor || '#3b82f6';
				const columnStrokeColor = seriesColors.columnPrimary || '#3b82f6';
				const markerStrokeColor = '#ffffff';
				const markerShadowColor = seriesColors.dropShadow || 'rgba(96,165,250,0.35)';
				const lineGlowColor = seriesColors.dropShadow || 'rgba(96,165,250,0.45)';
				const annotations = buildTemporalAnnotations(categories, serieLine, serieCol, {
					referenceLabel: 'Agendados',
					comparisonLabel: 'Produzidos',
					palette:{
						muted: chartMutedColor,
						accent: tooltipAccentColor,
						tooltipBg: tooltipBackground,
						tooltipMuted: tooltipMutedColor,
						tooltipText: tooltipTextColor,
						tooltipShadow: tooltipShadowColor,
						annotation: chartTheme.annotation,
						thresholds: thresholdColors,
						markerStroke: seriesColors.markerStroke
					}
				});

				// Usar mesmo range de eixo Y para as duas séries para comparação direta
				const allVals = [...serieLine, ...serieCol];
				let yMax = 0;
				for(const v of allVals){ yMax = Math.max(yMax, Number(v)||0); }
				if(!isFinite(yMax) || yMax <= 0){ yMax = 1; }

				const options = {
					chart:{
						type:'line', height: 360, stacked: false, toolbar:{show:true}, background: 'transparent', foreColor: chartTextColor,
						dropShadow:{ enabled:true, enabledOnSeries:[0], top:2, left:0, blur:10, color: lineGlowColor, opacity:0.9 }
					},
					theme:{ mode: apexMode, palette: 'palette10' },
					title:{ text: undefined },
					annotations,
					xaxis:{
						categories,
						labels:{ rotate: -25, style:{ colors: chartTextColor, fontSize: '12px' } },
						axisBorder:{ color: chartBorderColor },
						axisTicks:{ color: chartBorderColor }
					},
					yaxis:[
						{ seriesName:'Agendados', title:{text:'Agendados', style:{ color: chartMutedColor }}, labels:{ style:{ colors: chartTextColor }}, min:0, max: yMax },
						{ opposite:true, seriesName:'Produzidos', title:{text:'Produzidos', style:{ color: chartMutedColor }}, labels:{ style:{ colors: chartTextColor }}, min:0, max: yMax }
					],
					legend:{ position:'top', labels:{ colors: chartTextColor } },
					stroke:{ width:[3.8,0], curve:'smooth', lineCap:'round', dashArray:[7,0] },
					markers:{
						size:5,
						strokeWidth:2,
						colors:[lineStrokeColor],
						strokeColors: markerStrokeColor,
						fillOpacity:1,
						shape:'circle',
						hover:{ size:8, sizeOffset:2 },
						dropShadow:{ enabled:true, top:1, left:0, blur:6, color: markerShadowColor, opacity:0.42 }
					},
					grid:{ borderColor: chartGridColor, strokeDashArray:3 },
					plotOptions:{ bar:{ columnWidth:'55%', borderRadius: 8, borderRadiusApplication: 'end', borderRadiusWhenStacked: 'last' } },
					dataLabels:{ enabled:false },
					series:[
						{ name:'Agendados (SIRF)', type:'line', data: lineData },
						{ name:'Produzidos (WMS)', type:'column', data: colData }
					],
					colors: [lineStrokeColor, columnStrokeColor],
					fill:{ opacity:1 },
					states:{
						hover:{ filter:{ type:'lighten', value:0.15 } },
						active:{ allowMultipleDataPointsSelection:true, filter:{ type:'lighten', value:0.25 } }
					},
					distributed: true,
					tooltip:{
						shared:true,
						intersect:false,
						theme: apexMode,
						custom: function({series, seriesIndex, dataPointIndex, w}){
							const date = w.globals.categoryLabels[dataPointIndex] || '';
							const ag = (series[0] && series[0][dataPointIndex]) || 0;
							const pr = (series[1] && series[1][dataPointIndex]) || 0;
							const diff = pr - ag;
							const pct = ag > 0 ? Math.round((pr/ag)*100) : 0;
							const trendColor = diff >= 0 ? thresholdColors.highText : thresholdColors.lowText;
							const trendIcon = diff >= 0 ? TOOLTIP_ICONS.statUp : TOOLTIP_ICONS.statDown;
							const pctColor = pct<=70 ? thresholdColors.lowText : (pct<=90 ? thresholdColors.mediumText : thresholdColors.highText);
							const [y,m,d] = String(date).split('-');
							const dateFmt = (y && m && d) ? `${d}/${m}/${y}` : date;
							return `
								<div class="apx-tip" style="background:${tooltipBackground};border:1px solid ${tooltipBorder};color:${tooltipTextColor};padding:12px 14px;border-radius:12px;min-width:220px;box-shadow:0 18px 42px ${tooltipShadowColor};backdrop-filter:blur(8px)">
									<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;font-weight:600;color:${tooltipAccentColor}">
										<span style="width:20px;height:20px;display:inline-flex">${TOOLTIP_ICONS.calendar}</span>
										<span>${dateFmt}</span>
									</div>
									<div style="display:flex;flex-direction:column;gap:10px;font-size:13px">
										<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(37,99,235,0.08)">
											<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.factory}</span><span>Agendados (SIRF)</span></div>
											<span style="color:${tooltipAccentColor};font-weight:600">${ag}</span>
										</div>
										<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(52,211,153,0.08)">
											<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.warehouse}</span><span>Produzidos (WMS)</span></div>
											<span style="color:${pctColor};font-weight:600">${pr} (${pct}%)</span>
										</div>
										<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(148,163,184,0.12)">
											<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${trendIcon}</span><span>Diferença</span></div>
											<span style="color:${trendColor};font-weight:600">${diff >= 0 ? '+' : ''}${Intl.NumberFormat('pt-BR').format(diff)}</span>
										</div>
									</div>
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
					const totalColors = [seriesColors.totalGradientFrom, seriesColors.totalAltGradientFrom];
					const totalGradientTargets = [seriesColors.totalGradientTo, seriesColors.totalAltGradientTo];
					const optTotal = {
						chart:{ type:'bar', height:360, stacked:true, stackType:'100%', background:'transparent', foreColor: chartTextColor,
							animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } }
						},
						theme:{ mode: apexMode },
						title:{ text: undefined },
						xaxis:{ categories:['Total'], labels:{ style:{ colors: chartTextColor } }, axisBorder:{ color: chartBorderColor }, axisTicks:{ color: chartBorderColor } },
						yaxis:{ min:0, max:100, tickAmount:5, labels:{ style:{ colors: chartTextColor }, formatter:(v)=> `${Math.round(v)}%` } },
						plotOptions:{ bar:{ columnWidth:'60%', borderRadius:6, borderRadiusApplication:'end' } },
						dataLabels:{
							enabled:true,
							formatter:(val,opts)=>{
								const idx = opts.seriesIndex;
								const tot = totalSum;
								if(tot<=0) return '0%';
								const pctAg = Math.round((totalAg/tot)*100);
								const pctPr = 100 - pctAg;
								return `${idx===0 ? pctAg : pctPr}%`;
							},
							style:{ colors:[chartTextColor], fontSize:'12px', fontWeight:700 },
							dropShadow:{ enabled:true, top:1, left:0, blur:2 }
						},
						series:[
							{ name:'Agendados', data:[ totalAg ] },
							{ name:'Produzidos', data:[ totalPr ] }
						],
						colors: totalColors,
						fill:{ type:'gradient', gradient:{ shade:'dark', type:'vertical', shadeIntensity:0.25, gradientToColors: totalGradientTargets, inverseColors:false, opacityFrom:0.9, opacityTo:0.95, stops:[0,90,100] } },
						states:{ hover:{ filter:{ type:'darken', value:0.7 } }, active:{ allowMultipleDataPointsSelection:true } },
						legend:{ show:true, position:'top', labels:{ colors: chartTextColor } },
						grid:{ borderColor: chartGridColor, strokeDashArray:3 },
						tooltip:{
							theme: apexMode,
							custom: ({series, seriesIndex, dataPointIndex, w}) => {
								const ag = totalAg;
								const pr = totalPr;
								const tot = ag + pr;
								const pctAg = tot>0 ? Math.round((ag/tot)*100) : 0;
								const pctPr = 100 - pctAg;
								const diff = pr - ag;
								const diffColor = diff < 0 ? thresholdColors.lowText : (diff === 0 ? thresholdColors.mediumText : thresholdColors.highText);
								const cAg = totalColors[0];
								const cPr = totalColors[1];
								const trendIcon = diff >= 0 ? TOOLTIP_ICONS.statUp : TOOLTIP_ICONS.statDown;
								return `
									<div class="apx-tip" style="background:${tooltipBackground};border:1px solid ${tooltipBorder};color:${tooltipTextColor};padding:14px;border-radius:14px;min-width:240px;box-shadow:0 22px 48px ${tooltipShadowColor};backdrop-filter:blur(8px)">
										<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;font-weight:700;color:${tooltipAccentColor}">
											<span style="width:22px;height:22px;display:inline-flex">${TOOLTIP_ICONS.calendar}</span>
											<span>Total — Somatório do período</span>
										</div>
										<div style="display:flex;flex-direction:column;gap:10px;font-size:13px">
											<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(14,165,233,0.1)">
												<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.factory}</span><span>Agendados</span></div>
												<span style="color:${tooltipAccentColor};font-weight:600">${Intl.NumberFormat('pt-BR').format(ag)} (${pctAg}%)</span>
											</div>
											<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(59,130,246,0.1)">
												<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.warehouse}</span><span>Produzidos</span></div>
												<span style="color:${tooltipAccentColor};font-weight:600">${Intl.NumberFormat('pt-BR').format(pr)} (${pctPr}%)</span>
											</div>
											<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(148,163,184,0.12)">
												<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${trendIcon}</span><span>Diferença</span></div>
												<span style="color:${diffColor};font-weight:600">${diff >= 0 ? '+' : ''}${Intl.NumberFormat('pt-BR').format(diff)}</span>
											</div>
											<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(37,99,235,0.08)">
												<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.statUp}</span><span>Total Geral</span></div>
												<span style="font-weight:600">${Intl.NumberFormat('pt-BR').format(tot)}</span>
											</div>
										</div>
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
					const columnColorC3 = seriesColors.columnSecondary || seriesColors.columnPrimary || '#3b82f6';
					const lineColorC3 = seriesColors.lineSecondary || tooltipAccentColor || seriesColors.linePrimary || columnColorC3;
					const markerStrokeC3 = '#ffffff';
					const markerShadowC3 = seriesColors.dropShadow || 'rgba(96,165,250,0.4)';
					const lineGlowC3 = seriesColors.dropShadow || 'rgba(96,165,250,0.45)';
					const colDataC3 = categories.map((x,i)=>({x, y: serieCarr[i], fillColor: columnColorC3 }));
					const lineDataC3 = categories.map((x,i)=>({x, y: serieDesc[i]}));
					const annotationsC3 = buildTemporalAnnotations(categories, serieDesc, serieCarr, {
						referenceLabel: 'Descargas C3',
						comparisonLabel: 'Carregamentos C3',
						palette:{
							muted: chartMutedColor,
							accent: tooltipAccentColor,
							tooltipBg: tooltipBackground,
							tooltipMuted: tooltipMutedColor,
							tooltipText: tooltipTextColor,
							tooltipShadow: tooltipShadowColor,
							annotation: chartTheme.annotation,
							thresholds: thresholdColors,
							markerStroke: seriesColors.markerStroke
						}
					});
					const allValsC3 = [...serieDesc, ...serieCarr];
					let yMaxC3 = 0; for(const v of allValsC3){ yMaxC3 = Math.max(yMaxC3, Number(v)||0); }
					if(!isFinite(yMaxC3) || yMaxC3 <= 0){ yMaxC3 = 1; }
					const optionsC3 = {
						chart:{
							type:'line', height: 360, stacked:false, toolbar:{show:true}, background:'transparent', foreColor: chartTextColor,
							animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } },
							dropShadow:{ enabled:true, enabledOnSeries:[0], top:2, left:0, blur:10, color: lineGlowC3, opacity:0.9 }
						},
						theme:{ mode: apexMode, palette:'palette10' },
						title:{ text: undefined },
						annotations: annotationsC3,
						xaxis:{ categories, labels:{ rotate:-25, style:{ colors: chartTextColor, fontSize:'12px' } }, axisBorder:{ color: chartBorderColor }, axisTicks:{ color: chartBorderColor } },
						yaxis:[
							{ seriesName:'Descargas C3', title:{text:'Descargas C3', style:{ color: chartMutedColor }}, labels:{ style:{ colors: chartTextColor }, formatter: (val)=> Intl.NumberFormat('pt-BR').format(Math.round(val)) }, min:0, max:yMaxC3 },
							{ opposite:true, seriesName:'Carregamentos C3', title:{text:'Carregamentos C3', style:{ color: chartMutedColor }}, labels:{ style:{ colors: chartTextColor }, formatter: (val)=> Intl.NumberFormat('pt-BR').format(Math.round(val)) }, min:0, max:yMaxC3 }
						],
						legend:{ position:'top', labels:{ colors: chartTextColor } },
						stroke:{ width:[3.6,0], curve:'smooth', lineCap:'round', dashArray:[6,0] },
						markers:{
							size:5,
							strokeWidth:2,
							colors:[lineColorC3],
							strokeColors: markerStrokeC3,
							fillOpacity:1,
							shape:'circle',
							hover:{ size:8, sizeOffset:2 },
							dropShadow:{ enabled:true, top:1, left:0, blur:6, color: markerShadowC3, opacity:0.42 }
						},
						grid:{ borderColor: chartGridColor, strokeDashArray:3 },
						plotOptions:{ bar:{ columnWidth:'52%', borderRadius:8, borderRadiusApplication:'end', borderRadiusWhenStacked:'last' } }, dataLabels:{ enabled:false },
						series:[
							{ name:'Qtd Descarga C3', type:'line', data: lineDataC3 },
							{ name:'Qtd Carregamento C3', type:'column', data: colDataC3 }
						],
						colors:[lineColorC3, columnColorC3],
						fill:{ opacity:0.96 },
						states:{
							hover:{ filter:{ type:'lighten', value:0.15 } },
							active:{ allowMultipleDataPointsSelection:true, filter:{ type:'lighten', value:0.25 } }
						},
						distributed:false,
						tooltip:{
							shared:true, intersect:false, theme: apexMode,
							custom: function({series, dataPointIndex, w}){
								const date = w.globals.categoryLabels[dataPointIndex] || '';
								const de = (series[0] && series[0][dataPointIndex]) || 0;
								const ca = (series[1] && series[1][dataPointIndex]) || 0;
								const diff = ca - de;
								const pct = de > 0 ? Math.round((ca/de)*100) : 0;
								const pctColor = pct <= 70 ? thresholdColors.lowText : (pct <= 90 ? thresholdColors.mediumText : thresholdColors.highText);
								const trendColor = diff >= 0 ? thresholdColors.highText : thresholdColors.lowText;
								const trendIcon = diff >= 0 ? TOOLTIP_ICONS.statUp : TOOLTIP_ICONS.statDown;
								const [y,m,d] = String(date).split('-');
								const dateFmt = (y && m && d) ? `${d}/${m}/${y}` : date;
								return `
									<div class="apx-tip" style="background:${tooltipBackground};border:1px solid ${tooltipBorder};color:${tooltipTextColor};padding:12px 14px;border-radius:12px;min-width:220px;box-shadow:0 18px 42px ${tooltipShadowColor};backdrop-filter:blur(8px)">
										<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;font-weight:600;color:${tooltipAccentColor}">
											<span style="width:20px;height:20px;display:inline-flex">${TOOLTIP_ICONS.calendar}</span>
											<span>${dateFmt}</span>
										</div>
										<div style="display:flex;flex-direction:column;gap:10px;font-size:13px">
											<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(59,130,246,0.08)">
												<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.warehouse}</span><span>Qtd Descarga C3</span></div>
												<span style="color:${tooltipAccentColor};font-weight:600">${de}</span>
											</div>
											<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(234,88,12,0.09)">
												<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.truck}</span><span>Qtd Carregamento C3</span></div>
												<span style="color:${pctColor};font-weight:600">${ca} (${pct}%)</span>
											</div>
											<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px;border-radius:10px;background:rgba(148,163,184,0.12)">
												<div style="display:flex;align-items:center;gap:8px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${trendIcon}</span><span>Diferença</span></div>
												<span style="color:${trendColor};font-weight:600">${diff >= 0 ? '+' : ''}${Intl.NumberFormat('pt-BR').format(diff)}</span>
											</div>
										</div>
									</div>
								`;
							}
						}
					};
					// Gráfico Total (somatório do período) - Descargas vs Carregamentos C3
					try{ if(window.__apexTemporalTotalC3){ window.__apexTemporalTotalC3.destroy(); } }catch{}
					const totalDe = serieDesc.reduce((a,b)=>a+(Number(b)||0),0);
					const totalCa = serieCarr.reduce((a,b)=>a+(Number(b)||0),0);
					const elTotalC3 = document.querySelector('#temporal_total_c3');
					if(elTotalC3){
						const totalC3Colors = [seriesColors.totalGradientFrom, seriesColors.totalAltGradientFrom];
						const totalC3GradientTargets = [seriesColors.totalGradientTo, seriesColors.totalAltGradientTo];
						const optTotalC3 = {
							chart:{ type:'bar', height:360, stacked:true, stackType:'100%', background:'transparent', foreColor: chartTextColor,
								animations:{ enabled:true, easing:'easeinout', speed:600, animateGradually:{ enabled:true, delay:120 }, dynamicAnimation:{ enabled:true, speed:350 } }
							},
							theme:{ mode: apexMode },
							title:{ text: undefined },
							xaxis:{ categories:['Total'], labels:{ style:{ colors: chartTextColor } }, axisBorder:{ color: chartBorderColor }, axisTicks:{ color: chartBorderColor } },
							yaxis:{ min:0, max:100, tickAmount:5, labels:{ style:{ colors: chartTextColor }, formatter:(v)=> `${Math.round(v)}%` } },
							plotOptions:{ bar:{ columnWidth:'60%', borderRadius:6, borderRadiusApplication:'end' } },
							dataLabels:{
								enabled:true,
								formatter:(val,opts)=>{
									const idx = opts.seriesIndex;
									const tot = totalDe + totalCa;
									if(tot<=0) return '0%';
									const pctDe = Math.round((totalDe/tot)*100);
									const pctCa = 100 - pctDe;
									return `${idx===0 ? pctDe : pctCa}%`;
								},
								style:{ colors:[chartTextColor], fontSize:'12px', fontWeight:700 },
								dropShadow:{ enabled:true, top:1, left:0, blur:2 }
							},
							series:[
								{ name:'Descargas C3', data:[ totalDe ] },
								{ name:'Carregamentos C3', data:[ totalCa ] }
							],
							colors: totalC3Colors,
							fill:{ type:'gradient', gradient:{ shade:'dark', type:'vertical', shadeIntensity:0.25, gradientToColors: totalC3GradientTargets, inverseColors:false, opacityFrom:0.9, opacityTo:0.95, stops:[0,90,100] } },
							states:{ hover:{ filter:{ type:'darken', value:0.7 } }, active:{ allowMultipleDataPointsSelection:true } },
							legend:{ show:true, position:'top', labels:{ colors: chartTextColor } }, grid:{ borderColor: chartGridColor, strokeDashArray:3 },
							tooltip:{
								theme: apexMode,
								custom: ({series, seriesIndex, dataPointIndex, w}) => {
									const de = totalDe;
									const ca = totalCa;
									const tot = de + ca;
									const pctDe = tot>0 ? Math.round((de/tot)*100) : 0;
									const pctCa = 100 - pctDe;
									const cDe = totalC3Colors[0];
									const cCa = totalC3Colors[1];
									const diff = ca - de;
									const diffTextColor = diff < 0 ? thresholdColors.lowText : (diff === 0 ? thresholdColors.mediumText : thresholdColors.highText);
									const trendIcon = diff >= 0 ? TOOLTIP_ICONS.statUp : TOOLTIP_ICONS.statDown;
									return `
										<div class="apx-tip" style="background:${tooltipBackground};border:1px solid ${tooltipBorder};color:${tooltipTextColor};padding:14px;border-radius:14px;min-width:240px;box-shadow:0 22px 48px ${tooltipShadowColor};backdrop-filter:blur(8px)">
											<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;font-weight:700;color:${tooltipAccentColor}">
												<span style="width:22px;height:22px;display:inline-flex">${TOOLTIP_ICONS.calendar}</span>
												<span>Total — Somatório do período</span>
											</div>
											<div style="display:flex;flex-direction:column;gap:10px;font-size:13px">
												<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(59,130,246,0.1)">
													<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.warehouse}</span><span>Descargas C3</span></div>
													<span style="color:${tooltipAccentColor};font-weight:600">${Intl.NumberFormat('pt-BR').format(de)} (${pctDe}%)</span>
												</div>
												<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(234,88,12,0.1)">
													<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.truck}</span><span>Carregamentos C3</span></div>
													<span style="color:${tooltipAccentColor};font-weight:600">${Intl.NumberFormat('pt-BR').format(ca)} (${pctCa}%)</span>
												</div>
												<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(148,163,184,0.12)">
													<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${trendIcon}</span><span>Diferença</span></div>
													<span style="color:${diffTextColor};font-weight:600">${diff >= 0 ? '+' : ''}${Intl.NumberFormat('pt-BR').format(diff)}</span>
												</div>
												<div style="display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 12px;border-radius:12px;background:rgba(37,99,235,0.08)">
													<div style="display:flex;align-items:center;gap:10px;font-weight:600"><span style="width:18px;height:18px;display:inline-flex">${TOOLTIP_ICONS.statUp}</span><span>Total Geral</span></div>
													<span style="font-weight:600">${Intl.NumberFormat('pt-BR').format(tot)}</span>
												</div>
											</div>
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
				const cards = Array.from(document.querySelectorAll('#obs_list .obsCard'));
				if(cards.length){
					const blocks = cards.map(card => {
						const title = card.querySelector('.obsCard-title')?.textContent.trim();
						const listItems = Array.from(card.querySelectorAll('.obsCard-list li')).map(li => li.textContent.trim()).filter(Boolean);
						const text = card.querySelector('.obsCard-text')?.textContent.trim();
						const parts = [];
						if(title){ parts.push(`<h3>${title}</h3>`); }
						if(listItems.length){
							parts.push('<ul>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ul>');
						}else if(text){
							parts.push(`<p>${text}</p>`);
						}
						return parts.join("");
					});
					rte.innerHTML = blocks.join("");
				}else{
					const legacyItems = Array.from(document.querySelectorAll('#obs_list .obsItem')).map(x => `<p>${x.textContent.trim()}</p>`);
					rte.innerHTML = legacyItems.join("");
				}
			}
			editor.style.display = "block";
			window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
		} else { // fechar
			editor.style.display = "none";
		}
	});
	
	save.addEventListener("click", () => {
		const date = document.getElementById("datePick").value;
		const html = rte.innerHTML.trim();
		const sanitized = html.replace(/<script.*?>.*?<\/script>/gi, "");
		const textProbe = sanitized.replace(/<[^>]*>/g, " ").replace(/&nbsp;/gi, " ").trim();
		const hasContent = textProbe.length > 0;
		if(hasContent){
			OBS_VISUAL.set(date, sanitized);
			renderObsVisual(sanitized);
		}else{
			OBS_VISUAL.delete(date);
			const fallback = (LAST_DAILY_DATA && LAST_DAILY_DATA.observacoes) || [];
			renderObs(fallback);
		}
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
		switch(cmd){
			case 'formatBlock':
				document.execCommand('formatBlock', false, val || 'P');
				break;
			case 'createLink':{
				const current = window.getSelection()?.toString() || '';
				const url = prompt('Informe o endereço (https://...)', current.startsWith('http') ? current : 'https://');
				if(url){
					document.execCommand('createLink', false, url.trim());
				}
				break;
			}
			case 'removeFormat':
				document.execCommand('removeFormat', false, null);
				document.execCommand('unlink', false, null);
				break;
			case 'insertHorizontalRule':
			case 'strikeThrough':
			case 'justifyFull':
			case 'justifyLeft':
			case 'justifyCenter':
			case 'justifyRight':
			case 'insertOrderedList':
			case 'insertUnorderedList':
			case 'indent':
			case 'outdent':
			case 'superscript':
			case 'subscript':
			case 'undo':
			case 'redo':
			case 'bold':
			case 'italic':
			case 'underline':
				document.execCommand(cmd, false, null);
				break;
			default:
				document.execCommand(cmd, false, val);
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

