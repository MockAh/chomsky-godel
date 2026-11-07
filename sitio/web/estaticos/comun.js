// Lo que comparten «Elige un tema» y la página de tema: sesión, salir y cambiar contraseña.
// Todo texto que viene del servidor se pone con textContent.

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
  const abrir = dialogoContrasena();
  document.getElementById('cuenta-contrasena').addEventListener('click', abrir);
  document.getElementById('cuenta-salir').addEventListener('click', salir);
}
