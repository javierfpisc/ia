#!/usr/bin/env python3
"""Prepara y, solo con autorización explícita, publica contenidos y prácticas en los repositorios de publicacion/repositorios.yml.

Uso: python3 scripts/publicar.py 01 02          # prepara: valida y genera trabajo/publicacion/NN/stage (sin red ni git)
     python3 scripts/publicar.py todas          # prepara todas las unidades declaradas
     python3 scripts/publicar.py 01 --publicar  # clona, sincroniza, confirma y sube. SOLO con autorización explícita del profesor

Opciones:
  --publicar      realiza commit y push en el repositorio de la unidad (por defecto solo prepara)
  --rama NOMBRE   rama destino si repositorios.yml no define `rama` para la unidad
  --origen RUTA   repositorio local en lugar de GitHub (solo pruebas)

GitHub se usa por SSH (git@github.com:<organización>/<repositorio>.git), con la clave SSH del sistema.
Si la rama no existe o no hay acceso, el script se detiene. Como SSH no permite comprobar la visibilidad,
el script avisa de que el profesor debe verificar que el repositorio es privado.

Publica:
  - guia, introduccion y entorno de la unidad en sus rutas `docs/...` (repositorios.yml);
  - los .md de contenidos/unidades/NN/ en <conceptos.directorio>/;
  - los .md de practicas/unidades/NN/ en <practicas.directorio>/;
  - publicacion/mkdocs.yml completado, con el nav generado a partir de los archivos publicados.
Se detiene ante errores, posibles secretos, rama inexistente o cambios inesperados en el destino.
Código de salida 1 si hay errores.
"""
import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

# absolute() y no resolve(): scripts/ es un enlace desde cada módulo y RAIZ debe ser el módulo, no materiales/
RAIZ = Path(__file__).absolute().parent.parent
CONFIG = RAIZ / "publicacion" / "repositorios.yml"
PLANTILLA = RAIZ / "publicacion" / "mkdocs.yml"
TRABAJO = RAIZ / "trabajo" / "publicacion"
CLAVES_ESPECIALES = ("guia", "introduccion", "entorno")
SECRETOS = [
    (r"gh[pousr]_[A-Za-z0-9]{20,}", "token de GitHub"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "clave privada"),
    (r"(?i)\b(password|passwd|contraseña|token|secret|api[_-]?key)\b\s*[:=]\s*\S+", "posible credencial"),
]


class ErrorPublicacion(Exception):
    pass


def orden(ruta):
    m = re.match(r"(\d+)", ruta.name)
    return (int(m.group(1)) if m else 999, ruta.name)


def cargar_config():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    meta = yaml.safe_load((RAIZ / "contenidos" / "unidades.yml").read_text(encoding="utf-8"))
    titulos = {u["unidad"]: u["titulo"] for u in meta["unidades"]}
    return cfg["github"]["organizacion"], cfg["unidades"], titulos


def dirs_unidad(n):
    return (RAIZ / "contenidos" / "unidades" / f"{n:02d}", RAIZ / "practicas" / "unidades" / f"{n:02d}")


def rutas_unidad(n, u):
    """Devuelve [(origen, destino)]; el destino es relativo a la raíz del repositorio de publicación."""
    dir_c, dir_p = dirs_unidad(n)
    especiales = [(dir_c / Path(u[c]).name, u[c]) for c in CLAVES_ESPECIALES if u.get(c)]
    nombres_especiales = {o.name for o, _ in especiales}
    pares = list(especiales)
    pares += [(RAIZ / "publicacion" / a, a) for a in u.get("archivos", [])]
    dir_conc = u["conceptos"]["directorio"]
    pares += [(f, f"{dir_conc}/{f.name}") for f in sorted(dir_c.glob("*.md"), key=orden)
              if f.name not in nombres_especiales]
    if u.get("practicas"):
        dir_prac = u["practicas"]["directorio"]
        pares += [(f, f"{dir_prac}/{f.name}") for f in sorted(dir_p.glob("*.md"), key=orden)]
    return pares


def titulo_md(ruta):
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return ruta.stem

def validar(n, u, aceptar_credenciales=False):
    errores, avisos = [], []
    for clave in ("repositorio", "mkdocs"):
        if not u.get(clave):
            errores.append(f"falta `{clave}` en publicacion/repositorios.yml")
    if u.get("mkdocs"):
        ruta_mk = posixpath.normpath(u["mkdocs"])
        if posixpath.isabs(ruta_mk) or ruta_mk.startswith("..") or not ruta_mk.endswith(".yml"):
            errores.append(f"`mkdocs` debe ser una ruta relativa a un .yml dentro del repositorio: {u['mkdocs']}")
    for clave in ("conceptos", "practicas"):
        if clave == "practicas" and not u.get(clave):
            continue
        if not (u.get(clave) or {}).get("directorio"):
            errores.append(f"falta `{clave}.directorio` en publicacion/repositorios.yml")
    if errores:
        return errores, avisos
    dir_c, dir_p = dirs_unidad(n)
    dirs_a_comprobar = [dir_c] + ([dir_p] if u.get("practicas") else [])
    for d in dirs_a_comprobar:
        if not d.is_dir():
            errores.append(f"no existe {d.relative_to(RAIZ)}")
    if errores:
        return errores, avisos
    docs = posixpath.join(posixpath.dirname(posixpath.normpath(u["mkdocs"])), "docs") + "/"
    for a in u.get("archivos", []):
        if not (RAIZ / "publicacion" / a).is_file():
            errores.append(f"no existe publicacion/{a} (declarado en `archivos`)")
    if errores:
        return errores, avisos
    rutas_destino = [u[c] for c in CLAVES_ESPECIALES if u.get(c)] + [u["conceptos"]["directorio"]]
    if u.get("practicas"):
        rutas_destino.append(u["practicas"]["directorio"])
    for ruta in rutas_destino:
        if not posixpath.normpath(ruta).startswith(docs):
            errores.append(f"'{ruta}' debe estar dentro de '{docs}' (docs_dir de `mkdocs: {u['mkdocs']}`)")
    if errores:
        return errores, avisos
    for c in [x for x in CLAVES_ESPECIALES if u.get(x)]:
        if not (dir_c / Path(u[c]).name).is_file():
            errores.append(f"no existe {(dir_c / Path(u[c]).name).relative_to(RAIZ)} (sección `{c}`)")
    if not any(dir_c.glob("*.md")):
        errores.append(f"no hay .md en {dir_c.relative_to(RAIZ)}")
    if u.get("practicas") and not any(dir_p.glob("*.md")):
        errores.append(f"no hay .md en {dir_p.relative_to(RAIZ)}")
    if errores:
        return errores, avisos
    for origen, _ in rutas_unidad(n, u):
        texto = origen.read_text(encoding="utf-8")
        for patron, motivo in SECRETOS:
            if re.search(patron, texto):
                msg = f"{origen.relative_to(RAIZ)}: {motivo} detectado"
                if aceptar_credenciales:
                    avisos.append(f"{msg} (ACEPTADO con --aceptar-credenciales por autorización del profesor)")
                else:
                    errores.append(f"{msg}; revisar antes de publicar")
    no_md = sorted(f.name for d in dirs_a_comprobar for f in d.iterdir() if f.is_file() and f.suffix != ".md")
    if no_md:
        avisos.append(f"archivos que no se publican (no son .md): {', '.join(no_md)}")
    if not u.get("rama"):
        avisos.append("sin `rama` en repositorios.yml: obligatoria para --publicar (o usar --rama)")
    return errores, avisos


def generar_mkdocs(n, u, org, titulo, pares):
    # MkDocs resuelve el nav desde docs_dir = <carpeta de mkdocs.yml>/docs
    base = posixpath.join(posixpath.dirname(u["mkdocs"]), "docs")

    def ruta_nav(destino):
        return posixpath.relpath(destino, base)

    def entradas(prefijo):
        return [{titulo_md(o): ruta_nav(d)} for o, d in pares if d.startswith(prefijo)]

    nav = [{etiqueta: ruta_nav(u[clave])}
           for clave, etiqueta in (("guia", "Guía de Unidad"), ("introduccion", "Inicio"), ("entorno", "Entorno"))
           if u.get(clave)]
    conceptos = entradas(u["conceptos"]["directorio"] + "/")
    practicas = entradas(u["practicas"]["directorio"] + "/") if u.get("practicas") else []
    if conceptos:
        nav.append({"Documentación": conceptos})
    if practicas:
        nav.append({"Prácticas": practicas})

    texto = PLANTILLA.read_text(encoding="utf-8")
    texto = re.sub(r"^site_name:.*$", "site_name: " + json.dumps(f"Unidad {n} · {titulo}", ensure_ascii=False),
                   texto, count=1, flags=re.M)
    texto = re.sub(r"^site_description:.*$",
                   "site_description: " + json.dumps(f"Documentación de la unidad {n} · {titulo}", ensure_ascii=False),
                   texto, count=1, flags=re.M)
    texto = texto.replace("<AQUÍ VA EL ENLACE AL REPOSITORIO DE GITHUB>", f"https://github.com/{org}/{u['repositorio']}")
    cabecera, _, resto = texto.partition("\nnav:")
    _, _, pie = resto.partition("\nplugins:")
    bloque = yaml.safe_dump({"nav": nav}, allow_unicode=True, sort_keys=False, width=1000)
    resultado = cabecera + "\n" + bloque + "\nplugins:" + pie
    if "<AQUÍ" in resultado:
        raise ErrorPublicacion("la plantilla publicacion/mkdocs.yml no se ha completado por completo")
    return resultado


def preparar(n, u, org, titulo):
    pares = rutas_unidad(n, u)
    stage = TRABAJO / f"{n:02d}" / "stage"
    if stage.exists():
        shutil.rmtree(stage)
    for origen, destino in pares:
        destino_ruta = stage / destino
        destino_ruta.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino_ruta)
    ruta_mk = stage / u["mkdocs"]
    ruta_mk.parent.mkdir(parents=True, exist_ok=True)
    ruta_mk.write_text(generar_mkdocs(n, u, org, titulo, pares), encoding="utf-8")
    return stage, pares


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorPublicacion(f"git {args[0]} falló: {(r.stderr or r.stdout).strip()}")
    return r.stdout.strip()


def comprobar_rama_ssh(url, rama):
    """Comprueba por SSH que la rama existe y que hay acceso al repositorio."""
    if not shutil.which("ssh") or not shutil.which("git"):
        raise ErrorPublicacion("git y ssh deben estar instalados para publicar")
    ls = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", url, rama], capture_output=True, text=True)
    if ls.returncode == 2:
        raise ErrorPublicacion(f"la rama '{rama}' no existe en {url}")
    if ls.returncode != 0:
        raise ErrorPublicacion(f"no se pudo acceder a {url} por SSH (clave SSH autorizada en la organización): "
                               f"{ls.stderr.strip()}")


def publicar(n, u, org, stage, pares, rama, origen):
    repo = u["repositorio"]
    url = origen or f"git@github.com:{org}/{repo}.git"
    conc = u["conceptos"]["directorio"]
    prac = (u.get("practicas") or {}).get("directorio")
    especiales = {u[c] for c in CLAVES_ESPECIALES if u.get(c)} | set(u.get("archivos", []))

    def gestionado(ruta):
        return ruta == u["mkdocs"] or ruta in especiales or ruta.startswith(tuple(d + "/" for d in (conc, prac) if d))

    clon = TRABAJO / f"{n:02d}" / "clon"
    if clon.exists():
        shutil.rmtree(clon)
    if origen:
        print(f"AVISO: --origen es solo para pruebas locales ({origen})")
    else:
        print(f"AVISO: no se puede verificar desde aquí que {org}/{repo} sea privado; "
              "compruébalo en GitHub antes de publicar (publicacion/instrucciones.txt)")
    comprobar_rama_ssh(url, rama)
    git("clone", "--quiet", "--branch", rama, "--single-branch", url, str(clon))

    for d in [x for x in (conc, prac) if x]:
        if (clon / d).is_dir():
            for f in (clon / d).glob("*.md"):
                f.unlink()
    for origen_f, destino in pares:
        (clon / destino).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen_f, clon / destino)
    (clon / u["mkdocs"]).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(stage / u["mkdocs"], clon / u["mkdocs"])
    for a in u.get("archivos", []):
        shutil.copy2(RAIZ / "publicacion" / a, clon / a)

    git("add", "-A", cwd=clon)
    cambios = git("status", "--porcelain", cwd=clon).splitlines()
    inesperados = [linea for linea in cambios if not gestionado(linea[3:].strip())]
    if inesperados:
        git("reset", "--quiet", cwd=clon)
        raise ErrorPublicacion("cambios inesperados fuera de las rutas gestionadas (no se ha confirmado nada):\n"
                               + "\n".join(inesperados))
    if not cambios:
        return f"sin cambios: {url} (rama {rama}) ya contiene esta versión"

    print("Cambios a publicar:")
    print("\n".join(cambios))
    git("commit", "--quiet", "-m", f"Publica unidad {n:02d}: contenidos y prácticas", cwd=clon)
    git("push", "--quiet", "origin", rama, cwd=clon)
    commit = git("rev-parse", "--short", "HEAD", cwd=clon)
    destino = origen or f"github.com/{org}/{repo}"
    return f"publicado en {destino} (rama {rama}), commit {commit}"


def main():
    ap = argparse.ArgumentParser(description="Prepara y, con autorización explícita, publica contenidos y prácticas.")
    ap.add_argument("unidades", nargs="+", help="números de unidad (p. ej. 01 02) o 'todas'")
    ap.add_argument("--publicar", action="store_true",
                    help="realiza commit y push (requiere autorización explícita del profesor)")
    ap.add_argument("--rama", help="rama destino si repositorios.yml no la define")
    ap.add_argument("--origen", help="repositorio local en lugar de GitHub (solo pruebas)")
    ap.add_argument("--aceptar-credenciales", action="store_true",
                    help="permite publicar aunque haya credenciales en claro (solo con autorización expresa del profesor)")
    args = ap.parse_args()

    org, unidades, titulos = cargar_config()
    for p in sorted((RAIZ / "contenidos" / "unidades").iterdir()):
        if p.is_dir() and p.name.isdigit() and int(p.name) not in unidades:
            print(f"AVISO: contenidos/unidades/{p.name} no está en repositorios.yml: no se publica")

    ids = sorted(unidades) if args.unidades == ["todas"] else [int(x) for x in args.unidades]
    desconocidas = [i for i in ids if i not in unidades]
    if desconocidas:
        print(f"ERROR: unidades no declaradas en repositorios.yml: {desconocidas}")
        sys.exit(1)

    codigo = 0
    for n in ids:
        u = unidades[n]
        print(f"\n=== Unidad {n:02d} → {u.get('repositorio')} ===")
        errores, avisos = validar(n, u, args.aceptar_credenciales)
        for e in errores:
            print("ERROR:", e)
        for a in avisos:
            print("AVISO:", a)
        if errores:
            codigo = 1
            continue
        try:
            stage, pares = preparar(n, u, org, titulos.get(n, ""))
        except ErrorPublicacion as e:
            print("ERROR:", e)
            codigo = 1
            continue
        print(f"Preparado en {stage.relative_to(RAIZ)} con {len(pares)} archivos:")
        for origen, destino in pares:
            print(f"  {origen.relative_to(RAIZ)} → {destino}")
        if not args.publicar:
            continue
        rama = args.rama or u.get("rama")
        if not rama:
            print("NO PUBLICADO: no hay rama destino (definir `rama` en repositorios.yml o usar --rama)")
            codigo = 1
            break
        try:
            print("RESULTADO:", publicar(n, u, org, stage, pares, rama, args.origen))
        except ErrorPublicacion as e:
            print("NO PUBLICADO:", e)
            codigo = 1
            break
    sys.exit(codigo)


if __name__ == "__main__":
    main()
