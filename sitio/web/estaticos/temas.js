// «Elige un tema»: una tarjeta por tema, en el orden de temas.json (vía /api/sesion).
import { cargarSesion, iniciarCuenta, el } from '/estaticos/comun.js';

iniciarCuenta();
const sesion = await cargarSesion();
const lista = document.getElementById('temas');

for (const tema of sesion.temas) {
  const versiones = tema.pestanas
    .map((p) => `${p.etiqueta} ${p.version}${p.aviso ? `, ${p.aviso.toLowerCase()}` : ''}`)
    .join(' · ');
  lista.append(el('li', {},
    el('a', { clase: 'tema-tarjeta', href: `/t/${encodeURIComponent(tema.id)}` },
      el('span', { clase: 'tema-corto', texto: tema.corto }),
      el('span', { clase: 'tema-nombre', texto: tema.nombre }),
      el('span', { clase: 'tema-versiones', texto: versiones || 'Sin contenido aún' }))));
}
