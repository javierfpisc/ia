#!/usr/bin/env python3
"""Control de calidad automático de un apartado de contenidos o de una práctica.

Uso: python3 scripts/calidad.py contenidos/unidades/04/03-firewall-netfilter-iptables.md [...]
     python3 scripts/calidad.py contenidos/unidades/04        (todos los .md de la unidad)
     python3 scripts/calidad.py practicas/unidades/04/01-mi-practica.md

Comprueba frente a contenidos/unidades.yml (o practicas/unidades.yml): extensión, diagramas, referencias prohibidas al
material original o a la docencia, URLs no autorizadas, enlaces relativos, encabezados, Mermaid y cobertura de contenidos
mínimos (minimos).
Código de salida 1 si hay errores (los avisos no fallan).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


import yaml
sys.path.insert(0, str(Path(__file__).parent))

os.environ["PATH"] += os.pathsep + str(Path.home() / ".local" / "bin")
# absolute() y no resolve(): scripts/ es un enlace desde cada módulo y RAIZ debe ser el módulo, no materiales/
RAIZ = Path(__file__).absolute().parent.parent
PROHIBIDO = [
    (r"seg[uú]n (el|la|los|las) (documento|fuente|pdf|manual|apuntes|profesor|docente)", "referencia a documento original"),
    (r"documentaci[oó]n (original|aportada|proporcionada)", "referencia a documentación original"),
    (r"\b(el|la) (profesor|profesora|docente)\b", "comentario docente"),
    (r"\b(la|las) fuentes? (indica|dice|afirma|señala|recoge)", "referencia a documento original"),
    (r"\bF\d{2}(#s\d+)?\b", "identificador interno de fuente"),
    (r"(?i)^\s*>?\s*\*{0,2}(estado|fuentes principales|última revisión)\*{0,2}\s*:", "metadatos internos"),
    (r"(?i)referencias a las fuentes|\bborrador\b|laguna", "texto de trabajo interno"),
    (r"(?i)\b(p[aá]g\.|p[aá]gina) \d+|\bpp?\. \d+", "cita de página"),
    (r"\[POR DEFINIR\]", "marcador pendiente"),
]


SECCIONES_PRACTICA = ["procedimiento", "verificación final", "qué debes entregar", "documentación oficial"]


def cargar_meta():
    return {t: yaml.safe_load((RAIZ / t / "unidades.yml").read_text()) for t in ("contenidos", "practicas")}


def tipo_de(ruta):
    return "practicas" if "practicas" in ruta.resolve().relative_to(RAIZ).parts[:1] else "contenidos"


def presupuesto(meta, unidad, ap, tipo):
    cfg = meta["configuracion"]
    u = next(x for x in meta["unidades"] if x["unidad"] == unidad)
    if ap.get("palabras"):
        return ap["palabras"]
    if tipo == "practicas":
        if not ap.get("sesiones"):
            return None
        return round(ap["sesiones"] * cfg["palabras_por_sesion"] * cfg["factor_tipo"].get(ap.get("tipo"), 1.0))
    sesiones = ap.get("sesiones") or u["sesiones"] / len(u["apartados"])
    factor = cfg["factor_profundidad"].get(ap.get("profundidad") or u.get("profundidad") or "descriptivo", 1.0)
    return round(sesiones * cfg["palabras_por_sesion"] * factor)


def revisar(ruta, metas):
    err, avi = [], []
    tipo = tipo_de(ruta)
    meta = metas[tipo]
    clave = "practicas" if tipo == "practicas" else "apartados"
    txt = ruta.read_text()
    unidad = int(ruta.parent.name) if ruta.parent.name.isdigit() else None
    u = next((x for x in meta["unidades"] if x["unidad"] == unidad), None)
    ap = next((a for a in (u or {}).get(clave) or [] if a["id"] == ruta.stem), None)

    sin_codigo = re.sub(r"```.*?```", "", txt, flags=re.S)
    palabras = len(re.findall(r"\w+", sin_codigo))
    n_mermaid = len(re.findall(r"^```mermaid", txt, flags=re.M))
    if ap:
        pres = presupuesto(meta, unidad, ap, tipo)
        tol = meta["configuracion"]["tolerancia"]
        if pres is None:
            avi.append("práctica sin `sesiones` ni `palabras`: sin control de extensión")
        elif not pres * (1 - tol) <= palabras <= pres * (1 + tol):
            avi.append(f"extensión {palabras} palabras fuera de {pres}±{int(tol*100)}%")
        if n_mermaid < ap.get("diagramas", 0):
            avi.append(f"{n_mermaid} diagramas Mermaid, se piden {ap['diagramas']}")

        # Validar minimos
        minimos = ap.get("minimos") or []
        if minimos:
            txt_busqueda = sin_codigo.lower()
            no_encontrados = []
            for minimo in minimos:
                # Buscar si el mínimo se menciona en el documento (búsqueda flexible)
                palabras_clave = re.findall(r"\b\w+\b", minimo.lower())
                encontrado = all(re.search(r"\b" + re.escape(pal) + r"\b", txt_busqueda) for pal in palabras_clave if len(pal) > 3)
                if not encontrado:
                    no_encontrados.append(minimo)
            if no_encontrados:
                for m in no_encontrados:
                    err.append(f"mínimo no cubierto: «{m}»")
    else:
        avi.append(f"no declarado en {tipo}/unidades.yml (sin control de extensión)")
    if tipo == "practicas":
        titulos = [t.strip().lower() for t in re.findall(r"(?m)^#{2,3} (.+)$", txt)]
        for sec in SECCIONES_PRACTICA:
            if not any(t.startswith(sec) for t in titulos):
                avi.append(f"falta la sección «{sec}»")

    tiene_auto = bool(re.search(r"(?m)^## Comprueba lo aprendido", txt))
    if tipo == "contenidos":
        n_auto = (ap or {}).get("autoevaluacion")
        if tiene_auto and not n_auto:
            err.append("«Comprueba lo aprendido» sin `autoevaluacion` en unidades.yml")
        elif n_auto and not tiene_auto:
            err.append(f"falta «Comprueba lo aprendido» ({n_auto} preguntas en unidades.yml)")
        elif n_auto:
            seccion = txt.split("## Comprueba lo aprendido", 1)[1].split("\n## ", 1)[0]
            n = len(re.findall(r"(?m)^\d+\. ", seccion.split("<details>")[0]))
            if n != n_auto:
                avi.append(f"{n} preguntas de autoevaluación, se piden {n_auto}")
    if txt.count("```") % 2:
        err.append("bloques de código sin cerrar")
    niveles = [len(m) for m in re.findall(r"(?m)^(#{1,6}) ", sin_codigo)]
    if niveles.count(1) != 1:
        err.append(f"debe haber un único H1 (hay {niveles.count(1)})")
    if any(b - a > 1 for a, b in zip(niveles, niveles[1:])):
        err.append("salto de nivel en encabezados")

    for i, linea in enumerate(sin_codigo.splitlines(), 1):
        for patron, motivo in PROHIBIDO:
            if re.search(patron, linea, flags=re.I if "(?i)" not in patron else 0):
                err.append(f"texto no apto para alumnado ({motivo}): «{linea.strip()[:70]}»")

    permitidas = set()
    if ap and ap.get("fuentes"):
        from ingesta import cargar_urls
        permitidas = {x["url"].rstrip("/") for x in cargar_urls(RAIZ / ap["fuentes"])}
    for destino in re.findall(r"\]\(([^)\s]+)\)", sin_codigo):
        if destino.startswith("http"):
            if permitidas and destino.split("#")[0].rstrip("/") not in permitidas:
                avi.append(f"URL que no está en fuentes.yaml: {destino}")
        elif not destino.startswith(("#", "mailto:")):
            if not (ruta.parent / destino.split("#")[0]).exists():
                err.append(f"enlace relativo roto: {destino}")

    if shutil.which("mmdc"):
        for k, bloque in enumerate(re.findall(r"```mermaid\n(.*?)```", txt, flags=re.S), 1):
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / "d.mmd").write_text(bloque)
                (Path(d) / "p.json").write_text('{"args":["--no-sandbox"]}')
                r = subprocess.run(["mmdc", "-p", f"{d}/p.json", "-i", f"{d}/d.mmd", "-o", f"{d}/d.svg"],
                                   capture_output=True, text=True)
                if r.returncode:
                    err.append(f"diagrama Mermaid {k} inválido")
    elif n_mermaid:
        avi.append("mmdc no disponible: Mermaid sin validar")
    return err, avi, palabras, n_mermaid


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    metas, fallos = cargar_meta(), 0
    ficheros = []
    for a in sys.argv[1:]:
        p = Path(a)
        ficheros += sorted(x for x in p.rglob("*.md") if x.name != "index.md" and "registro" not in x.name) if p.is_dir() else [p]
    for f in ficheros:
        err, avi, pal, mer = revisar(f, metas)
        print(f"\n{f} — {pal} palabras, {mer} diagramas")
        for e in err:
            print(f"  ERROR  {e}")
        for a in avi:
            print(f"  AVISO  {a}")
        if not err and not avi:
            print("  OK")
        fallos += bool(err)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
