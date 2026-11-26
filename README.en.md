# chomsky-godel

*[Versión en español](README.md)*

A personal study programme in **Systems Engineering and Cybersecurity**. It goes from mathematics to
hardware, and from there to systems and security. It also holds the website where its interactive
lessons are published.

The student is Guillermo, with a background in mathematics, who studies with Claude Code on the desktop
(WSL), using three *skills* that act as tutors. The whole repository is the programme's memory: every
session starts cold and reads `estudio/`.

The working language of the repository is Spanish. Only this README and the read-only version of the
site («the museum») are in English.

## The phases

| Phase | Topic | Status |
|---|---|---|
| 0 | **The bridge:** from mathematics to machine logic | Closed |
| 1 | **The naked machine:** CPU, memory, cache, x86-64 Assembly | Closed |
| 2 | **The language of the system:** C, pointers, manual memory, first buffer overflow | In progress |
| 3 | **The operating system:** processes, permissions, syscalls, Linux from the inside | — |
| 4 | **Networks:** OSI and TCP/IP, DNS, HTTP, TLS, Wireshark | — |
| 5 | **Cybersecurity fundamentals:** cryptography, authentication, first CTF | — |
| 6 | **The fork:** offensive or defensive | — |

The full plan, with the exit criteria of each phase, is in
[`estudio/plan-general.md`](estudio/plan-general.md) (Spanish).

## How it is organized

| Folder | What is there |
|---|---|
| [`estudio/`](estudio/README.md) | The programme's memory: profile, plan, progress, session logs, closing reports |
| [`retos/`](retos/README.md) | Work on the phase challenges (Assembly, C…) and their tools (`ensamblar.sh`, `trazar.sh`) |
| `temas/` | The lessons in HTML: Boolean logic, ALU, CPU and Phases 0–2, with their English versions (`*.en.html`) |
| `sitio/` | The website that publishes `temas/`: FastAPI + Firestore on Cloud Run |
| `docs/` | The site's specification and its decision log (`docs/sitio/decisiones.md`) |
| `.claude/skills/` | The tutors: **tutor**, **tutor-maestro** and **escriba** |

## The tutors

- **Tutor:** teaches the class according to the plan, with micro-lessons, micro-tasks and
  challenges. The rule is *predict first, verify afterwards*.
- **Tutor Maestro:** free, high-level conversation with no syllabus. It also writes the
  understanding reports.
- **Escriba (the scribe):** closes every session. It records what was learned in
  `estudio/progreso.md` and in a session log.

## The site

It is a «museum» of what has been done and learned. It is published on Cloud Run and has two
versions:

- **Private:** with login and annotations.
- **Read-only (P-34):** through a secret link, in Spanish and in English (P-35).

**Running it locally:**

```bash
cd sitio && .venv/bin/python -m pytest -q        # tests
sitio/.venv/bin/python sitio/local.py --puerto 8090   # local server (from the repo root)
```

The rules for writing lessons are in [`temas/instrucciones-html.md`](temas/instrucciones-html.md)
(Spanish). They are checked with `sitio/revisar_html.py`. Deployment uses `sitio/desplegar.sh`
(`construir` to build, then `publicar` to publish).

## Privacy

Raw material (`docs/bitacoras-estudio/`, `docs/notas-altas/`) and secrets (`sitio/.env`,
invitations, the museum key) are not versioned.
