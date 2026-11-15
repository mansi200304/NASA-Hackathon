import { normalizeSeries, normalizeRate, normalizeHotspots, validateGeoJSON, safeSourceURL, formatNumber, isNumber } from './model.mjs';

const $ = selector => document.querySelector(selector);
const DATA = new URL('../data/processed/', import.meta.url);
const COLORS = { rust: '#A64B2A', ink: '#2D2A25', olive: '#52664B', sand: '#E4D9C9' };
const state = { selected: null, slugs: [], series: new Map(), rates: new Map(), layers: new Map(), outlines: new Map(), base: 'satellite' };
let map, outlineGroup;
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
};
function note(text) { return el('p', 'metric-note', text); }
function setStatus(text) { $('#data-status').textContent = text; }
function dataError(result, fallback) {
  if (result?.status === 'invalid') return 'File needs review: ' + result.error;
  if (result?.status === 'error') return 'Could not load the source file. Refresh to retry.';
  return fallback;
}
async function loadJSON(name, normalize = value => value) {
  if (window.ATLAS_PREVIEW_DATA) {
    if (!(name in window.ATLAS_PREVIEW_DATA)) return { status: 'missing' };
    try { return { status: 'ready', value: normalize(window.ATLAS_PREVIEW_DATA[name]) }; }
    catch (error) { return { status: 'invalid', error: error.message }; }
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(new URL(name, DATA), { signal: controller.signal, cache: 'no-cache' });
    if (response.status === 404) return { status: 'missing' };
    if (!response.ok) throw new Error('HTTP ' + response.status);
    let raw;
    try { raw = await response.json(); } catch { return { status: 'invalid', error: 'Invalid JSON.' }; }
    try { return { status: 'ready', value: normalize(raw) }; }
    catch (error) { return { status: 'invalid', error: error.message }; }
  } catch (error) { return { status: 'error', error: error.message }; }
  finally { clearTimeout(timeout); }
}
function factList(items) {
  const list = el('dl', 'detail-facts');
  items.forEach(([label, value]) => {
    const row = el('div');
    row.append(el('dt', '', label), el('dd', '', value));
    list.append(row);
  });
  return list;
}
function section(title) {
  const node = el('section', 'detail-section');
  node.append(el('h2', '', title));
  return node;
}
function svgNode(tag, attrs = {}, text) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
  if (text != null) node.textContent = text;
  return node;
}
function makeChart(series) {
  const wrap = el('div', 'chart');
  const svg = svgNode('svg', { viewBox: '0 0 300 170', role: 'img', 'aria-label': 'Cumulative displacement in centimetres relative to ' + series.reference });
  const valid = series.points.filter(p => isNumber(p.value));
  const start = Date.parse(series.dates[0]), end = Date.parse(series.dates.at(-1));
  let lo = Math.min(...valid.map(p => p.value)), hi = Math.max(...valid.map(p => p.value));
  const pad = Math.max((hi - lo) * 0.15, 0.1);
  lo -= pad; hi += pad;
  const x = date => 42 + (Date.parse(date) - start) / (end - start || 1) * 244;
  const y = value => 130 - (value - lo) / (hi - lo) * 112;
  [lo, (lo + hi) / 2, hi].forEach(value => {
    svg.append(svgNode('line', { x1: 42, x2: 286, y1: y(value), y2: y(value), stroke: '#C9C0B2', 'stroke-width': 0.7 }));
    svg.append(svgNode('text', { x: 35, y: y(value) + 3, 'text-anchor': 'end', class: 'chart-label' }, formatNumber(value)));
  });
  svg.append(svgNode('text', { x: 8, y: 12, class: 'chart-label' }, 'cm'));
  let path = '', next = true;
  series.points.forEach(p => {
    if (p.value === null) { next = true; return; }
    path += (next ? 'M' : 'L') + x(p.date) + ',' + y(p.value) + ' ';
    next = false;
  });
  svg.append(svgNode('path', { d: path, fill: 'none', stroke: COLORS.rust, 'stroke-width': 1.8 }));
  valid.forEach(p => svg.append(svgNode('circle', { cx: x(p.date), cy: y(p.value), r: 2.5, fill: COLORS.rust })));
  svg.append(svgNode('text', { x: 42, y: 153, class: 'chart-label' }, series.dates[0]));
  if (series.dates.length > 1) svg.append(svgNode('text', { x: 286, y: 168, 'text-anchor': 'end', class: 'chart-label' }, series.dates.at(-1)));
  wrap.append(svg);
  const details = el('details');
  details.append(el('summary', '', 'View observations as a table'));
  const table = el('table'), head = el('thead'), header = el('tr'), body = el('tbody');
  header.append(el('th', '', 'Date'), el('th', '', 'Displacement (cm)'));
  head.append(header);
  series.points.forEach(p => { const tr = el('tr'); tr.append(el('td', '', p.date), el('td', '', p.value === null ? 'No observation' : formatNumber(p.value))); body.append(tr); });
  table.append(head, body); details.append(table); wrap.append(details);
  return wrap;
}
function renderDetails() {
  const feature = state.hotspots.features.find(f => f.properties.slug === state.selected);
  const p = feature.properties;
  const result = state.series.get(state.selected);
  const series = result?.status === 'ready' ? result.value : null;
  const rateResult = state.rates.get(state.selected);
  const meta = rateResult?.status === 'ready' ? rateResult.value : null;
  const root = $('#detail-content');
  root.replaceChildren();
  const kicker = el('div', 'detail-kicker');
  kicker.append(el('span', '', (p.county || 'Arizona') + ', Arizona'), el('span', '', 'Study ' + String(state.slugs.indexOf(state.selected) + 1).padStart(2, '0')));
  root.append(kicker, el('h1', '', p.name), el('p', 'story-name', p.tagline));
  const hasRate = series && isNumber(series.rate_cm_yr);
  const metric = el('section', 'metric' + (hasRate ? '' : ' pending'));
  metric.append(el('p', 'metric-label', 'Reported displacement rate'));
  const value = el('div', 'metric-value', hasRate ? formatNumber(series.rate_cm_yr) : 'Measurement pending');
  if (hasRate) value.append(el('small', '', (isNumber(series.rate_sigma) ? '± ' + formatNumber(series.rate_sigma) + ' ' : '') + 'cm/yr'));
  metric.append(value);
  metric.append(note(hasRate
    ? (isNumber(series.rate_sigma) ? 'Uncertainty supplied by the processing pipeline.' : 'Uncertainty has not been supplied.')
    : dataError(result, 'Awaiting a referenced time series and fitted rate.')));
  if (hasRate) metric.append(note(series.sign_convention || 'Sign convention not supplied. This value is not labelled as vertical sinking.'));
  root.append(metric);
  const chartSection = section('Displacement through time');
  if (series?.hasData) {
    chartSection.append(makeChart(series), note('Relative to: ' + series.reference));
  } else {
    const wait = el('div', 'chart-wait');
    wait.append(el('span', 'waiting-mark'), el('p', '', 'No observations to plot yet'), el('small', '', dataError(result, 'The chart will use the measured record. Pending does not mean zero movement.')));
    chartSection.append(wait);
  }
  root.append(chartSection);
  const record = section('Measurement record');
  record.append(factList([
    ['Satellite / product', series?.source || meta?.track || 'Not supplied'],
    ['Track / frame', series?.track || meta?.track || 'Coverage check pending'],
    ['Record', series?.dates.length ? series.dates[0] + ' — ' + series.dates.at(-1) : 'Pending'],
    ['Reference', series?.reference || 'Stable reference pending'],
    ['Data release', series?.data_release || meta?.data_release || 'Not supplied']
  ]));
  root.append(record);
  const validation = section('ADWR comparison');
  if (series && isNumber(series.adwr_rate_cm_yr)) {
    validation.append(el('p', 'detail-copy', 'ADWR contextual rate: ' + formatNumber(series.adwr_rate_cm_yr) + ' cm/yr.'));
    validation.append(el('p', 'validation-note', 'A validation difference is not calculated until period, footprint, direction and reference are comparable.'));
  } else {
    validation.append(el('p', 'detail-copy', 'Comparison pending'));
    validation.append(el('p', 'validation-note', 'Match the area and observation period before comparing rates.'));
  }
  root.append(validation);
  const story = section('Why this place');
  story.append(el('p', 'detail-copy', p.story));
  root.append(story);
  const bottom = el('div', 'detail-bottom');
  bottom.append(el('div', '', 'Radar measures motion along the satellite’s line of sight. A vertical rate requires a justified conversion.'));
  const button = el('button', '', 'Read the measurement limits');
  button.type = 'button'; button.addEventListener('click', () => openDialog('limits'));
  bottom.append(button); root.append(bottom);
}
function renderHotspots() {
  const list = $('#hotspot-list'); list.replaceChildren();
  state.hotspots.features.forEach((f, i) => {
    const button = el('button', 'hotspot-button');
    button.type = 'button';
    button.dataset.slug = f.properties.slug;
    button.setAttribute('aria-pressed', String(f.properties.slug === state.selected));
    button.append(el('span', 'index', String(i + 1).padStart(2, '0')));
    const title = el('span', 'place', f.properties.name);
    title.append(el('span', 'tagline', f.properties.tagline));
    button.append(title);
    button.addEventListener('click', () => selectHotspot(f.properties.slug));
    list.append(button);
  });
}
function selectHotspot(slug, fit = true) {
  state.selected = slug;
  document.querySelectorAll('.hotspot-button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.slug === slug)));
  state.outlines.forEach((layer, key) => layer.setStyle({ color: key === slug ? '#F4EFE6' : '#9CA5A9', weight: key === slug ? 1.8 : 1, fillOpacity: 0, dashArray: key === slug ? null : '5 5' }));
  $('#map-location').textContent = state.hotspots.features.find(f => f.properties.slug === slug).properties.name;
  renderDetails(); updateRateLayer();
  if (fit && map) fitSelected();
}
function fitSelected() {
  const layer = state.outlines.get(state.selected);
  if (map && layer) {
    map.stop();
    map.fitBounds(layer.getBounds(), { padding: [50, 75], animate: false, maxZoom: 11 });
  }
}
function showAll() { if (map && outlineGroup) { map.stop(); map.fitBounds(outlineGroup.getBounds(), { padding: [45, 65], animate: false, maxZoom: 9 }); } }
function initMap() {
  if (!window.L) {
    $('#map-error').textContent = 'The map library could not load. Study details remain available.';
    $('#map-error').hidden = false; return;
  }
  map = L.map('map', { zoomControl: false, minZoom: 5, maxZoom: 18, zoomSnap: 0.25, attributionControl: true }).setView([32.8, -111.65], 9);
  map.createPane('measurements'); map.getPane('measurements').style.zIndex = 330;
  L.control.zoom({ position: 'topright' }).addTo(map);
  L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(map);
  const tileSources = {
    dark: { url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', attribution: 'Tiles &copy; Esri, HERE, Garmin, OpenStreetMap contributors', maxNativeZoom: 16 },
    terrain: { url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', attribution: 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin, USGS, NGA, EPA, USDA, NPS' },
    satellite: { url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community' }
  };
  state.basemaps = {};
  Object.entries(tileSources).forEach(([key, config]) => {
    const layer = L.tileLayer(config.url, { attribution: config.attribution, maxNativeZoom: config.maxNativeZoom || 18, maxZoom: 18 });
    let errors = 0;
    layer.on('tileerror', () => { if (state.base === key && ++errors >= 3) $('#map-error').hidden = false; });
    layer.on('tileload', () => { if (state.base === key) { errors = 0; $('#map-error').hidden = true; } });
    state.basemaps[key] = layer;
  });
  state.basemaps[state.base].addTo(map);
  outlineGroup = L.featureGroup().addTo(map);
  state.hotspots.features.forEach(f => {
    const layer = L.geoJSON(f, { bubblingMouseEvents: false, style: { color: '#9CA5A9', weight: 1, fillOpacity: 0 } });
    const tooltip = el('div', '', f.properties.name);
    if (f.properties.confirmation) tooltip.append(el('small', '', f.properties.confirmation));
    layer.bindTooltip(tooltip, { sticky: true, className: 'study-label' });
    layer.on('click', () => selectHotspot(f.properties.slug));
    layer.addTo(outlineGroup); state.outlines.set(f.properties.slug, layer);
  });
  map.on('click', event => {
    // A PNG contains colours, not numeric pixels. Do not invent a pixel sampler.
    const node = el('div');
    node.append(el('strong', '', event.latlng.lat.toFixed(4) + ', ' + event.latlng.lng.toFixed(4)), el('p', '', 'Pixel measurements are unavailable in this first preview. Select a study area for its published record.'));
    L.popup().setLatLng(event.latlng).setContent(node).openOn(map);
  });
  new ResizeObserver(() => map.invalidateSize({ pan: false })).observe($('#map'));
}
function renderLayerControls() {
  const list = $('#layer-list'); list.replaceChildren();
  state.layers.forEach((config, key) => {
    const ready = config.status === 'ready';
    const row = el('div', 'layer-row' + (ready ? '' : ' unavailable'));
    const label = el('label');
    const input = el('input');
    input.type = 'checkbox'; input.checked = ready && config.visible; input.disabled = !ready;
    input.id = 'layer-' + key;
    const statusLabel = ready ? '' : config.status === 'missing' || config.status === 'loading' ? 'Pending' : 'Review file';
    label.append(input, el('span', 'layer-title', config.name), el('span', 'layer-state', statusLabel));
    if (config.error) label.title = config.error;
    row.append(label);
    input.addEventListener('change', () => {
      config.visible = input.checked;
      if (key === 'rate') updateRateLayer();
      else if (map && config.layer) { if (input.checked) config.layer.addTo(map); else map.removeLayer(config.layer); }
    });
    if (ready && key !== 'hotspots') {
      const opacityWrap = el('div', 'opacity-control'), opacity = el('input');
      opacity.type = 'range'; opacity.min = 0; opacity.max = 100; opacity.value = config.opacity * 100;
      opacity.setAttribute('aria-label', config.name + ' opacity');
      opacity.addEventListener('input', () => {
        config.opacity = Number(opacity.value) / 100;
        if (key === 'rate') state.rateImage?.setOpacity(config.opacity);
        else config.layer?.setStyle({ opacity: config.opacity, fillOpacity: config.opacity * 0.15 });
      });
      opacityWrap.append(el('span', '', 'Opacity'), opacity); row.append(opacityWrap);
    }
    list.append(row);
  });
}
function updateRateLayer() {
  if (map && state.rateImage) map.removeLayer(state.rateImage);
  state.rateImage = null;
  const result = state.rates.get(state.selected), config = state.layers.get('rate');
  config.status = result?.status || 'missing'; config.error = result?.error;
  const legend = $('#rate-legend'); legend.hidden = true; legend.replaceChildren();
  if (result?.status === 'ready' && config.visible && map) {
    const meta = result.value;
    const slug = state.selected;
    const imageName = 'rate_' + slug + '.png';
    const imageURL = window.ATLAS_PREVIEW_IMAGES?.[imageName] || new URL(imageName, DATA).href;
    const image = L.imageOverlay(imageURL, meta.bounds, { pane: 'measurements', opacity: config.opacity, interactive: false });
    state.rateImage = image;
    image.on('error', () => {
      if (state.rateImage !== image) return;
      map.removeLayer(image); legend.hidden = true;
      config.status = 'invalid'; config.error = 'Rate metadata exists, but the PNG did not load.';
      renderLayerControls();
    });
    image.on('load', () => {
      if (state.rateImage !== image) return;
      legend.hidden = false;
      legend.append(el('strong', '', 'Ground motion · line of sight'));
      legend.append(el('div', '', formatNumber(meta.vmin) + ' to ' + formatNumber(meta.vmax) + ' cm/yr'));
      if (Array.isArray(meta.colors) && meta.colors.length >= 2 && meta.colors.every(c => /^#[0-9a-f]{6}$/i.test(c))) {
        const strip = el('div', 'legend-colors'); strip.style.background = 'linear-gradient(to right,' + meta.colors.join(',') + ')'; legend.append(strip);
      }
      // The team's documented custom ramp is not a linear colour scale. Describe
      // it categorically rather than manufacture a numeric gradient from it.
      if (typeof meta.colormap === 'string' && meta.colormap.startsWith('custom: red = sinking')) {
        const key = el('div', 'map-color-key');
        for (const [cls, text] of [['sinking', 'Red: sinking'], ['stable', 'Transparent: stable'], ['rising', 'Blue: rising']]) {
          const item = el('span', '', text); item.prepend(el('i', cls)); key.append(item);
        }
        legend.append(key);
      }
      legend.append(el('small', '', meta.track || 'Track not supplied'));
      legend.append(el('small', '', meta.dates[0] + ' — ' + meta.dates.at(-1)));
      if (meta.sign_convention) legend.append(el('small', '', meta.sign_convention));
      legend.append(el('small', '', meta.data_release || 'Release status not supplied'));
    });
    image.addTo(map);
  }
  renderLayerControls();
}
function makeOverlay(raw, key) {
  const color = key === 'habitat' ? COLORS.olive : key === 'datacenters' ? COLORS.ink : COLORS.rust;
  return L.geoJSON(raw, {
    bubblingMouseEvents: false,
    style: { color, weight: 1.3, fillOpacity: 0.12, opacity: 0.8 },
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 5, color, weight: 1.5, fillColor: color, fillOpacity: feature.properties?.status === 'planned' ? 0 : 0.8 }),
    onEachFeature: (feature, layer) => {
      const p = feature.properties || {};
      const popup = el('div');
      popup.append(el('strong', '', p.name || p.NAME || 'Context feature'));
      if (key === 'datacenters') {
        popup.append(el('p', '', 'Compiled public-source location. Status: ' + (p.status || 'unknown')));
        popup.append(el('p', '', 'Water use: ' + (p.water_use ?? 'Not published')));
      }
      const source = safeSourceURL(p.source_url);
      if (source) { const a = el('a', '', 'Source'); a.href = source; a.target = '_blank'; a.rel = 'noopener noreferrer'; popup.append(a); }
      layer.bindPopup(popup);
    }
  });
}
const dialogCopy = {
  method: {
    title: 'How we measure ground motion',
    body: '<p>Satellite radar observes the distance between a satellite and the ground. Comparing repeated passes can reveal motion along that viewing direction.</p><ol><li>Check valid pixels, coherence and the correction layers in each NISAR product.</li><li>Convert corrected phase to distance using the product wavelength and verified sign convention.</li><li>Reference each observation to a stable area, then build a connected time series on one track.</li><li>Fit a rate, estimate uncertainty and compare with ADWR observations over a comparable area and period.</li></ol><p>This first interface reads exported results. It does not calculate a rate from a coloured image. Tracks, dates and release status are displayed only when supplied with the result.</p>'
  },
  limits: {
    title: 'Read the map with its limits',
    body: '<ul><li><strong>Pending is not zero.</strong> Empty results mean that a file is missing or has not passed the interface checks.</li><li><strong>Radar measures line-of-sight motion.</strong> A vertical sinking rate needs a justified conversion. A positive or negative value is not interpreted without its sign convention.</li><li><strong>Short records need care.</strong> Seasonal movement, atmospheric errors and the stable reference can influence a fitted rate.</li><li><strong>Data quality varies.</strong> Farming and construction can reduce coherence. Product corrections and release status must be checked.</li><li><strong>Location does not establish cause.</strong> A nearby farm, city or data center does not prove responsibility for ground movement.</li><li><strong>Habitat is a separate layer.</strong> Radar does not observe wildlife.</li><li><strong>A study box is not a sinking zone.</strong> Outlines show the areas the team chose to investigate.</li></ul>'
  },
  sources: {
    title: 'Data, context & code',
    body: '<p>Study extents are defined by the project. Context layers are shown only when their source files are available; missing layers are not replaced with invented features.</p><ul><li><a href=\"https://github.com/mansi200304/NASA-Hackathon\" target=\"_blank\" rel=\"noopener noreferrer\">Project repository and processing code</a></li><li><a href=\"https://nisar.jpl.nasa.gov/\" target=\"_blank\" rel=\"noopener noreferrer\">NASA / ISRO NISAR mission</a></li><li><a href=\"https://search.asf.alaska.edu/\" target=\"_blank\" rel=\"noopener noreferrer\">Alaska Satellite Facility data search</a></li><li><a href=\"https://www.azwater.gov/hydrology/field-services/land-subsidence-arizona\" target=\"_blank\" rel=\"noopener noreferrer\">ADWR land subsidence resources</a></li></ul><p>The terrain and satellite basemaps are served by Esri; attribution appears on the map. Mapping software: Leaflet 1.9.4, BSD-2-Clause. Basemap imagery provides geographic context and is not the NISAR measurement layer.</p>'
  }
};
function openDialog(key) {
  const copy = dialogCopy[key]; if (!copy) return;
  $('#dialog-title').textContent = copy.title;
  $('#dialog-body').innerHTML = copy.body; // Static, locally authored content only.
  $('#about-dialog').showModal();
}
document.querySelectorAll('[data-dialog]').forEach(b => b.addEventListener('click', () => openDialog(b.dataset.dialog)));
$('#close-dialog').addEventListener('click', () => $('#about-dialog').close());
$('#about-dialog').addEventListener('click', e => { if (e.target === $('#about-dialog')) { const r = e.target.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.target.close(); } });
$('#reload-data').addEventListener('click', () => location.reload());
$('#toggle-layers').addEventListener('click', () => {
  const open = $('.sidebar').classList.toggle('layers-open');
  $('#toggle-layers').setAttribute('aria-expanded', String(open));
  $('#toggle-layers').textContent = open ? 'Hide layers' : 'Layers';
});
$('#show-all').addEventListener('click', showAll);
$('#fit-study').addEventListener('click', fitSelected);
document.querySelectorAll('[data-basemap]').forEach(button => button.addEventListener('click', () => {
  if (!map) return;
  map.removeLayer(state.basemaps[state.base]); state.base = button.dataset.basemap;
  state.basemaps[state.base].addTo(map); $('#map-error').hidden = true;
  document.querySelectorAll('[data-basemap]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
}));

async function start() {
  const hotspots = await loadJSON('hotspots.geojson', normalizeHotspots);
  if (hotspots.status !== 'ready') {
    setStatus('Study file needs review');
    $('#detail-content').append(el('h1', '', 'Study outlines unavailable'), note(dataError(hotspots, 'Serve the repository root and include data/processed/hotspots.geojson.')));
    $('#map-error').textContent = 'The study outlines could not load. See the study panel for details.';
    $('#map-error').hidden = false; return;
  }
  state.hotspots = hotspots.value;
  state.slugs = state.hotspots.features.map(f => f.properties.slug);
  state.selected = state.slugs[0];
  $('#study-count').textContent = String(state.slugs.length).padStart(2, '0');
  state.layers.set('hotspots', { name: 'Study outlines', status: 'ready', visible: true, opacity: 1 });
  state.layers.set('rate', { name: 'Ground motion', status: 'loading', visible: true, opacity: 0.75 });
  for (const [key, name] of [['adwr_subsidence', 'ADWR subsidence'], ['datacenters', 'Data centers'], ['habitat', 'Habitat']]) state.layers.set(key, { name, status: 'loading', visible: false, opacity: 0.8 });
  renderHotspots(); initMap();
  state.layers.get('hotspots').layer = outlineGroup;
  renderDetails(); renderLayerControls(); selectHotspot(state.selected);
  const tasks = [
    ...state.slugs.map(async slug => state.series.set(slug, await loadJSON('timeseries_' + slug + '.json', raw => normalizeSeries(raw, slug)))),
    ...state.slugs.map(async slug => state.rates.set(slug, await loadJSON('rate_' + slug + '.json', normalizeRate))),
    ...['adwr_subsidence', 'datacenters', 'habitat'].map(async key => {
      const result = await loadJSON(key + '.geojson', validateGeoJSON);
      const config = state.layers.get(key); config.status = result.status; config.error = result.error;
      if (result.status === 'ready') {
        if (!result.value.features.length) { config.status = 'missing'; return; }
        if (map) { config.layer = makeOverlay(result.value, key); config.visible = true; config.layer.addTo(map); }
      }
    })
  ];
  await Promise.all(tasks);
  renderDetails(); updateRateLayer();
  const hasMeasurements = [...state.series.values()].some(r => r.status === 'ready' && r.value.hasData);
  const problems = [...state.series.values(), ...state.rates.values(), ...state.layers.values()].some(r => ['invalid', 'error'].includes(r.status));
  setStatus(problems ? 'Some files need review' : hasMeasurements ? 'Measured record loaded' : 'Measurements pending');
}
start().catch(error => {
  setStatus('Interface needs attention');
  $('#map-error').textContent = 'The interface could not finish loading. Refresh data to retry.';
  $('#map-error').hidden = false;
  console.error('Atlas initialization failed:', error);
});

