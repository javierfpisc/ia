#!/usr/bin/env python3
"""Convierte las fuentes de una unidad o apartado en texto troceado para ahorrar contexto.

Uso: python3 scripts/ingesta.py documentacion/unidad4-redes-seguras [APARTADO_O_PRACTICA_ID] [--sin-red] [--refrescar]

Entrada : <carpeta>/fuentes.yaml (lista de {fuente, descripcion, url}) y
          archivos pdf/odt/docx/epub/md/txt/html de la carpeta.
          Con un id solo se usan las URLs que contienen alguno de los textos del campo `urls`
          de ese apartado (contenidos/unidades.yml) o práctica (practicas/unidades.yml), y los
          documentos locales cuya ruta contiene alguno de los textos de su campo `documentos`.
Salida  : trabajo/<carpeta>/<ID|_todo>/{extracto.md, indice.md, manifiesto.json}
Caché   : trabajo/_cache/ (--refrescar fuerza nueva descarga)
Usa la biblioteca estándar, PyYAML y las herramientas del sistema (pdftotext; pandoc si existe).
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path

os.environ["PATH"] += os.pathsep + str(Path.home() / ".local" / "bin")
# absolute() y no resolve(): scripts/ es un enlace desde cada módulo y RAIZ debe ser el módulo, no materiales/
RAIZ = Path(__file__).absolute().parent.parent
EXT_LOCALES = {".pdf", ".odt", ".docx", ".epub", ".md", ".txt", ".html"}
PALABRAS_TROZO_MAX = 1000


class HtmlAMd(HTMLParser):
    IGNORAR = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self.out, self.skip, self.pre = [], 0, False

    def handle_starttag(self, t, a):
        if t in self.IGNORAR:
            self.skip += 1
        elif self.skip:
            return
        elif re.fullmatch(r"h[1-6]", t):
            self.out.append("\n\n" + "#" * int(t[1]) + " ")
        elif t == "li":
            self.out.append("\n- ")
        elif t == "pre":
            self.pre = True
            self.out.append("\n\n```\n")
        elif t == "code" and not self.pre:
            self.out.append("`")
        elif t in {"p", "div", "tr", "br", "table", "ul", "ol"}:
            self.out.append("\n")

    def handle_endtag(self, t):
        if t in self.IGNORAR:
            self.skip = max(0, self.skip - 1)
        elif self.skip:
            return
        elif t == "pre":
            self.pre = False
            self.out.append("\n```\n")
        elif t == "code" and not self.pre:
            self.out.append("`")
        elif t in {"td", "th"}:
            self.out.append(" | ")
        elif re.fullmatch(r"h[1-6]|p", t):
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d if self.pre else re.sub(r"\s+", " ", d))


def limpiar(txt):
    txt = txt.replace("\r", "").replace("\u00ad", "")
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def html_a_md(html):
    p = HtmlAMd()
    p.feed(html)
    return limpiar("".join(p.out))


def xml_a_texto(xml):
    xml = re.sub(r"</(w:p|text:p|text:h)>", "\n", xml)
    return limpiar(re.sub(r"<[^>]+>", "", xml))


def leer_local(ruta):
    """Devuelve (texto, modo) con modo 'paginas' (PDF) o 'texto'."""
    ext = ruta.suffix.lower()
    if ext in {".md", ".txt"}:
        return ruta.read_text(errors="replace"), "texto"
    if ext == ".html":
        return html_a_md(ruta.read_text(errors="replace")), "texto"
    if ext == ".pdf":
        r = subprocess.run(["pdftotext", "-layout", str(ruta), "-"], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr.strip())
        return r.stdout, "paginas"
    if shutil.which("pandoc"):
        r = subprocess.run(["pandoc", str(ruta), "-t", "gfm", "--wrap=none"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout, "texto"
    with zipfile.ZipFile(ruta) as z:
        if ext == ".odt":
            return xml_a_texto(z.read("content.xml").decode()), "texto"
        if ext == ".docx":
            return xml_a_texto(z.read("word/document.xml").decode()), "texto"
        if ext == ".epub":
            partes = [n for n in sorted(z.namelist()) if n.endswith((".xhtml", ".html"))]
            return "\n\n".join(html_a_md(z.read(n).decode(errors="replace")) for n in partes), "texto"
    raise RuntimeError("formato no soportado")


def descargar(url, refrescar=False):
    cache = RAIZ / "trabajo" / "_cache" / (hashlib.sha1(url.encode()).hexdigest() + ".md")
    if cache.exists() and not refrescar:
        return cache.read_text()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (materiales-brs-ingesta)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        cuerpo = r.read().decode(r.headers.get_content_charset() or "utf-8", errors="replace")
        ctype = r.headers.get_content_type()
    txt = cuerpo if ctype in {"text/markdown", "text/plain"} else html_a_md(cuerpo)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(txt)
    return txt


def huella(txt):
    return hashlib.sha256(re.sub(r"\s+", " ", txt).encode()).hexdigest()[:16]


def trocear(txt, modo):
    """Devuelve [(etiqueta, texto)] dividiendo por páginas (PDF) o por encabezados."""
    if modo == "paginas":
        trozos, buf, ini = [], [], 1
        pags = txt.split("\f")
        for i, p in enumerate(pags, 1):
            p = limpiar(p)
            if p:
                buf.append(p)
            if buf and sum(len(b.split()) for b in buf) >= 350:
                trozos.append((f"pp. {ini}-{i}" if i > ini else f"p. {i}", "\n\n".join(buf)))
                buf, ini = [], i + 1
        if buf:
            trozos.append((f"pp. {ini}-{len(pags)}", "\n\n".join(buf)))
        return trozos
    trozos = []
    for p in re.split(r"(?m)^(?=#{1,4} )", txt):
        p = p.strip()
        if not p:
            continue
        m = re.match(r"#{1,4} (.+)", p)
        titulo = m.group(1).strip() if m else "(inicio)"
        lineas, acum, n = p.split("\n"), [], 0
        for ln in lineas:
            acum.append(ln)
            n += len(ln.split())
            if n >= PALABRAS_TROZO_MAX:
                trozos.append((titulo, "\n".join(acum)))
                acum, n = [], 0
        if acum:
            trozos.append((titulo, "\n".join(acum)))
    return trozos


def cargar_urls(area):
    import yaml
    fichero = area / "fuentes.yaml"
    if not fichero.exists():
        return []
    return [{"url": u["url"], "titulo": u.get("fuente") or u["url"]} for u in yaml.safe_load(fichero.read_text()) or []]


def buscar_apartado(apartado):
    import yaml
    for tipo, clave in (("contenidos", "apartados"), ("practicas", "practicas")):
        meta = yaml.safe_load((RAIZ / tipo / "unidades.yml").read_text())
        for u in meta["unidades"]:
            for ap in u.get(clave) or []:
                if ap["id"] == apartado:
                    return ap
    sys.exit(f"Apartado o práctica {apartado} no encontrado en contenidos/unidades.yml ni en practicas/unidades.yml")


def filtrar_apartado(urls, ap):
    pats = ap.get("urls") or []
    return [x for x in urls if any(p in x["url"] for p in pats)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sin_red, refrescar = "--sin-red" in sys.argv, "--refrescar" in sys.argv
    if not 1 <= len(args) <= 2:
        sys.exit(__doc__)
    area = Path(args[0]).resolve()
    apartado = args[1] if len(args) == 2 else None
    if not area.is_dir():
        sys.exit(f"No existe {area}")
    rel = area.relative_to(RAIZ / "documentacion")
    salida = RAIZ / "trabajo" / rel / (apartado or "_todo")
    salida.mkdir(parents=True, exist_ok=True)

    urls = cargar_urls(area)
    ap = buscar_apartado(apartado) if apartado else None
    if ap:
        urls = filtrar_apartado(urls, ap)

    fuentes, n = [], 0
    for u in urls:
        n += 1
        fid = f"F{n:02d}"
        if sin_red:
            print(f"{fid} omitida (--sin-red): {u['url']}")
            continue
        try:
            fuentes.append((fid, "url", u["url"], u["titulo"], descargar(u["url"], refrescar), "texto"))
        except Exception as e:
            print(f"{fid} ERROR descargando {u['url']}: {e}")
    for f in sorted(area.rglob("*")):
        if f.is_file() and f.suffix.lower() in EXT_LOCALES and (not ap or any(d in str(f.relative_to(area)) for d in ap.get("documentos") or [])):
            n += 1
            try:
                txt, modo = leer_local(f)
                fuentes.append((f"F{n:02d}", "local", str(f.relative_to(area)), f.name, txt, modo))
            except Exception as e:
                print(f"F{n:02d} ERROR leyendo {f.name}: {e}")

    extracto, indice, manifiesto = [], [], []
    for fid, tipo, ref, titulo, txt, modo in fuentes:
        trozos = trocear(txt, modo)
        total = sum(len(t.split()) for _, t in trozos)
        manifiesto.append({"id": fid, "tipo": tipo, "ref": ref, "huella": huella(txt), "palabras": total,
                           "fecha": datetime.date.today().isoformat()})
        etiqueta = "URL oficial (prioridad 1)" if tipo == "url" else "Documento local (prioridad 2)"
        indice.append(f"\n## {fid} · {etiqueta} · {titulo}\n`{ref}` · {total} palabras\n")
        indice.append("| Trozo | Contenido | Palabras |\n|---|---|---|")
        for i, (t, tx) in enumerate(trozos, 1):
            marca = f"{fid}#s{i:02d}"
            extracto.append(f"<!-- {marca} | {titulo} | {t} -->\n{tx}\n")
            indice.append(f"| {marca} | {t[:80]} | {len(tx.split())} |")
    (salida / "extracto.md").write_text("\n".join(extracto))
    (salida / "indice.md").write_text(f"# Índice de fuentes — {rel}\n" + "\n".join(indice) + "\n")
    (salida / "manifiesto.json").write_text(json.dumps(manifiesto, indent=1, ensure_ascii=False))
    print(f"{len(fuentes)} fuentes, {sum(m['palabras'] for m in manifiesto)} palabras -> {salida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
