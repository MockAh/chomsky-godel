// Anotaciones de la página de tema (spec 01 §2 P4 y 03 §3).
// - Una casilla por sección del tema y, si la lección lo anuncia con postMessage, una por elemento.
// - Guardado automático: 800 ms tras dejar de escribir y al salir del campo; reintento cada 5 s;
//   envío final con keepalive al cerrar; aviso del navegador si queda algo sin guardar.
// - Si la sesión venció (401) se avisa y nunca se borra lo escrito.
import { api, el } from '/estaticos/comun.js';

const ESPERA = 800;
const REINTENTO = 5000;
const MAX_TEXTO = 20000;
const TIPOS = { ejercicio: 'este ejercicio', circuito: 'este circuito', pregunta: 'esta pregunta', lectura: 'esta lectura' };
const MSG_401 = 'Tu sesión terminó y esto no se guardó. Copia tu texto, vuelve a entrar y pégalo aquí.';

const fecha = (s) => new Date(s * 1000).toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' });
const ruta = (...partes) => partes.map(encodeURIComponent).join('/');

// ─────────────────────────────────────────────────────────────────────────
// Campos con guardado automático
// ─────────────────────────────────────────────────────────────────────────
const campos = new Set();
let sesionTerminada = false;

function avisarSesion() {
  sesionTerminada = true;
  document.getElementById('aviso-sesion').hidden = false;
}

class Campo {
  constructor({ url, extra = {}, texto = '', etiqueta, alCambiar = () => {} }) {
    this.url = url;
    this.extra = extra;
    this.alCambiar = alCambiar;
    this.sucio = false;
    this.guardando = false;
    this.temporizador = null;
    this.textarea = el('textarea', { maxlength: String(MAX_TEXTO), rows: '4', 'aria-label': etiqueta, spellcheck: 'true' });
    this.textarea.value = texto;
    this.estado = el('span', { clase: 'nota-estado', 'aria-live': 'polite' });
    this.textarea.addEventListener('input', () => {
      this.sucio = true;
      this.mostrar('Sin guardar');
      this.alCambiar(this.textarea.value);
      this.programar(ESPERA);
    });
    this.textarea.addEventListener('blur', () => { if (this.sucio) this.programar(0); });
    campos.add(this);
  }

  mostrar(texto, clase = '') {
    this.estado.textContent = texto;
    this.estado.className = `nota-estado ${clase}`;
  }

  programar(ms) {
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => this.guardar(), ms);
  }

  cuerpo() {
    return JSON.stringify({ ...this.extra, texto: this.textarea.value });
  }

  async guardar() {
    if (!this.sucio || this.guardando) return;
    if (sesionTerminada) { this.mostrar('No guardado: sesión terminada', 'error'); return; }
    this.guardando = true;
    const enviado = this.textarea.value;
    this.mostrar('Guardando…');
    try {
      const r = await fetch(this.url, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: this.cuerpo() });
      if (r.status === 401) {
        avisarSesion();
        this.mostrar('No guardado: sesión terminada', 'error');
        return;  // no se reintenta ni se borra
      }
      if (!r.ok) throw new Error(String(r.status));
      if (this.textarea.value === enviado) {
        this.sucio = false;
        this.mostrar(`Guardado ${new Date().toLocaleTimeString('es-MX', { timeStyle: 'short' })}`, 'ok');
      } else {
        this.programar(ESPERA);  // se siguió escribiendo mientras se guardaba
      }
    } catch {
      this.mostrar('No se guardó; reintentando…', 'error');
      this.programar(REINTENTO);
    } finally {
      this.guardando = false;
    }
  }

  // Al cerrar la página: último intento que sobrevive a la descarga
  despedir() {
    if (!this.sucio || sesionTerminada) return;
    fetch(this.url, { method: 'PUT', keepalive: true, headers: { 'Content-Type': 'application/json' }, body: this.cuerpo() });
  }
}

addEventListener('pagehide', () => { for (const c of campos) c.despedir(); });
addEventListener('beforeunload', (e) => {
  if ([...campos].some((c) => c.sucio)) { e.preventDefault(); e.returnValue = ''; }
});

// ─────────────────────────────────────────────────────────────────────────
// Vista «Todas las anotaciones»
// ─────────────────────────────────────────────────────────────────────────
export async function iniciarAnotaciones({ tema, sesion, iframeDe }) {
  const esAdmin = sesion.rol === 'admin';
  const anotables = tema.pestanas.filter((p) => p.anotable);
  const boton = document.getElementById('btn-anotaciones');
  const cajon = document.getElementById('cajon-notas');
  const cuerpoCajon = document.getElementById('cajon-cuerpo');
  const subtitulo = document.getElementById('cajon-pestana');
  const flotante = document.getElementById('btn-anotar-elemento');
  const dialogo = document.getElementById('dlg-elemento');

  document.getElementById('aviso-sesion').textContent = MSG_401;
  if (!anotables.length) return { cambioPestana() {} };

  const r = await api(`/api/anotaciones/${ruta(tema.id)}`);
  const datos = await r.json();

  if (esAdmin) {
    document.getElementById('cajon-exportar').hidden = false;
  }

  let pestanaActiva = null;
  const vistas = new Map();        // pestaña → { nodo, secciones: Map(seccion → {nodo, lista}) }
  const elementos = new Map();     // `${pestana}|${seccion}|${titulo}` → { campo, info, vista }
  const elementoAnunciado = new Map();  // pestaña → info del último elemento anunciado

  const vistaElemento = (info, campo) => {
    const vista = el('div', { clase: 'nota-elemento' },
      el('div', { clase: 'nota-elemento-titulo' },
        el('span', { texto: info.titulo }),
        el('span', { clase: 'nota-meta', texto: [info.tipo, info.estado].filter(Boolean).join(' · ') })),
      el('p', { clase: 'nota-vista', texto: campo.textarea.value || '—' }),
      el('button', { type: 'button', clase: 'boton boton-texto', texto: 'Editar', onclick: () => abrirElemento(info) }));
    return vista;
  };

  function registrarElemento(pid, info, texto = '') {
    const clave = `${pid}|${info.seccion}|${info.titulo}`;
    if (elementos.has(clave)) return elementos.get(clave);
    const registro = { info, vista: null, campo: null };
    registro.campo = new Campo({
      url: `/api/anotaciones/${ruta(tema.id, pid, info.seccion)}/elemento`,
      extra: { titulo: info.titulo, tipo: info.tipo, estado: info.estado || '' },
      texto,
      etiqueta: `Nota: ${info.titulo}`,
      alCambiar: (v) => { registro.vista.querySelector('.nota-vista').textContent = v || '—'; },
    });
    registro.vista = vistaElemento(info, registro.campo);
    elementos.set(clave, registro);
    vistas.get(pid)?.secciones.get(info.seccion)?.lista.append(registro.vista);
    return registro;
  }

  function construirVista(p) {
    const nodo = el('div', { clase: 'notas-pestana' });
    const secciones = new Map();
    for (const s of tema.secciones) {
      const mia = datos.mias.find((n) => n.pestana === p.id && n.seccion === s.id);
      const campo = new Campo({
        url: `/api/anotaciones/${ruta(tema.id, p.id, s.id)}`,
        texto: mia ? mia.texto : '',
        etiqueta: `Nota de la sección ${s.nombre}`,
      });
      const lista = el('div', { clase: 'notas-elementos' });
      const bloque = el('section', { clase: 'nota-seccion', id: `nota-${p.id}-${s.id}` },
        el('h3', { texto: s.nombre }), campo.textarea, campo.estado, lista);

      const previas = datos.anteriores.filter((n) => n.pestana === p.id && n.seccion === s.id);
      if (previas.length) bloque.append(listaLectura(`Mis notas de versiones anteriores (${previas.length})`, previas));
      if (esAdmin) {
        const otras = datos.de_otros.filter((n) => n.pestana === p.id && n.seccion === s.id);
        if (otras.length) bloque.append(listaLectura(`Notas de otras cuentas (${otras.length})`, otras, true));
      }
      secciones.set(s.id, { nodo: bloque, lista });
      nodo.append(bloque);
    }
    vistas.set(p.id, { nodo, secciones });
    cuerpoCajon.append(nodo);
    for (const n of datos.mias_elementos.filter((n) => n.pestana === p.id)) {
      registrarElemento(p.id, { seccion: n.seccion, ...n.elemento }, n.texto);
    }
  }

  function listaLectura(titulo, notas, conAutor = false) {
    const det = el('details', { clase: 'notas-previas' }, el('summary', { texto: titulo }));
    for (const n of notas) {
      const meta = [conAutor ? n.autor_rol : null, n.version, fecha(n.actualizada),
        n.elemento ? `· ${n.elemento.titulo}` : null].filter(Boolean).join(' · ');
      det.append(el('div', { clase: 'nota-previa' },
        el('div', { clase: 'nota-meta', texto: meta }),
        el('p', { clase: 'nota-vista', texto: n.texto })));
    }
    return det;
  }

  function mostrarPestana(pid) {
    for (const [id, v] of vistas) v.nodo.hidden = id !== pid;
    const p = tema.pestanas.find((x) => x.id === pid);
    subtitulo.textContent = p ? `${p.etiqueta} · ${p.version}` : '';
  }

  function abrirCajon(seccion) {
    if (!pestanaActiva) return;
    cajon.hidden = false;
    boton.setAttribute('aria-expanded', 'true');
    document.body.classList.add('con-cajon');
    if (seccion) {
      document.getElementById(`nota-${pestanaActiva}-${seccion}`)?.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
  }

  function cerrarCajon() {
    cajon.hidden = true;
    boton.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('con-cajon');
  }

  boton.addEventListener('click', () => (cajon.hidden ? abrirCajon() : cerrarCajon()));
  document.getElementById('cajon-cerrar').addEventListener('click', () => { cerrarCajon(); boton.focus(); });

  // Diálogo de un elemento (ejercicio, circuito, pregunta, lectura)
  const dlgTitulo = document.getElementById('dlg-elemento-titulo');
  const dlgMeta = document.getElementById('dlg-elemento-meta');
  const dlgCampo = document.getElementById('dlg-elemento-campo');
  document.getElementById('dlg-elemento-cerrar').addEventListener('click', () => dialogo.close());

  function abrirElemento(info) {
    const registro = registrarElemento(pestanaActiva, info);
    dlgTitulo.textContent = info.titulo;
    dlgMeta.textContent = [info.tipo, info.estado, tema.secciones.find((s) => s.id === info.seccion)?.nombre]
      .filter(Boolean).join(' · ');
    dlgCampo.replaceChildren(registro.campo.textarea, registro.campo.estado);
    dialogo.showModal();
    registro.campo.textarea.focus();
  }

  flotante.addEventListener('click', () => {
    const info = elementoAnunciado.get(pestanaActiva);
    if (info) abrirElemento(info);
  });

  function actualizarFlotante() {
    const info = elementoAnunciado.get(pestanaActiva);
    flotante.hidden = !info;
    if (info) flotante.textContent = `Anotar ${TIPOS[info.tipo]}`;
  }

  // Contrato postMessage: solo del mismo origen y del iframe de una pestaña anotable
  const idsSecciones = new Set(tema.secciones.map((s) => s.id));
  const texto = (v, max) => typeof v === 'string' && v.length <= max;
  addEventListener('message', (e) => {
    if (e.origin !== location.origin) return;
    const p = anotables.find((x) => iframeDe(x.id)?.contentWindow === e.source);
    const d = e.data;
    if (!p || !d || typeof d !== 'object' || !idsSecciones.has(d.seccion)) return;
    if (d.tipo === 'seccion') {
      if (p.id === pestanaActiva) abrirCajon(d.seccion);
    } else if (d.tipo === 'elemento') {
      if (!texto(d.titulo, 200) || !d.titulo.trim() || !(d.clase in TIPOS)) return;
      if (d.estado !== undefined && !texto(d.estado, 40)) return;
      elementoAnunciado.set(p.id, { seccion: d.seccion, titulo: d.titulo.trim(), tipo: d.clase, estado: d.estado || '' });
      actualizarFlotante();
    }
  });

  for (const p of anotables) construirVista(p);

  return {
    cambioPestana(pid) {
      const anotable = anotables.some((p) => p.id === pid);
      pestanaActiva = anotable ? pid : null;
      boton.hidden = !anotable;
      if (anotable) mostrarPestana(pid); else cerrarCajon();
      actualizarFlotante();
    },
  };
}
