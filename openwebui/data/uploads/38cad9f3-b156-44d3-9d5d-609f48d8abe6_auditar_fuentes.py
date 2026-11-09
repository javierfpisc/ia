#!/usr/bin/env python3
"""Audita las URLs de un fuentes.yaml: estado de descarga y cantidad de texto útil.

Uso: python3 scripts/auditar_fuentes.py documentacion/unidad4-redes-seguras [--min-palabras 400] [--conservar TEXTO ...] [--podar]
Informa de cada URL (OK / POCO TEXTO / ERROR). Con --podar elimina de fuentes.yaml los bloques
no válidos, guardando antes una copia fuentes.yaml.bak.
"""
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ingesta import cargar_urls, descargar  # noqa: E402


def evaluar(u, minimo):
    try:
        palabras = len(descargar(u["url"]).split())
    except Exception as e:
        return u, "ERROR", str(e)[:60]
    return u, ("OK" if palabras >= minimo else "POCO TEXTO"), f"{palabras} palabras"


def main():
    args = [a for a in sys.argv[1:2]]
    minimo = int(sys.argv[sys.argv.index("--min-palabras") + 1]) if "--min-palabras" in sys.argv else 400
    conservar = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--conservar"]
    carpeta = Path(args[0])
    fichero = carpeta / "fuentes.yaml"
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda u: evaluar(u, minimo), cargar_urls(carpeta)))
    malas = []
    for u, estado, det in res:
        print(f"{estado:10} {det:28} {u['url']}")
        if estado == "POCO TEXTO" and any(c in u["url"] for c in conservar):
            continue
        if estado != "OK":
            malas.append(u["url"])
    print(f"\n{len(res) - len(malas)} válidas, {len(malas)} descartables")
    if "--podar" in sys.argv and malas:
        shutil.copy(fichero, fichero.with_suffix(fichero.suffix + ".bak"))
        bloques = re.split(r"(?m)^(?=- )", fichero.read_text())
        mantener = [b for b in bloques if not any(re.search(rf"url:\s*{re.escape(m)}\s*$", b, re.M) for m in malas)]
        fichero.write_text("".join(mantener))
        print(f"Eliminadas {len(bloques) - len(mantener)} entradas de {fichero}")


if __name__ == "__main__":
    main()
