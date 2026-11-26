// «Elige un tema»: una tarjeta por tema, en el orden de temas.json (vía /api/sesion).
// Los temas con grupo «claude» van aparte, en «Lecciones de Claude» (una por fase).
import { cargarSesion, iniciarCuenta, el, t, BASE, MUSEO } from '/estaticos/comun.js';

iniciarCuenta();
const sesion = await cargarSesion();
if (MUSEO) document.title = `chomsky-godel · ${t('Temas')}`;
const lista = document.getElementById('temas');
const lecciones = document.getElementById('lecciones');

for (const tema of sesion.temas) {
  const deClaude = tema.grupo === 'claude';
  const versiones = tema.pestanas
    .map((p) => `${p.etiqueta} ${p.version}${p.aviso ? `, ${p.aviso.toLowerCase()}` : ''}${p.solo_es ? ` (${t('Solo en español')})` : ''}`)
    .join(' · ');
  (deClaude ? lecciones : lista).append(el('li', {},
    el('a', { clase: deClaude ? 'tema-tarjeta leccion-tarjeta' : 'tema-tarjeta', href: `${BASE}/t/${encodeURIComponent(tema.id)}` },
      el('span', { clase: 'tema-corto', texto: tema.corto }),
      el('span', { clase: 'tema-nombre', texto: tema.nombre }),
      el('span', { clase: 'tema-versiones', texto: versiones || t('Sin contenido aún') }))));
}
document.getElementById('bloque-lecciones').hidden = !lecciones.children.length;
