import { normalizeSeries, normalizeRate, normalizeHotspots, validateGeoJSON, safeSourceURL, formatNumber, isNumber, cleanInsights } from './model.mjs';

const $ = selector => document.querySelector(selector);
const DATA = new URL('../data/processed/', import.meta.url);
const COLORS = { rust: '#A64B2A', ink: '#2D2A25', olive: '#52664B', sand: '#E4D9C9', slate: '#626D76' };
// Region-wide layers and marker sets exported by the pipeline (data/processed/). Rasters start hidden; NISAR is provisional.
const REGION_LAYERS = [
  ['rate_sentinel1_descending', 'Sentinel-1 sinking rate, 2016–2026', false],
  ['rate_sentinel1_ascending', 'Sentinel-1 cross-check, opposite direction', false],
  ['rate_nisar_willcox', 'NISAR, Willcox box · provisional', false],
  ['rate_nisar_eloy', 'NISAR, Eloy box · provisional, under 4 months', false]
];
const MARKER_LAYERS = [['mines_excluded', 'Probable mines (not groundwater)'], ['checked_flat', 'Checked: no sinking found']];
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
function section(title, noteKey = null) {
  const node = el('section', 'detail-section'), header = el('div', 'detail-section-heading');
  header.append(el('h2', '', title));
  if (noteKey) header.append(explainButton(noteKey));
  node.append(header);
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
  const svg = svgNode('svg', { viewBox: '0 0 330 190', role: 'group', 'aria-label': 'Interactive satellite displacement observations. Focus or tap a dot to inspect the actual measurement.' });
  const valid = series.points.filter(p => isNumber(p.value));
  const stable = series.stablePoints.filter(p => isNumber(p.value));
  const start = Date.parse(series.dates[0]), end = Date.parse(series.dates.at(-1));
  const values = [...valid, ...stable].map(p => p.value);
  let lo = Math.min(...values), hi = Math.max(...values);
  const pad = Math.max((hi - lo) * 0.15, 0.1); lo -= pad; hi += pad;
  const x = date => 45 + (Date.parse(date) - start) / (end - start || 1) * 267;
  const y = val => 144 - (val - lo) / (hi - lo) * 120;
  [lo, (lo + hi) / 2, hi].forEach(v => {
    svg.append(svgNode('line', { x1: 45, x2: 312, y1: y(v), y2: y(v), stroke: '#C9C0B2', 'stroke-width': 0.8 }));
    svg.append(svgNode('text', { x: 38, y: y(v) + 3, 'text-anchor': 'end', class: 'chart-label' }, formatNumber(v)));
  });
  svg.append(svgNode('text', { x: 9, y: 13, class: 'chart-label' }, 'cm'));
  function draw(points) {
    let d = '', gap = true;
    points.forEach(p => {
      if (!isNumber(p.value)) { gap = true; return; }
      d += (gap ? 'M' : 'L') + x(p.date) + ',' + y(p.value) + ' '; gap = false;
    });
    return d;
  }
  svg.append(svgNode('path', { d: draw(series.points), fill: 'none', stroke: COLORS.rust, 'stroke-width': 2.2 }));
  if (stable.length) svg.append(svgNode('path', { d: draw(series.stablePoints), fill: 'none', stroke: COLORS.slate, 'stroke-width': 1.7, 'stroke-dasharray': '4 3' }));
  svg.append(svgNode('text', { x: 45, y: 166, class: 'chart-label' }, series.dates[0]));
  if (series.dates.length > 1) svg.append(svgNode('text', { x: 312, y: 183, 'text-anchor': 'end', class: 'chart-label' }, series.dates.at(-1)));
  const readout = el('output', 'chart-readout', 'Tap or focus a dot to inspect a real satellite observation.');
  readout.setAttribute('aria-live', 'polite');
  let active = null;
  function addPoints(points, name, color) {
    points.forEach(p => {
      if (!isNumber(p.value)) return;
      const description = name + ' · ' + p.date + ' · ' + formatNumber(p.value) + ' cm';
      const point = svgNode('circle', { cx: x(p.date), cy: y(p.value), r: 4.3, fill: color, class: 'chart-point', tabindex: 0, role: 'button', 'aria-label': description });
      const show = () => {
        if (active) active.classList.remove('chart-point-active');
        active = point; point.classList.add('chart-point-active'); readout.textContent = description;
      };
      point.addEventListener('mouseenter', show);
      point.addEventListener('focus', show);
      point.addEventListener('click', show);
      point.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); show(); } });
      svg.append(point);
    });
  }
  addPoints(series.points, 'Study displacement', COLORS.rust);
  addPoints(series.stablePoints, 'Stable-ground reference', COLORS.slate);
  wrap.append(svg, readout);
  if (stable.length) wrap.append(note('Rust: study displacement · Dashed slate: stable reference. Both are line-of-sight measurements.'));
  const details = el('details');
  details.append(el('summary', '', 'View observations as a table'));
  const table = el('table'), head = el('thead'), header = el('tr'), body = el('tbody');
  header.append(el('th', '', 'Date'), el('th', '', 'Displacement (cm)'));
  if (stable.length) header.append(el('th', '', 'Stable ground (cm)'));
  head.append(header);
  series.points.forEach((p, i) => {
    const tr = el('tr'); tr.append(el('td', '', p.date), el('td', '', p.value === null ? 'No observation' : formatNumber(p.value)));
    if (stable.length) tr.append(el('td', '', series.stablePoints[i].value === null ? 'No observation' : formatNumber(series.stablePoints[i].value)));
    body.append(tr);
  });
  table.append(head, body); details.append(table); wrap.append(details);
  return wrap;
}
function renderInsights(root, series) {
  const ins = cleanInsights(series?.insights);
  if (!ins) return;
  const box = el('section', 'insights'), header = el('div', 'detail-section-heading');
  header.append(el('h2', 'insights-title', 'In plain terms'), explainButton('confidence'));
  box.append(header, el('p', 'insights-summary', ins.summary));
  if (ins.confidence) {
    const row = el('div', 'confidence-row');
    [[ins.confidence.where_label, ins.confidence.where], [ins.confidence.how_fast_label, ins.confidence.how_fast]].forEach(([label, level]) => {
      const pill = el('span', 'confidence-pill level-' + level);
      pill.append(el('small', '', label), el('strong', '', 'Confidence: ' + level));
      row.append(pill);
    });
    box.append(row);
  }
  ins.points.forEach(point => {
    const item = el('div', 'insight-point');
    item.append(el('h3', '', point.heading), el('p', '', point.text));
    box.append(item);
  });
  root.append(box);
}
const FIELD_NOTES = {
  confidence: ['How certain is this observation?', 'Confidence describes the strength and quality of the evidence, not how concerning a place is. Several observations, an appropriate reference and independent look directions strengthen interpretation.', 'Confidence labels are from the team’s processed export.'],
  rate: ['What does the reported rate mean?', 'This rate summarizes observed motion over a defined interval. A radar satellite views the ground at an angle, so a line-of-sight rate is not automatically a vertical sinking rate.', 'Read the rate together with its uncertainty, time interval, reference area and sign convention. A motion signal does not establish cause.'],
  chart: ['How do I read the graph?', 'Every dot is an actual exported observation. Tap or focus a dot for its date and value. Blank periods are missing evidence, not zero movement.', 'The dashed comparison, when supplied, tracks stable-reference behavior; no intermediate observations are fabricated.'],
  record: ['Why does metadata matter?', 'Satellite product, orbit track, look direction, real acquisition dates and reference area determine what is comparable.', 'Different viewing geometries or periods cannot automatically be combined as equivalent vertical rates.'],
  validation: ['What does the official comparison show?', 'ADWR radar results provide important historical context. Spatial patterns, correlations and medians may agree or disagree across sensors.', 'Different periods, look directions and reference areas limit direct rate comparisons. Agreement does not by itself validate each study.'],
  study: ['What is a study outline?', 'The boundary represents a project-defined study extent. It is not the observed subsidence footprint.', 'Names and stories are taken from the latest GeoJSON, not a fixed list.'],
  directions: ['Why do two satellite look directions matter?', 'Ascending passes generally move from south toward north, while descending passes move from north toward south. They observe the landscape from different slanted viewing geometries. Comparing both can help distinguish some components of motion and test consistency.', 'One viewing direction alone does not uniquely determine vertical ground movement. Geometry, quality and reference selection matter.']
};
function showFieldNote(title, description, footnote = '') {
  $('#explain-title').textContent = title;
  $('#explain-text').textContent = description;
  $('#explain-note').textContent = footnote;
  $('#explain-drawer').hidden = false;
}
function explainButton(key) {
  const button = el('button', 'explain-trigger', 'Explain ↗'); button.type = 'button';
  button.setAttribute('aria-label', 'Explain: ' + FIELD_NOTES[key][0]);
  button.addEventListener('click', () => showFieldNote(...FIELD_NOTES[key]));
  return button;
}
function showStudyNote(feature) {
  showFieldNote(feature.properties.name, feature.properties.story || FIELD_NOTES.study[1], FIELD_NOTES.study[2]);
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
  const studyContext = el('div', 'study-context'); studyContext.append(explainButton('study')); root.append(studyContext);
  if (p.confirmation) root.append(el('p', 'confirmation-chip' + (p.confirmation === 'single look direction' ? ' unconfirmed' : ''), p.confirmation === 'single look direction' ? 'Unconfirmed · ' + p.confirmation : p.confirmation));
  renderInsights(root, series);
  const hasRate = series && isNumber(series.rate_cm_yr);
  const metric = el('section', 'metric' + (hasRate ? '' : ' pending'));
  metric.append(el('p', 'metric-label', 'Reported displacement rate · line of sight'));
  const value = el('div', 'metric-value', hasRate ? formatNumber(series.rate_cm_yr) : 'Measurement pending');
  if (hasRate) value.append(el('small', '', (isNumber(series.rate_sigma) ? '± ' + formatNumber(series.rate_sigma) + ' ' : '') + 'cm/yr'));
  metric.append(value);
  metric.append(note(hasRate
    ? (isNumber(series.rate_sigma) ? (series.rate_sigma_note || 'Uncertainty supplied by the processing pipeline.') : 'Uncertainty has not been supplied.')
    : dataError(result, 'Awaiting a referenced time series and fitted rate.')));
  if (hasRate) metric.append(note(series.sign_convention || 'Sign convention not supplied. This value is not labelled as vertical sinking.'));
  metric.append(explainButton('rate'));
  root.append(metric);
  const chartSection = section('Displacement through time', 'chart');
  if (series?.hasData) {
    chartSection.append(makeChart(series), note('Relative to: ' + series.reference));
  } else {
    const wait = el('div', 'chart-wait');
    wait.append(el('span', 'waiting-mark'), el('p', '', 'No observations to plot yet'), el('small', '', dataError(result, 'The chart will use the measured record. Pending does not mean zero movement.')));
    chartSection.append(wait);
  }
  root.append(chartSection);
  const record = section('Measurement record', 'record');
  record.append(factList([
    ['Satellite / product', series?.source || meta?.track || 'Not supplied'],
    ['Track / frame', series?.track || meta?.track || 'Coverage check pending'],
    ['Record', series?.dates.length ? series.dates[0] + ' — ' + series.dates.at(-1) : 'Pending'],
    ['Reference', series?.reference || 'Stable reference pending'],
    ['Data release', series?.data_release || meta?.data_release || 'Not supplied']
  ]));
  root.append(record);
  const caveats = Array.isArray(series?.caveats) ? series.caveats.filter(text => typeof text === 'string' && text.trim()) : [];
  if (caveats.length) {
    const limits = section('Study measurement limits');
    caveats.forEach(text => limits.append(el('p', 'validation-note', text)));
    root.append(limits);
  }
  if (typeof series?.nisar?.status_note === 'string' && series.nisar.status_note.trim()) {
    const provisional = section('NISAR status');
    provisional.append(el('p', 'validation-note', series.nisar.status_note));
    root.append(provisional);
  }
  const validation = section('ADWR comparison', 'validation');
  if (series && (isNumber(series.adwr_rate_cm_yr) || isNumber(series.adwr_rs2_rate_cm_yr))) {
    const c = series.adwr_comparison;
    validation.append(note('Median rates over the same sinking pixels · cm/yr, line of sight · ADWR units inferred. These medians differ from the fitted rate above.'));
    validation.append(factList([
      ['Our median', formatNumber(c?.ours_median ?? series.median_rate_cm_yr)],
      ['ADWR Sentinel-1', formatNumber(series.adwr_rate_cm_yr)],
      ['ADWR RADARSAT-2', formatNumber(series.adwr_rs2_rate_cm_yr)]
    ]));
    if (c) validation.append(factList([
      ['Sentinel-1 correlation', formatNumber(c.corr_s1)],
      ['RADARSAT-2 correlation', formatNumber(c.corr_rs2)],
      ['Our − ADWR S1 median', isNumber(c.diff_s1) ? formatNumber(c.diff_s1) + ' cm/yr' : 'Pending']
    ]));
    validation.append(el('p', 'validation-note', series.adwr_note || 'ADWR provenance and comparison periods have not been supplied.'));
    validation.append(el('p', 'validation-note', 'Sentinel-1 is a consistency check, not independent validation. RADARSAT-2 is an independent sensor over a longer period. Agreement varies; these comparisons do not establish validation of every study or of NISAR. Eloy – Picacho is not validated by this test.'));
    const source = el('a', '', 'Comparison method, periods and limitations');
    source.href = 'https://github.com/mansi200304/NASA-Hackathon/blob/main/docs/adwr_validation.md'; source.target = '_blank'; source.rel = 'noopener noreferrer'; validation.append(source);
  } else {
    validation.append(el('p', 'detail-copy', 'Comparison pending'));
    validation.append(el('p', 'validation-note', 'Match the area and observation period before comparing rates.'));
  }
  root.append(validation);
  const story = section('Why this place');
  story.append(el('p', 'detail-copy', p.story));
  if (typeof p.land_use_note === 'string' && p.land_use_note.trim()) story.append(note(p.land_use_note));
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
    button.addEventListener('click', () => { selectHotspot(f.properties.slug); showStudyNote(f); });
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
    layer.on('click', () => { selectHotspot(f.properties.slug); showStudyNote(f); });
    layer.addTo(outlineGroup); state.outlines.set(f.properties.slug, layer);
  });
  map.on('click', event => {
    // A PNG contains colours, not numeric pixels. Do not invent a pixel sampler.
    showFieldNote('Map coordinate · ' + event.latlng.lat.toFixed(4) + ', ' + event.latlng.lng.toFixed(4),
      'This is a selected coordinate, not a verified ground-motion measurement. A colour-mapped PNG has no numeric value we can accurately sample here.',
      'Select a study to inspect the actual exported observations, uncertainty and source metadata.');
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
    if (config.error) label.title = config.error; else if (config.note) label.title = config.note;
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
        else if (config.layer?.setOpacity) config.layer.setOpacity(config.opacity);
        else config.layer?.setStyle({ opacity: config.opacity, fillOpacity: key === 'adwr_subsidence' ? 0 : MARKER_LAYERS.some(l => l[0] === key) ? config.opacity * 0.8 : config.opacity * 0.15 });
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
  const color = key === 'checked_flat' ? COLORS.olive : key === 'mines_excluded' ? COLORS.slate : COLORS.rust;
  return L.geoJSON(raw, {
    bubblingMouseEvents: false,
    style: { color, weight: 1.3, fillOpacity: key === 'adwr_subsidence' ? 0 : 0.12, opacity: 0.8 },
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 5, color, weight: 1.5, fillColor: color, fillOpacity: 0.8 }),
    onEachFeature: (feature, layer) => {
      const p = feature.properties || {};
      const popup = el('div');
      popup.append(el('strong', '', p.name || p.NAME || 'Context feature'));
      if (key === 'adwr_subsidence') {
        if (p.period) popup.append(el('p', '', p.period));
        if (p.source) popup.append(el('p', '', p.source));
      }
      if (key === 'mines_excluded' && p.reason) popup.append(el('p', '', p.reason));
      if (key === 'checked_flat' && p.note) popup.append(el('p', '', p.note + (isNumber(p.median_rate_cm_yr) ? ' · median ' + formatNumber(p.median_rate_cm_yr) + ' cm/yr' : '')));
      const source = safeSourceURL(p.source_url);
      if (source) { const a = el('a', '', 'Source'); a.href = source; a.target = '_blank'; a.rel = 'noopener noreferrer'; popup.append(a); }
      layer.bindPopup(popup);
      layer.on('click', () => showFieldNote(p.name || p.NAME || 'Mapped context',
        [p.reason, p.note, p.period, p.source].filter(v => typeof v === 'string' && v.trim()).join(' · ') || 'This mapped feature comes from a supplied context dataset, not a direct satellite measurement.',
        'Read the feature provenance and study record before interpreting it.'));
    }
  });
}
const dialogCopy = {
  method: {
    title: 'How we measure ground motion',
    body: '<p>A satellite sends a radar pulse down and times the echo, so it knows how far away the ground is. Flying over the same spot again and again, it can tell when the ground has moved closer or farther by a few millimetres.</p><ol><li><strong>Compare two passes.</strong> If the ground moved between two passes, the radar waves return slightly out of step. That shift tells us how far it moved.</li><li><strong>Add up many pairs.</strong> One pair is noisy, because moisture in the air and the upper atmosphere also change the signal. Chaining many pairs over years lets steady sinking add up while random noise does not.</li><li><strong>Two satellites.</strong> Sentinel-1 has flown since 2016, so it gives a ten-year trend. NASA-ISRO NISAR started in late 2025, so its record is still short. We show the Sentinel-1 trend and mark NISAR as preliminary.</li><li><strong>Two viewing directions.</strong> Satellites look at the ground from the east or from the west. When both agree, the sinking is much more likely to be real.</li><li><strong>Check against the official record.</strong> We compare our numbers with the radar results the Arizona Department of Water Resources publishes itself.</li></ol><p>We removed the effects of the Earth\u2019s tides and of the upper atmosphere. We did not remove water vapour in the lower atmosphere, which is a main source of the remaining noise. Numbers are measured along the satellite\u2019s slanted view, not straight down.</p>'
  },
  limits: {
    title: 'Read the map with its limits',
    body: '<ul><li><strong>Pending is not zero.</strong> Empty results mean that a file is missing or has not passed the interface checks.</li><li><strong>Radar measures line-of-sight motion.</strong> A vertical sinking rate needs a justified conversion. A positive or negative value is not interpreted without its sign convention.</li><li><strong>Short records need care.</strong> Seasonal movement, atmospheric errors and the stable reference can influence a fitted rate.</li><li><strong>Data quality varies.</strong> Farming and construction can reduce coherence. Product corrections and release status must be checked.</li><li><strong>Location does not establish cause.</strong> A nearby farm or city does not prove responsibility for ground movement.</li><li><strong>Radar does not observe wildlife.</strong> Any mention of habitat comes from outside sources, not from this measurement.</li><li><strong>Mines move too.</strong> Open-pit mines and their waste piles shift for reasons unrelated to groundwater. We mark the ones we found.</li><li><strong>Blue patches are probably not real uplift.</strong> Rising values, such as on the Willcox Playa floor, most likely come from wet or swelling soil changing the radar signal. We have not verified this.</li><li><strong>Gaps are not zeros.</strong> Where the map is empty, the radar could not measure reliably (over plowed fields, for example). That does not mean the ground is stable.</li><li><strong>A study box is not a sinking zone.</strong> Outlines show the areas the team chose to investigate.</li></ul>'
  },
  sources: {
    title: 'Data, context & code',
    body: '<p>Study extents are defined by the project. Context layers are shown only when their source files are available; missing layers are not replaced with invented features.</p><ul><li><a href=\"https://github.com/mansi200304/NASA-Hackathon\" target=\"_blank\" rel=\"noopener noreferrer\">Project repository and processing code</a></li><li><a href=\"https://nisar.jpl.nasa.gov/\" target=\"_blank\" rel=\"noopener noreferrer\">NASA / ISRO NISAR mission</a></li><li><a href=\"https://search.asf.alaska.edu/\" target=\"_blank\" rel=\"noopener noreferrer\">Alaska Satellite Facility data search</a></li><li><a href=\"https://www.azwater.gov/hydrology/field-services/land-subsidence-arizona\" target=\"_blank\" rel=\"noopener noreferrer\">ADWR land subsidence resources</a></li><li><a href=\"https://www.azwater.gov/gis\" target=\"_blank\" rel=\"noopener noreferrer\">ADWR GIS data: subsidence areas and radar products used for the comparison</a></li><li><a href=\"https://www.openstreetmap.org/copyright\" target=\"_blank\" rel=\"noopener noreferrer\">OpenStreetMap: land-use notes</a></li></ul><p>The terrain and satellite basemaps are served by Esri; attribution appears on the map. Mapping software: Leaflet 1.9.4, BSD-2-Clause. Basemap imagery provides geographic context and is not the NISAR measurement layer.</p>'
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
$('#close-explain').addEventListener('click', () => { $('#explain-drawer').hidden = true; });
document.addEventListener('keydown', event => { if (event.key === 'Escape') $('#explain-drawer').hidden = true; });
$('#about-dialog').addEventListener('click', e => { if (e.target === $('#about-dialog')) { const r = e.target.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.target.close(); } });
$('#reload-data').addEventListener('click', () => location.reload());
$('#toggle-layers').addEventListener('click', () => {
  const open = $('.sidebar').classList.toggle('layers-open');
  $('#toggle-layers').setAttribute('aria-expanded', String(open));
  $('#toggle-layers').textContent = open ? 'Hide layers' : 'Layers';
});
$('#show-all').addEventListener('click', showAll);
$('#fit-study').addEventListener('click', fitSelected);
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const steps = document.querySelectorAll('.overview-steps > div');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.1 });
  steps.forEach(step => { step.classList.add('overview-step-in'); observer.observe(step); });
}
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
  state.layers.set('adwr_subsidence', { name: 'ADWR subsidence areas', status: 'loading', visible: false, opacity: 0.8 });
  for (const [key, name, visible] of REGION_LAYERS) state.layers.set(key, { name, status: 'loading', visible, opacity: 0.7 });
  for (const [key, name] of MARKER_LAYERS) state.layers.set(key, { name, status: 'loading', visible: true, opacity: 0.9 });
  renderHotspots(); initMap();
  state.layers.get('hotspots').layer = outlineGroup;
  renderDetails(); renderLayerControls(); selectHotspot(state.selected);
  const tasks = [
    ...state.slugs.map(async slug => state.series.set(slug, await loadJSON('timeseries_' + slug + '.json', raw => normalizeSeries(raw, slug)))),
    ...state.slugs.map(async slug => state.rates.set(slug, await loadJSON('rate_' + slug + '.json', normalizeRate))),
    ...['adwr_subsidence', ...MARKER_LAYERS.map(l => l[0])].map(async key => {
      const result = await loadJSON(key + '.geojson', validateGeoJSON);
      const config = state.layers.get(key); config.status = result.status; config.error = result.error;
      if (result.status === 'ready') {
        if (!result.value.features.length) { config.status = 'missing'; return; }
        if (map) { config.layer = makeOverlay(result.value, key); config.visible = true; config.layer.addTo(map); }
      }
    }),
    ...REGION_LAYERS.map(async ([key]) => {
      const result = await loadJSON(key + '.json', normalizeRate);
      const config = state.layers.get(key); config.status = result.status; config.error = result.error;
      if (result.status !== 'ready') return;
      const meta = result.value;
      config.note = [meta.track, meta.sign_convention, meta.data_release].filter(Boolean).join(' · ');
      const src = window.ATLAS_PREVIEW_IMAGES?.[key + '.png'] || new URL(key + '.png', DATA).href;
      if (map) { config.layer = L.imageOverlay(src, meta.bounds, { pane: 'measurements', opacity: config.opacity, interactive: false }); if (config.visible) config.layer.addTo(map); }
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

