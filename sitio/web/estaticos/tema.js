// Página de tema: pestañas (role=tablist) con un iframe por pestaña.
// Los iframes se quedan montados al cambiar de pestaña para no perder el avance;
// las que no son la inicial se cargan la primera vez que se abren.
// En el museo (P-34) no se cargan las anotaciones.
import { cargarSesion, iniciarCuenta, el, t, BASE, INICIO, MUSEO } from '/estaticos/comun.js';

iniciarCuenta();
const sesion = await cargarSesion();
const idTema = decodeURIComponent(location.pathname.slice(BASE.length).split('/')[2] || '');
const tema = sesion.temas.find((t) => t.id === idTema);
const barra = document.getElementById('pestanas');
const paneles = document.getElementById('paneles');

if (!tema) {
  location.replace(INICIO);
} else {
  document.title = `chomsky-godel · ${tema.corto}`;
  document.getElementById('tema-nombre').textContent = tema.nombre;
  await montar(tema);
}

function ponerAviso(iframe, aviso) {
  // El contenido comparte origen (P-1): el sitio pone la etiqueta sin modificar el archivo.
  const doc = iframe.contentDocument;
  if (!doc || !doc.body || doc.getElementById('aviso-sitio')) return;
  const etiqueta = doc.createElement('div');
  etiqueta.id = 'aviso-sitio';
  etiqueta.textContent = aviso;
  etiqueta.style.cssText = 'position:sticky;top:0;z-index:2147483647;display:inline-block;margin:8px;'
    + 'padding:4px 10px;border-radius:4px;background:#050510;color:#78c8ff;border:1px solid #78c8ff;'
    + 'font:600 11px/1.6 ui-monospace,monospace;letter-spacing:2px;text-transform:uppercase;';
  doc.body.prepend(etiqueta);
}

async function montar(tema) {
  if (!tema.pestanas.length) {
    paneles.append(el('p', { clase: 'vacio', texto: t('Este tema todavía no tiene contenido.') }));
    return;
  }
  const botones = [];
  const panelPor = new Map();
  const notas = MUSEO ? { cambioPestana() {} }
    : await (await import('/estaticos/anotaciones.js'))
      .iniciarAnotaciones({ tema, sesion, iframeDe: (pid) => panelPor.get(pid)?.iframe });

  tema.pestanas.forEach((p) => {
    const boton = el('button', {
      type: 'button', role: 'tab', clase: 'pestana', id: `tab-${p.id}`,
      'aria-controls': `panel-${p.id}`, 'aria-selected': 'false', tabindex: '-1', texto: p.etiqueta,
    });
    boton.dataset.pestana = p.id;
    boton.addEventListener('click', () => activar(p.id));
    botones.push(boton);
    barra.append(boton);

    const panel = el('section', { clase: 'panel', id: `panel-${p.id}`, role: 'tabpanel', 'aria-labelledby': `tab-${p.id}` });
    panel.hidden = true;
    paneles.append(panel);
    panelPor.set(p.id, { panel, pestana: p, iframe: null });
  });

  function activar(id, enfocar = false) {
    for (const b of botones) {
      const sel = b.dataset.pestana === id;
      b.setAttribute('aria-selected', String(sel));
      b.tabIndex = sel ? 0 : -1;
      if (sel && enfocar) b.focus();
    }
    for (const [pid, info] of panelPor) {
      info.panel.hidden = pid !== id;
      if (pid === id && !info.iframe) {
        const iframe = el('iframe', {
          src: `${BASE}/contenido/${encodeURIComponent(tema.id)}/${encodeURIComponent(pid)}`,
          title: `${tema.corto} · ${info.pestana.etiqueta}`,
        });
        const aviso = [info.pestana.aviso, info.pestana.solo_es && t('Solo en español')].filter(Boolean).join(' · ');
        if (aviso) iframe.addEventListener('load', () => ponerAviso(iframe, aviso));
        info.panel.append(iframe);
        info.iframe = iframe;
      }
    }
    history.replaceState(null, '', `#${id}`);
    notas.cambioPestana(id);
  }

  barra.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    const i = botones.indexOf(document.activeElement);
    if (i < 0) return;
    const j = (i + (e.key === 'ArrowRight' ? 1 : -1) + botones.length) % botones.length;
    activar(botones[j].dataset.pestana, true);
  });

  const pedida = location.hash.slice(1);
  activar(panelPor.has(pedida) ? pedida : tema.pestanas[0].id);
}
