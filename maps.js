/* UrbanPulse AI — Tamil Nadu City Map Engine v3.0 */

const TN = {
  center: [11.1271, 78.6569], // Tamil Nadu center
  zoom: 7,
  cities: {
    Chennai:     { coords: [13.0827, 80.2707], zoom: 12, pop: '10.9M', zone: 'Metropolitan' },
    Coimbatore:  { coords: [11.0168, 76.9558], zoom: 12, pop: '2.1M',  zone: 'Western Zone' },
    Madurai:     { coords: [9.9252,  78.1198], zoom: 12, pop: '1.5M',  zone: 'Southern Zone' },
    Salem:       { coords: [11.6643, 78.1460], zoom: 12, pop: '0.9M',  zone: 'Central Zone' },
    Trichy:      { coords: [10.7905, 78.7047], zoom: 12, pop: '1.0M',  zone: 'Central Zone' },
    Vellore:     { coords: [12.9165, 79.1325], zoom: 12, pop: '0.6M',  zone: 'Northern Zone' },
    Thanjavur:   { coords: [10.7870, 79.1378], zoom: 12, pop: '0.5M',  zone: 'Delta Zone' },
    Tirunelveli: { coords: [8.7139,  77.7567], zoom: 12, pop: '0.7M',  zone: 'Southern Zone' },
  },
};

/* ─── CARTO Dark Tile ─── */
const TILE = {
  url: 'https://{s}.basemaps.cartocdn.com/dark_matter_nolabels/{z}/{x}/{y}{r}.png',
  labels: 'https://{s}.basemaps.cartocdn.com/dark_matter_only_labels/{z}/{x}/{y}{r}.png',
  attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
};

const RISK_PALETTE = {
  Critical: { fill: '#e11d48', border: '#fb7185', glow: 'rgba(225,29,72,0.5)'  },
  High:     { fill: '#d97706', border: '#fbbf24', glow: 'rgba(217,119,6,0.4)'  },
  Medium:   { fill: '#2563eb', border: '#60a5fa', glow: 'rgba(37,99,235,0.35)' },
  Low:      { fill: '#059669', border: '#34d399', glow: 'rgba(5,150,105,0.3)'  },
  Minimal:  { fill: '#334155', border: '#64748b', glow: 'rgba(51,65,85,0.2)'   },
};

/* ─── TN Infrastructure Assets ─── */
const TN_ASSETS = [
  // Chennai
  { name: 'Chennai Metro Phase II — Corridor 3',  city: 'Chennai',     type: 'Metro',      coords: [13.0850, 80.2750], risk: 'High',     pct: 72, icon: '🚇', note: 'Elevated section stress detected' },
  { name: 'CMWSSB Water Main — T.Nagar',          city: 'Chennai',     type: 'Pipeline',   coords: [13.0350, 80.2300], risk: 'Critical',  pct: 88, icon: '💧', note: 'Post-Cyclone Michaung pipe rupture risk' },
  { name: 'Cooum River Floodgate — Ambattur',     city: 'Chennai',     type: 'Drainage',   coords: [13.1100, 80.1600], risk: 'Critical',  pct: 91, icon: '🌊', note: 'Monsoon overflow predicted — 1.4m above safe' },
  { name: 'Anna Salai Street Lighting Grid',      city: 'Chennai',     type: 'Power',      coords: [13.0600, 80.2500], risk: 'Medium',    pct: 45, icon: '💡', note: '14 fixtures flagged for replacement' },
  { name: 'Kathipara Grade Separator',            city: 'Chennai',     type: 'Bridge',     coords: [13.0150, 80.2050], risk: 'Low',       pct: 28, icon: '🌉', note: 'Routine inspection scheduled Q4' },
  { name: 'Marina Beach Coastal Road',            city: 'Chennai',     type: 'Road',       coords: [13.0560, 80.2780], risk: 'Medium',    pct: 52, icon: '🛣️', note: 'Salt erosion affecting retaining walls' },
  // Coimbatore
  { name: 'Pillur Reservoir Dam',                 city: 'Coimbatore',  type: 'Dam',        coords: [11.0900, 76.7200], risk: 'High',      pct: 68, icon: '🏗️', note: 'Below capacity — water scarcity alert' },
  { name: 'TNEB Substation — Saravanampatti',     city: 'Coimbatore',  type: 'Power',      coords: [11.0700, 76.9900], risk: 'Medium',    pct: 41, icon: '⚡', note: 'Grid overload during summer peak' },
  { name: 'Avinashi Road Flyover',                city: 'Coimbatore',  type: 'Bridge',     coords: [11.0200, 77.0100], risk: 'Low',       pct: 22, icon: '🌉', note: 'Good condition — 18 months post-maintenance' },
  { name: 'Coimbatore Smart City ATMS',           city: 'Coimbatore',  type: 'Traffic',    coords: [11.0168, 76.9558], risk: 'Low',       pct: 15, icon: '🚦', note: 'AI traffic control operational' },
  // Madurai
  { name: 'Vaigai River Bund — Madurai Central',  city: 'Madurai',     type: 'Drainage',   coords: [9.9252,  78.1198], risk: 'High',      pct: 74, icon: '🌊', note: 'Bund reinforcement overdue by 2 years' },
  { name: 'Madurai Bypass NH-85 Expansion',       city: 'Madurai',     type: 'Road',       coords: [9.9100,  78.1400], risk: 'Medium',    pct: 38, icon: '🛣️', note: 'Subbase settlement in 3 segments' },
  // Salem
  { name: 'Salem Steel Flyover — Ring Road',      city: 'Salem',       type: 'Bridge',     coords: [11.6643, 78.1460], risk: 'High',      pct: 66, icon: '🌉', note: 'Fatigue cracking on central span joints' },
  // Trichy
  { name: 'Cauvery Water Treatment Plant',        city: 'Trichy',      type: 'Pipeline',   coords: [10.7905, 78.7047], risk: 'Medium',    pct: 44, icon: '💧', note: 'Filter bank capacity at 78%' },
  // Vellore
  { name: 'Palar River Embankment',               city: 'Vellore',     type: 'Drainage',   coords: [12.9165, 79.1325], risk: 'Low',       pct: 25, icon: '🌊', note: 'Stable. Next inspection Dec 2026' },
];

/* ─── TN Flood Risk Zones (post-Cyclone Michaung) ─── */
const FLOOD_ZONES = [
  { coords: [13.1100, 80.2600], radius: 3500, name: 'Ambattur Industrial Estate', severity: 'Severe',   color: '#e11d48' },
  { coords: [13.0700, 80.2800], radius: 2200, name: 'Perambur — Kolathur',        severity: 'High',     color: '#d97706' },
  { coords: [13.0300, 80.2700], radius: 1800, name: 'Adyar Riverbed Zone',        severity: 'High',     color: '#d97706' },
  { coords: [13.0900, 80.2900], radius: 1400, name: 'Tondiarpet Coastal',         severity: 'Moderate', color: '#2563eb' },
];

/* ─── Initialize a UrbanPulse map ─── */
function initUrbanPulseMap(containerId, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return null;

  const city = opts.city && TN.cities[opts.city] ? TN.cities[opts.city] : null;

  const map = L.map(containerId, {
    center: city ? city.coords : (opts.center || [13.0827, 80.2707]),
    zoom:   city ? city.zoom  : (opts.zoom   || 12),
    zoomControl: false,
    attributionControl: true,
  });

  L.tileLayer(TILE.url, { attribution: TILE.attribution, maxZoom: 20 }).addTo(map);
  L.tileLayer(TILE.labels, { attribution: '', maxZoom: 20, opacity: 0.7 }).addTo(map);
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  return map;
}

/* ─── Add full TN city layers ─── */
function addCityMapLayers(map, options = {}) {
  if (!map) return;

  /* City hub markers */
  Object.entries(TN.cities).forEach(([name, city]) => {
    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:12px;height:12px;
        border-radius:50%;
        background:#00d4ff;
        border:2px solid rgba(0,212,255,0.5);
        box-shadow:0 0 16px rgba(0,212,255,0.8),0 0 4px #00d4ff;
        animation:none;
      " title="${name}"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });
    L.marker(city.coords, { icon })
      .addTo(map)
      .bindTooltip(`<strong style="color:#00d4ff">${name}</strong><br>
        <span style="color:#7ba4c7;font-size:11px;">${city.zone} · Pop. ${city.pop}</span>`, {
        direction: 'top', opacity: 1,
        className: 'up-tooltip',
      });
  });

  /* Flood zones */
  if (!options.hideFlood) {
    FLOOD_ZONES.forEach(z => {
      L.circle(z.coords, {
        radius: z.radius,
        color: z.color,
        fillColor: z.color,
        fillOpacity: 0.10,
        weight: 1.5,
        opacity: 0.5,
        dashArray: '5,4',
      }).addTo(map).bindTooltip(`
        <strong style="color:${z.color}">${z.name}</strong><br>
        <span style="color:#7ba4c7;font-size:11px;">Flood Risk: ${z.severity}</span>
      `, { direction: 'top', opacity: 1 });
    });
  }

  /* Asset markers */
  TN_ASSETS.forEach(a => {
    const pal  = RISK_PALETTE[a.risk] || RISK_PALETTE.Medium;
    const size = a.risk === 'Critical' ? 32 : a.risk === 'High' ? 28 : 24;
    const pulse = (a.risk === 'Critical' || a.risk === 'High')
      ? `animation:none;box-shadow:0 0 0 3px ${pal.glow},0 0 20px ${pal.glow};`
      : `box-shadow:0 0 12px ${pal.glow};`;

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:${size}px;height:${size}px;
        border-radius:50%;
        background:${pal.fill}22;
        border:2px solid ${pal.border};
        display:flex;align-items:center;justify-content:center;
        font-size:${size === 32 ? 16 : 13}px;
        ${pulse}
        cursor:pointer;
        transition:transform 0.2s;
      ">${a.icon}</div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });

    L.marker(a.coords, { icon })
      .addTo(map)
      .bindPopup(`
        <div style="font-family:Inter,sans-serif;min-width:220px;padding:4px;">
          <div style="font-weight:800;font-size:0.92rem;margin-bottom:4px;color:#e8f4ff;">${a.name}</div>
          <div style="font-size:0.76rem;color:#7ba4c7;margin-bottom:8px;">${a.city} · ${a.type}</div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="
              font-size:0.68rem;font-weight:700;text-transform:uppercase;
              padding:3px 8px;border-radius:999px;letter-spacing:0.5px;
              background:${pal.fill}22;color:${pal.border};border:1px solid ${pal.border}44;
            ">${a.risk}</span>
            <span style="font-family:monospace;font-weight:900;color:${pal.fill};font-size:1rem;">${a.pct}%</span>
          </div>
          <div style="height:5px;background:#0a1628;border-radius:4px;overflow:hidden;margin-bottom:8px;">
            <div style="height:100%;width:${a.pct}%;background:linear-gradient(90deg,${pal.fill},${pal.border});border-radius:4px;"></div>
          </div>
          <div style="font-size:0.76rem;color:#7ba4c7;font-style:italic;">${a.note}</div>
        </div>
      `, { maxWidth: 280 });
  });
}

/* ─── Add complaint pins ─── */
function addComplaintLayer(map, complaints) {
  if (!complaints || !map) return;
  complaints.forEach(c => {
    if (!c.lat || !c.lng) return;
    const pal = RISK_PALETTE[c.priority] || RISK_PALETTE.Medium;
    L.circleMarker([c.lat, c.lng], {
      radius: 7,
      fillColor: pal.fill,
      color: pal.border,
      fillOpacity: 0.8,
      weight: 1.5,
    }).addTo(map).bindPopup(`<strong>${c.title}</strong><br><small>${c.priority} · ${c.status}</small>`);
  });
}
