/* Arizona Is Sinking: static map. Data comes from data/*.json and data/*.png (written by src/export_web.py). */
(function () {
  "use strict";
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const $ = (id) => document.getElementById(id);
  const getJSON = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.json(); });
  const fmt = (v, d = 1) => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(d);

  const map = L.map("map", { zoomControl: true, minZoom: 6, maxZoom: 14 }).setView([32.6, -110.8], 8);
  const bases = {
    dark: L.layerGroup([
      L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri, HERE, Garmin, OpenStreetMap contributors", maxZoom: 16 }),
      L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", { maxZoom: 16, pane: "overlayPane" }),
    ]),
    sat: L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { attribution: "Imagery &copy; Esri, Maxar, Earthstar Geographics", maxZoom: 18 }),
  };
  bases.dark.addTo(map);
  document.querySelectorAll("input[name=base]").forEach((r) => r.addEventListener("change", () => {
    Object.values(bases).forEach((b) => map.removeLayer(b)); bases[r.value].addTo(map);
    if (r.value === "sat") bases.sat.bringToBack(); else bases.dark.eachLayer((l) => l.bringToBack());
  }));

  // Panes keep NISAR above Sentinel-1 regardless of the order layers load in.
  map.createPane("s1"); map.getPane("s1").style.zIndex = 330;
  map.createPane("nisar"); map.getPane("nisar").style.zIndex = 340;

  const overlays = {};       // id -> L.ImageOverlay
  const groups = {};         // id -> L.LayerGroup
  function addRaster(id, pane) {
    return getJSON("data/" + id + ".json").then((m) => {
      const o = L.imageOverlay("data/" + id + ".png", m.bounds, { pane, opacity: $("o-" + id).value / 100, interactive: false });
      overlays[id] = o; if ($("t-" + id).checked) o.addTo(map);
    }).catch(() => { const t = $("t-" + id); t.disabled = true; t.parentElement.title = "Layer data not available yet"; t.checked = false; });
  }
  ["nisar_willcox", "nisar_eloy", "s1_rate_desc", "s1_rate_asc"].forEach((id) => {
    $("t-" + id).addEventListener("change", (e) => { const o = overlays[id]; if (!o) return; e.target.checked ? o.addTo(map) : map.removeLayer(o); });
    $("o-" + id).addEventListener("input", (e) => { if (overlays[id]) overlays[id].setOpacity(e.target.value / 100); });
  });
  ["hotspots", "excluded", "flat"].forEach((id) => {
    groups[id] = L.layerGroup(); if ($("t-" + id).checked) groups[id].addTo(map);
    $("t-" + id).addEventListener("change", (e) => (e.target.checked ? groups[id].addTo(map) : map.removeLayer(groups[id])));
  });

  Promise.all([addRaster("s1_rate_desc", "s1"), addRaster("s1_rate_asc", "s1"), addRaster("nisar_willcox", "nisar"), addRaster("nisar_eloy", "nisar")]);

  let chart1 = null, chart2 = null;
  function drawChart(canvasId, prev, labels, series, opts) {
    if (prev) prev.destroy();
    const css = getComputedStyle(document.documentElement);
    return new Chart($(canvasId), {
      type: "line",
      data: { labels, datasets: series.filter(Boolean).map((s) => Object.assign({ pointRadius: 2.5, borderWidth: 2, tension: 0 }, s)) },
      options: { responsive: true, animation: false, plugins: { legend: { labels: { color: css.getPropertyValue("--muted").trim(), boxWidth: 12, font: { size: 11 } } } },
        scales: { x: { ticks: { color: css.getPropertyValue("--muted").trim(), maxTicksLimit: opts.maxTicks || 6, font: { size: 10 } }, grid: { display: false } },
                  y: { title: { display: true, text: "mm (line of sight)", color: css.getPropertyValue("--muted").trim(), font: { size: 11 } }, ticks: { color: css.getPropertyValue("--muted").trim(), font: { size: 10 } }, grid: { color: "rgba(128,128,128,.2)" } } } },
    });
  }

  function chipFor(h) {
    if (h.confirmed === "both look directions") return '<span class="chip ok">Seen from both look directions</span>';
    if (h.confirmed === "single look direction") return '<span class="chip warn">One look direction only: unconfirmed</span>';
    return '<span class="chip warn">Weak in the second look direction</span>';
  }

  function openPanel(h) {
    const s = h.s1, n = h.nisar;
    const asc = s.ascending ? `<div class="kv"><span>Ascending track median</span><span>${fmt(s.ascending.median_rate, 2)} cm/yr (${esc(s.ascending.n_px)} px)</span></div>` : '<div class="kv"><span>Ascending cross-check</span><span>not available here</span></div>';
    let nisarHtml;
    if (n) {
      nisarHtml = `<div class="section-title">NISAR (new, short record)</div><div class="nisar-box">
        <div class="kv"><span>Track / period</span><span>${esc(n.track)}, ${esc(n.dates[0])} to ${esc(n.dates[n.dates.length - 1])}</span></div>
        <div class="kv"><span>Fitted rate</span><span>${fmt(n.rate_cm_yr, 1)} ± ${n.rate_sigma.toFixed(1)} cm/yr</span></div>
        <p class="note"><b>Not a reliable rate yet.</b> ${esc(n.scope)} The fit moves by more than its error bar when we drop a few dates, and the uncertainty shown is optimistic.</p>
        <canvas id="c2" height="150"></canvas></div>`;
    } else {
      nisarHtml = '<div class="section-title">NISAR</div><p class="note">Not analysed for this area: the NISAR tracks we processed do not cover it well, or it was not a target. Sentinel-1 is the evidence here.</p>';
    }
    $("panel-body").innerHTML = `
      <h2>${esc(h.name)}</h2>
      <p class="sub">${esc(h.place)}</p>
      ${chipFor(h)}
      <p>${esc(h.story)}</p>
      <div class="headline"><div class="num">${fmt(s.median_rate, 1)} cm/yr</div>
        <div class="lbl">Median of the sinking ground, Sentinel-1, ${esc(s.period[0].slice(0, 4))} to ${esc(s.period[1].slice(0, 4))}, along the line of sight. Fastest 5% are faster than ${fmt(s.p5_rate, 1)}.</div></div>
      <div class="kv"><span>Sinking area (&ge; 1 cm/yr)</span><span>${esc(s.area_km2)} km²</span></div>
      <div class="kv"><span>Fastest pixel</span><span>${fmt(s.fastest, 1)} cm/yr</span></div>
      <div class="kv"><span>Straight-line fit to the average</span><span>${fmt(s.series_rate, 2)} ± ${s.series_sigma.toFixed(2)} cm/yr</span></div>
      ${asc}
      <div class="section-title">Sentinel-1 history (about 6-month steps)</div>
      <canvas id="c1" height="170"></canvas>
      <p class="note">Red line: average of the sinking pixels. Grey line: stable ground nearby, to show how noisy the measurement is on its own.</p>
      ${nisarHtml}
      <div class="section-title">What is on top</div>
      <p class="note">${esc(h.land)} Source: OpenStreetMap.</p>
      <div class="section-title">Check against official numbers</div>
      ${h.adwr ? `<p class="note">ADWR published InSAR over the same pixels: <b>${fmt(h.adwr.s1, 1)} cm/yr</b> (Sentinel-1, 2017 to 2026; same satellite, so a consistency check) and <b>${fmt(h.adwr.rs2, 1)} cm/yr</b> (RADARSAT-2, 2010 to 2026; independent sensor). Official ADWR feature: ${esc(Object.keys(h.adwr.features).join(", ") || "none")}. Ours: ${fmt(s.median_rate, 1)}.</p>` : '<p class="note">Not compared with Arizona Department of Water Resources values.</p>'}
      <p class="note">Values are line-of-sight, referenced to the frame's median ground; a few mm/yr of bias is possible. Sinking does not by itself show who caused it.</p>`;
    $("panel").classList.remove("hidden"); $("hint").style.display = "none";
    chart1 = drawChart("c1", chart1, s.dates, [
      { label: "Sinking area", data: s.series_mm, borderColor: "#ff6b4a", backgroundColor: "#ff6b4a" },
      s.stable_series_mm ? { label: "Stable ground nearby", data: s.stable_series_mm, borderColor: "#8b98a5", backgroundColor: "#8b98a5", borderDash: [4, 3] } : null], { maxTicks: 6 });
    if (n) chart2 = drawChart("c2", chart2, n.dates, [{ label: "NISAR, whole study box", data: n.series_mm, borderColor: "#e3a93b", backgroundColor: "#e3a93b" }], { maxTicks: 5 });
    map.fitBounds(h.s1.bounds, { paddingTopLeft: [300, 60], paddingBottomRight: [420, 60], maxZoom: 11 });
  }
  $("close").addEventListener("click", () => $("panel").classList.add("hidden"));

  getJSON("data/hotspots.json").then((hs) => {
    const all = [];
    hs.forEach((h) => {
      const col = h.confirmed === "both look directions" ? "#ff6b4a" : "#e3a93b";
      const r = L.rectangle(h.s1.bounds, { color: col, weight: 2, fill: true, fillOpacity: 0.04, dashArray: h.confirmed === "both look directions" ? null : "6 4" }).addTo(groups.hotspots);
      r.bindTooltip(h.name, { sticky: true }); r.on("click", () => openPanel(h)); all.push(h.s1.bounds[0], h.s1.bounds[1]);
    });
    const want = new URLSearchParams(location.search).get("open");
    const target = want && hs.find((h) => h.id === want);
    if (target) { openPanel(target); }
    else if (all.length) map.fitBounds(L.latLngBounds(all), { paddingTopLeft: [300, 40], paddingBottomRight: [40, 40] });
  }).catch(() => { $("hint").textContent = "Hotspot data not found: run src/export_web.py"; });

  getJSON("data/excluded.json").then((xs) => xs.forEach((x) => {
    L.circleMarker([x.lat, x.lon], { radius: 6, color: "#9aa7b4", weight: 2, fillColor: "#5c6773", fillOpacity: 0.9 }).addTo(groups.excluded)
      .bindPopup(`<b>${esc(x.name)}</b><br>${esc(x.why)}`);
  })).catch(() => {});
  getJSON("data/flat.json").then((xs) => xs.forEach((x) => {
    L.circleMarker([x.lat, x.lon], { radius: 5, color: "#3fb97f", weight: 2, fillColor: "#1d6b49", fillOpacity: 0.85 }).addTo(groups.flat)
      .bindPopup(`<b>${esc(x.name)}</b><br>No sinking found: median ${fmt(x.median_rate, 2)} cm/yr within 3 km (Sentinel-1, 2016 to 2026). Only the fastest 5% reach ${fmt(x.p5_rate, 2)}.`);
  })).catch(() => {});

  $("btn-how").addEventListener("click", () => $("dlg-how").showModal());
  $("btn-limits").addEventListener("click", () => $("dlg-limits").showModal());
})();
