// Build a portable preview from the same source used by the real app.
// No measured fixture values are created. Basemap tiles still require internet.
import { readFile, writeFile, readdir } from 'node:fs/promises';
const root = new URL('./', import.meta.url);
const read = path => readFile(new URL(path, root), 'utf8');
const [html, css, leafletCSS, leaflet, model, app] = await Promise.all([
  read('index.html'), read('styles.css'), read('vendor/leaflet.css'),
  read('vendor/leaflet.js'), read('model.mjs'), read('app.js')
]);
const data = {}, images = {};
for (const name of await readdir(new URL('../data/processed/', root))) {
  if (name.endsWith('.json') || name.endsWith('.geojson')) {
    // A malformed optional file must not silently become a valid measurement.
    try { data[name] = JSON.parse(await read('../data/processed/' + name)); }
    catch { console.warn('Skipped malformed JSON: ' + name); }
  } else if (/^rate_(eloy|buckeye|willcox)\.png$/.test(name)) {
    images[name] = 'data:image/png;base64,' + (await readFile(new URL('../data/processed/' + name, root))).toString('base64');
  }
}
const json = value => JSON.stringify(value).replace(/</g, '\\u003c');
const inlineJS = 'window.ATLAS_PREVIEW_DATA=' + json(data) + ';window.ATLAS_PREVIEW_IMAGES=' + json(images) + ';\n' +
  model.replace(/^export /gm, '') + '\n' + app.replace(/^import .*?;\n/, '');
let preview = html
  .replace('<link rel="stylesheet" href="./vendor/leaflet.css">', '<style>' + leafletCSS + '</style>')
  .replace('<link rel="stylesheet" href="./styles.css">', '<style>' + css + '</style>')
  .replace('<script src="./vendor/leaflet.js" defer></script>', '<script>' + leaflet.replace(/<\/script/gi, '<\\/script') + '</script>')
  .replace('<script type="module" src="./app.js"></script>', '<script type="module">' + inlineJS.replace(/<\/script/gi, '<\\/script') + '</script>')
  .replace('Independent team project · Preliminary research', 'Portable preview · Preliminary research');
const output = new URL('preview.html', root);
await writeFile(output, preview);
console.log('Created ' + output.pathname);

