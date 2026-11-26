// Lo que comparten «Elige un tema» y la página de tema: sesión, salir y cambiar contraseña.
// Todo texto que viene del servidor se pone con textContent.
// Museo (P-34): bajo /m/<clave>/ es la versión de solo lectura, sin cuenta ni anotaciones;
// bajo /m/<clave>/en/ la misma en inglés (P-35). El sitio con login sigue solo en español.

const enMuseo = location.pathname.match(/^\/m\/([^/]+)(\/en)?(?=\/|$)/);
export const MUSEO = Boolean(enMuseo);
export const IDIOMA = enMuseo && enMuseo[2] ? 'en' : 'es';
export const BASE = enMuseo ? enMuseo[0] : '';
export const INICIO = MUSEO ? `${BASE}/temas` : '/';

// Textos fijos del sitio en inglés, por su texto en español.
const EN = {
  'Elige un tema': 'Choose a topic',
  'Lecciones de Claude': 'Lessons by Claude',
  '‹ Temas': '‹ Topics',
  Temas: 'Topics',
  'Contenido del tema': 'Topic content',
  'Este tema todavía no tiene contenido.': 'This topic has no content yet.',
  'Sin contenido aún': 'No content yet',
  'Solo en español': 'Spanish only',
  'CLIC EN LA ESFERA PARA ENTRAR': 'CLICK THE SPHERE TO ENTER',
  'ARRASTRAR: MIRAR · SCROLL: AVANZAR': 'DRAG: LOOK · SCROLL: MOVE',
  'ARRASTRAR: MIRAR · FLECHAS: MOVER': 'DRAG: LOOK · ARROWS: MOVE',
  'Volver al centro': 'Back to center',
  Entrar: 'Enter',
};

export const t = (texto) => (IDIOMA === 'en' && EN[texto]) || texto;

/** Traduce los elementos marcados con data-i18n (y su title) y pone el lang de la página. */
export function traducirPagina() {
  if (IDIOMA !== 'en') return;
  document.documentElement.lang = 'en';
  for (const nodo of document.querySelectorAll('[data-i18n]')) {
    nodo.textContent = t(nodo.textContent.trim());
    if (nodo.title) nodo.title = t(nodo.title);
  }
  for (const nodo of document.querySelectorAll('[aria-label]')) nodo.setAttribute('aria-label', t(nodo.getAttribute('aria-label')));
}

const CLAVE_IDIOMA = 'museo-idioma';

/** Enlace al mismo lugar en el otro idioma; recuerda la elección en este navegador. */
export function enlaceIdioma(clase = 'boton boton-texto idioma') {
  const otro = IDIOMA === 'en' ? 'es' : 'en';
  const raiz = BASE.replace(/\/en$/, '');
  const resto = location.pathname.slice(BASE.length);
  const a = el('a', {
    clase, id: 'idioma', lang: otro, hreflang: otro,
    href: `${raiz}${otro === 'en' ? '/en' : ''}${resto}${location.hash}`,
    texto: otro === 'en' ? 'English' : 'Español',
  });
  a.addEventListener('click', () => {
    try { localStorage.setItem(CLAVE_IDIOMA, otro); } catch { /* sin almacenamiento: no pasa nada */ }
  });
  return a;
}

/** En la entrada del museo en español, lleva al inglés si este navegador lo eligió antes. */
export function idiomaRecordado() {
  if (!MUSEO || IDIOMA === 'en' || location.pathname !== BASE) return false;
  let pedido = null;
  try { pedido = localStorage.getItem(CLAVE_IDIOMA); } catch { /* nada */ }
  if (pedido !== 'en') return false;
  location.replace(`${BASE}/en`);
  return true;
}

export async function api(ruta, opciones = {}) {
  const r = await fetch(ruta, {
    ...opciones,
    headers: { 'Content-Type': 'application/json', ...(opciones.headers || {}) },
  });
  if (r.status === 401 && !opciones.permitir401) {
    location.replace('/login');
    throw new Error('sin sesión');
  }
  return r;
}

export function el(etiqueta, props = {}, ...hijos) {
  const nodo = document.createElement(etiqueta);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'texto') nodo.textContent = v;
    else if (k === 'clase') nodo.className = v;
    else if (k.startsWith('on')) nodo.addEventListener(k.slice(2), v);
    else nodo.setAttribute(k, v);
  }
  for (const h of hijos) if (h) nodo.append(h);
  return nodo;
}

export async function cargarSesion() {
  if (MUSEO) {
    const r = await fetch(`${BASE}/api/temas`);
    if (!r.ok) { location.replace(BASE); throw new Error('museo cerrado'); }
    return { correo: '', rol: 'lector', temas: (await r.json()).temas };
  }
  const r = await api('/api/sesion');
  const sesion = await r.json();
  document.getElementById('cuenta-correo').textContent = sesion.correo;
  return sesion;
}

async function salir() {
  try {
    await fetch('/api/logout', { method: 'POST' });
  } finally {
    location.replace('/login');
  }
}

function dialogoContrasena() {
  const mensaje = el('p', { clase: 'mensaje', role: 'alert' });
  const campo = (id, texto, auto) => {
    const input = el('input', { id, type: 'password', autocomplete: auto, required: '', maxlength: '256' });
    return [el('label', { clase: 'campo' }, el('span', { texto }), input), input];
  };
  const [lActual, actual] = campo('cc-actual', 'Contraseña actual', 'current-password');
  const [lNueva, nueva] = campo('cc-nueva', 'Contraseña nueva', 'new-password');
  const [lRepetir, repetir] = campo('cc-repetir', 'Repítela', 'new-password');
  const enviar = el('button', { type: 'submit', clase: 'boton boton-principal', texto: 'Cambiar' });
  const dialogo = el('dialog', { clase: 'tarjeta', 'aria-labelledby': 'cc-titulo' });
  const form = el('form', { novalidate: '' },
    el('h2', { id: 'cc-titulo', texto: 'Cambiar contraseña' }),
    lActual, lNueva, lRepetir,
    el('p', { clase: 'regla', texto: '12 caracteres o más, con mayúscula, minúscula, número y símbolo. Se cerrarán tus otras sesiones.' }),
    mensaje,
    el('div', { clase: 'acciones' },
      el('button', { type: 'button', clase: 'boton boton-texto', texto: 'Cancelar', onclick: () => dialogo.close() }),
      enviar));
  dialogo.append(form);
  document.body.append(dialogo);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    mensaje.className = 'mensaje';
    if (nueva.value !== repetir.value) { mensaje.textContent = 'Las contraseñas nuevas no coinciden.'; return; }
    enviar.disabled = true;
    try {
      const r = await api('/api/contrasena', {
        method: 'POST', body: JSON.stringify({ actual: actual.value, nueva: nueva.value }),
      });
      const datos = await r.json().catch(() => ({}));
      if (r.ok) {
        mensaje.className = 'mensaje ok';
        mensaje.textContent = 'Listo. Tu contraseña cambió.';
        form.reset();
        setTimeout(() => dialogo.close(), 1200);
      } else {
        mensaje.textContent = (datos.errores || []).join(' ') || datos.detalle || 'No se pudo cambiar.';
      }
    } finally {
      enviar.disabled = false;
    }
  });

  return () => {
    form.reset();
    mensaje.textContent = '';
    dialogo.showModal();
    actual.focus();
  };
}

export function iniciarCuenta() {
  document.querySelectorAll('a.marca, a.volver').forEach((a) => { a.href = INICIO; });
  if (MUSEO) {
    traducirPagina();
    document.querySelector('.cuenta')?.replaceChildren(enlaceIdioma());
    return;
  }
  const abrir = dialogoContrasena();
  document.getElementById('cuenta-contrasena').addEventListener('click', abrir);
  document.getElementById('cuenta-salir').addEventListener('click', salir);
}
