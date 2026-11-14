import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeSeries, normalizeRate, validateGeoJSON, safeSourceURL, formatNumber } from '../model.mjs';

const series = extra => ({ hotspot: 'eloy', units: 'cm', reference: 'Synthetic test reference', dates: ['2026-01-01', '2026-01-13'], displacement: [0, -1], rate_cm_yr: -2, rate_sigma: 0.2, ...extra });
test('pending nulls never become zero, while a real zero remains valid', () => {
  const pending = normalizeSeries(series({ dates: [], displacement: [], reference: '', rate_cm_yr: null, rate_sigma: null }), 'eloy');
  assert.equal(pending.hasData, false);
  assert.equal(pending.rate_cm_yr, null);
  assert.equal(formatNumber(null), 'Pending');
  const zero = normalizeSeries(series({ displacement: [0, 0], rate_cm_yr: 0, rate_sigma: 0 }), 'eloy');
  assert.equal(zero.hasData, true);
  assert.equal(zero.rate_cm_yr, 0);
});
test('null chart gaps survive normalization', () => {
  const result = normalizeSeries(series({ dates: ['2026-01-01', '2026-01-13', '2026-01-25'], displacement: [0, null, -1] }), 'eloy');
  assert.equal(result.points[1].value, null);
});
test('measured data requires a reference and honest units', () => {
  assert.throws(() => normalizeSeries(series({ reference: '' }), 'eloy'));
  assert.throws(() => normalizeSeries(series({ units: 'mm' }), 'eloy'));
  assert.throws(() => normalizeSeries(series({ rate_sigma: -1 }), 'eloy'));
  assert.throws(() => normalizeSeries(series({ displacement: [0, '1'] }), 'eloy'));
});
test('duplicate, out-of-order and nonexistent dates are rejected', () => {
  for (const dates of [['2026-01-01', '2026-01-01'], ['2026-01-13', '2026-01-01'], ['2026-02-30', '2026-03-15']]) {
    assert.throws(() => normalizeSeries(series({ dates }), 'eloy'));
  }
});
test('raster bounds are validated as latitude/longitude with a real display domain', () => {
  const meta = { bounds: [[32.6, -111.9], [33, -111.4]], units: 'cm/yr', vmin: -5, vmax: 0, dates: ['2026-01-01', '2026-01-13'] };
  assert.equal(normalizeRate(meta), meta);
  assert.throws(() => normalizeRate({ ...meta, bounds: [[-111.9, 32.6], [-111.4, 33]] }));
  assert.throws(() => normalizeRate({ ...meta, vmax: -5 }));
  assert.throws(() => normalizeRate({ ...meta, crs: 'EPSG:32612' }));
});
test('GeoJSON rejects projected coordinates; popup links reject executable schemes', () => {
  const feature = { type: 'FeatureCollection', features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: [-111, 33] }, properties: {} }] };
  assert.equal(validateGeoJSON(feature), feature);
  assert.throws(() => validateGeoJSON({ ...feature, features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: [400000, 3600000] } }] }));
  assert.equal(safeSourceURL('javascript:alert(1)'), null);
  assert.equal(safeSourceURL('https://example.com/source'), 'https://example.com/source');
});

