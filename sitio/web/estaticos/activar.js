// Crear contraseña con el enlace de un solo uso: /activar#<ficha>.
// La ficha va en el fragmento, así no llega a los registros del servidor.
const ficha = location.hash.slice(1);
history.replaceState(null, '', '/activar');  // que no quede en el historial ni en pantalla

const form = document.getElementById('form-activar');
const nueva = document.getElementById('nueva');
const repetir = document.getElementById('repetir');
const mensaje = document.getElementById('mensaje');
const crear = document.getElementById('crear');
const ENLACE_INVALIDO = 'Este enlace ya se usó o venció.';

function sacudir() {
  form.classList.remove('sacudir');
  void form.offsetWidth;
  form.classList.add('sacudir');
}

if (!ficha) {
  mensaje.textContent = ENLACE_INVALIDO;
  crear.disabled = true;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  mensaje.textContent = '';
  if (nueva.value !== repetir.value) {
    mensaje.textContent = 'Las contraseñas no coinciden.';
    sacudir();
    return;
  }
  crear.disabled = true;
  try {
    const r = await fetch('/api/activar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ficha, contrasena: nueva.value }),
    });
    if (r.ok) { location.replace('/'); return; }
    const datos = await r.json().catch(() => ({}));
    if (r.status === 410) {
      mensaje.textContent = ENLACE_INVALIDO;
      return;  // el botón queda desactivado
    }
    mensaje.textContent = (datos.errores || []).join(' ') || datos.detalle || 'No se pudo crear la contraseña.';
    sacudir();
  } catch {
    mensaje.textContent = 'Sin conexión con el servidor. Intenta de nuevo.';
  }
  crear.disabled = false;
});
