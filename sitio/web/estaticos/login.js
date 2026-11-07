// Pantalla de entrada: espacio 3D navegable con una esfera al centro.
// Clic en la esfera → diálogo de credenciales → POST /api/login.
import * as THREE from '/estaticos/vendor/three-0.160.0/three.module.min.js';

const dialogo = document.getElementById('credenciales');
const form = document.getElementById('form-login');
const correo = document.getElementById('correo');
const contrasena = document.getElementById('contrasena');
const mensaje = document.getElementById('mensaje');
const botonEntrar = document.getElementById('entrar');
const reducirMovimiento = matchMedia('(prefers-reduced-motion: reduce)').matches;

let alEntrar = () => { location.replace('/'); };  // la escena 3D lo reemplaza por un vuelo

function abrirDialogo() {
  if (dialogo.open) return;
  mensaje.textContent = '';
  dialogo.showModal();
  (correo.value ? contrasena : correo).focus();
}

document.getElementById('abrir').addEventListener('click', abrirDialogo);
document.getElementById('cancelar').addEventListener('click', () => dialogo.close());

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  mensaje.textContent = '';
  if (!correo.value.trim() || !contrasena.value) {
    mensaje.textContent = 'Escribe tu correo y tu contraseña.';
    return;
  }
  botonEntrar.disabled = true;
  try {
    const r = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo: correo.value.trim(), contrasena: contrasena.value }),
    });
    if (r.ok) {
      dialogo.close();
      alEntrar();
      return;
    }
    const datos = await r.json().catch(() => ({}));
    mensaje.textContent = r.status === 422 ? 'Usuario o contraseña incorrectos.'
      : (typeof datos.detalle === 'string' ? datos.detalle : 'No se pudo iniciar sesión.');
    contrasena.value = '';
    contrasena.focus();
    dialogo.classList.remove('sacudir');
    void dialogo.offsetWidth;  // reinicia la animación
    dialogo.classList.add('sacudir');
  } catch {
    mensaje.textContent = 'Sin conexión con el servidor. Intenta de nuevo.';
  } finally {
    botonEntrar.disabled = false;
  }
});

// ─────────────────────────────────────────────────────────────────────────
// Escena
// ─────────────────────────────────────────────────────────────────────────
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true });
} catch {
  renderer = null;
}

if (!renderer) {
  // Sin WebGL: el sitio sigue funcionando con el diálogo solo.
  document.body.classList.add('sin-3d');
  abrirDialogo();
  dialogo.addEventListener('cancel', (e) => e.preventDefault());
} else {
  iniciarEscena(renderer);
}

function iniciarEscena(renderer) {
  if (matchMedia('(pointer: coarse)').matches) {
    document.querySelector('#hud .hud-sec').textContent = 'ARRASTRAR: MIRAR · FLECHAS: MOVER';
  }
  const contenedor = document.getElementById('escena');
  const lienzo = renderer.domElement;
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  contenedor.appendChild(lienzo);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050510);
  scene.fog = new THREE.Fog(0x050510, 30, 120);

  const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.1, 500);
  const INICIO = new THREE.Vector3(0, 0, 9);
  camera.position.copy(INICIO);

  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  // Luces
  scene.add(new THREE.AmbientLight(0x404060, 0.6));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);
  const luz1 = new THREE.PointLight(0x00ffcc, 1.5, 50);
  luz1.position.set(0, 10, 0);
  scene.add(luz1);
  const luz2 = new THREE.PointLight(0xff44aa, 1.0, 40);
  luz2.position.set(-10, -5, 5);
  scene.add(luz2);

  // La esfera, al centro, con un halo de alambre que gira
  const esferaMat = new THREE.MeshStandardMaterial({
    color: 0xdd44ff, metalness: 0.5, roughness: 0.15, emissive: 0x441144, emissiveIntensity: 0.4,
  });
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(1.7, 64, 64), esferaMat);
  scene.add(esfera);

  const haloMat = new THREE.MeshBasicMaterial({
    color: 0x78c8ff, wireframe: true, transparent: true, opacity: 0.12,
  });
  const halo = new THREE.Mesh(new THREE.IcosahedronGeometry(2.35, 2), haloMat);
  scene.add(halo);

  const anillo = new THREE.Mesh(
    new THREE.TorusGeometry(2.9, 0.015, 8, 160),
    new THREE.MeshBasicMaterial({ color: 0x00ffaa, transparent: true, opacity: 0.35 }),
  );
  anillo.rotation.x = Math.PI / 2.4;
  scene.add(anillo);

  // Rejillas de referencia y marcadores
  const piso = new THREE.GridHelper(80, 40, 0x223355, 0x112233);
  piso.position.y = -8;
  scene.add(piso);
  const techo = new THREE.GridHelper(80, 40, 0x223355, 0x112233);
  techo.position.y = 8;
  scene.add(techo);

  const marcadorMat = new THREE.MeshBasicMaterial({ color: 0x00aaff });
  const marcadorGeo = new THREE.BoxGeometry(0.2, 0.2, 0.2);
  for (let i = 0; i < 30; i++) {
    const m = new THREE.Mesh(marcadorGeo, marcadorMat);
    const ang = (i / 30) * Math.PI * 2;
    const radio = 18 + Math.random() * 12;
    m.position.set(Math.cos(ang) * radio, (Math.random() - 0.5) * 12, Math.sin(ang) * radio);
    scene.add(m);
  }

  // Estrellas
  const posEstrellas = [];
  for (let i = 0; i < 1500; i++) {
    posEstrellas.push((Math.random() - 0.5) * 300, (Math.random() - 0.5) * 300, (Math.random() - 0.5) * 300);
  }
  const estrellasGeo = new THREE.BufferGeometry();
  estrellasGeo.setAttribute('position', new THREE.Float32BufferAttribute(posEstrellas, 3));
  const estrellas = new THREE.Points(estrellasGeo, new THREE.PointsMaterial({
    color: 0x88ccff, size: 0.4, transparent: true, opacity: 0.7, sizeAttenuation: true,
  }));
  scene.add(estrellas);

  // ── Controles: arrastrar mira, scroll avanza, flechas desplazan ──
  let yaw = 0, pitch = 0, vYaw = 0, vPitch = 0, velocidad = 0;
  const SENS = 0.003, AMORT_MIRADA = 0.85, EMPUJE = 0.4, AMORT_MOV = 0.94, VEL_MAX = 1.5;
  const LATERAL = 0.12, LIMITE = 60, UMBRAL_CLIC = 6;

  let arrastrando = false, ux = 0, uy = 0, inicioX = 0, inicioY = 0;
  const raycaster = new THREE.Raycaster();
  const puntero = new THREE.Vector2();

  function tocaEsfera(x, y) {
    puntero.set((x / innerWidth) * 2 - 1, -(y / innerHeight) * 2 + 1);
    raycaster.setFromCamera(puntero, camera);
    return raycaster.intersectObject(esfera).length > 0;
  }

  lienzo.addEventListener('contextmenu', (e) => e.preventDefault());
  lienzo.addEventListener('pointerdown', (e) => {
    arrastrando = true;
    ux = inicioX = e.clientX;
    uy = inicioY = e.clientY;
    lienzo.setPointerCapture(e.pointerId);
    lienzo.classList.add('arrastrando');
  });
  lienzo.addEventListener('pointermove', (e) => {
    if (arrastrando) {
      const f = e.pointerType === 'touch' ? 0.7 : 1;
      vYaw -= (e.clientX - ux) * SENS * f;
      vPitch -= (e.clientY - uy) * SENS * f;
      ux = e.clientX;
      uy = e.clientY;
    } else {
      lienzo.classList.toggle('sobre-esfera', tocaEsfera(e.clientX, e.clientY));
    }
  });
  const soltar = (e) => {
    if (!arrastrando) return;
    arrastrando = false;
    lienzo.classList.remove('arrastrando');
    const movio = Math.hypot(e.clientX - inicioX, e.clientY - inicioY) > UMBRAL_CLIC;
    if (e.type === 'pointerup' && !movio && tocaEsfera(e.clientX, e.clientY)) abrirDialogo();
  };
  lienzo.addEventListener('pointerup', soltar);
  lienzo.addEventListener('pointercancel', soltar);

  lienzo.addEventListener('wheel', (e) => {
    e.preventDefault();
    velocidad += -Math.sign(e.deltaY) * EMPUJE;
    velocidad = Math.max(-VEL_MAX, Math.min(VEL_MAX, velocidad));
  }, { passive: false });

  // Enter o espacio sobre la escena también abre el diálogo
  addEventListener('keydown', (e) => {
    if (dialogo.open || e.target !== document.body) return;
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrirDialogo(); }
  });

  const flechas = { up: false, down: false, left: false, right: false };
  for (const clave of Object.keys(flechas)) {
    const el = document.getElementById(`btn-${clave}`);
    const presionar = (e) => { e.preventDefault(); flechas[clave] = true; el.classList.add('presionado'); };
    const soltarBtn = () => { flechas[clave] = false; el.classList.remove('presionado'); };
    el.addEventListener('pointerdown', presionar);
    for (const ev of ['pointerup', 'pointerleave', 'pointercancel']) el.addEventListener(ev, soltarBtn);
  }

  // Volver al centro: la esfera siempre se puede encontrar
  let regreso = null;
  document.getElementById('btn-centro').addEventListener('click', () => {
    regreso = { desde: camera.position.clone(), yaw0: yaw, pitch0: pitch, t0: performance.now() };
    velocidad = vYaw = vPitch = 0;
  });

  // Al entrar: vuelo hacia la esfera y luego a «Elige un tema»
  let vuelo = null;
  alEntrar = () => {
    if (reducirMovimiento) { location.replace('/'); return; }
    vuelo = { desde: camera.position.clone(), t0: performance.now() };
    setTimeout(() => location.replace('/'), 900);
  };

  const posEl = document.getElementById('pos');
  const angEl = document.getElementById('ang');
  const reloj = new THREE.Clock();
  const adelante = new THREE.Vector3();
  const suave = (x) => x * x * (3 - 2 * x);

  renderer.setAnimationLoop(() => {
    const t = reloj.getElapsedTime();

    yaw += vYaw;
    pitch += vPitch;
    vYaw *= AMORT_MIRADA;
    vPitch *= AMORT_MIRADA;
    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));

    if (regreso) {
      const k = suave(Math.min(1, (performance.now() - regreso.t0) / 1200));
      camera.position.lerpVectors(regreso.desde, INICIO, k);
      yaw = regreso.yaw0 * (1 - k);
      pitch = regreso.pitch0 * (1 - k);
      if (k >= 1) regreso = null;
    }

    camera.rotation.order = 'YXZ';
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;

    if (vuelo) {
      const k = suave(Math.min(1, (performance.now() - vuelo.t0) / 900));
      camera.position.lerpVectors(vuelo.desde, esfera.position, k * 0.92);
      camera.lookAt(esfera.position);
    } else if (!regreso) {
      adelante.set(0, 0, -1).applyEuler(camera.rotation);
      camera.position.addScaledVector(adelante, velocidad);
      velocidad *= AMORT_MOV;
      if (Math.abs(velocidad) < 0.001) velocidad = 0;
      if (flechas.up) camera.position.y += LATERAL;
      if (flechas.down) camera.position.y -= LATERAL;
      if (flechas.left) camera.position.x -= LATERAL;
      if (flechas.right) camera.position.x += LATERAL;
      camera.position.clampScalar(-LIMITE, LIMITE);
    }

    // La esfera flota y «respira»; más brillo si el puntero está encima o el diálogo abierto
    const activa = lienzo.classList.contains('sobre-esfera') || dialogo.open;
    esfera.position.y = reducirMovimiento ? 0 : Math.sin(t * 0.6) * 0.5;
    halo.position.y = anillo.position.y = esfera.position.y;
    const objetivo = activa ? 0.95 : 0.4 + Math.sin(t * 1.4) * 0.12;
    esferaMat.emissiveIntensity += (objetivo - esferaMat.emissiveIntensity) * 0.08;
    haloMat.opacity += ((activa ? 0.3 : 0.12) - haloMat.opacity) * 0.08;
    halo.rotation.y = t * 0.15;
    halo.rotation.x = t * 0.07;
    anillo.rotation.z = t * 0.2;

    estrellas.rotation.y = t * 0.01;
    luz1.position.x = Math.cos(t * 0.3) * 8;
    luz1.position.z = Math.sin(t * 0.3) * 8;

    posEl.textContent = `POS: ${camera.position.x.toFixed(1)}, ${camera.position.y.toFixed(1)}, ${camera.position.z.toFixed(1)}`;
    angEl.textContent = `ANG: ${(yaw * 180 / Math.PI).toFixed(0)}°, ${(pitch * 180 / Math.PI).toFixed(0)}°`;

    renderer.render(scene, camera);
  });
}
