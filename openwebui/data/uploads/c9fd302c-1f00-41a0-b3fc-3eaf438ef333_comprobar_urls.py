#!/usr/bin/env python3
"""Detecta URLs oficiales caídas o con contenido modificado desde la última ingesta.

Uso: python3 scripts/comprobar_urls.py [documentacion/unidad4-redes-seguras ...]
Sin argumentos revisa todos los manifiestos de trabajo/. Descarga siempre de nuevo (ignora la caché).
Un cambio de huella indica que los apartados que usan esa fuente deben revisarse.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ingesta import RAIZ, descargar, huella  # noqa: E402


def main():
    if len(sys.argv) > 1:
        manifiestos = []
        for a in sys.argv[1:]:
            base = RAIZ / "trabajo" / Path(a).resolve().relative_to(RAIZ / "documentacion")
            manifiestos += sorted(base.rglob("manifiesto.json"))
    else:
        manifiestos = sorted((RAIZ / "trabajo").rglob("manifiesto.json"))
    problemas, vistas = 0, {}
    for mf in manifiestos:
        for f in json.loads(mf.read_text()):
            if f["tipo"] != "url":
                continue
            if f["ref"] not in vistas:
                try:
                    vistas[f["ref"]] = "OK" if huella(descargar(f["ref"], refrescar=True)) == f["huella"] else "CAMBIADA"
                except Exception as e:
                    vistas[f["ref"]] = f"ERROR ({e})"
            estado = vistas[f["ref"]]
            if estado != "OK":
                problemas += 1
            print(f"{estado:10} {mf.parent.relative_to(RAIZ / 'trabajo')}  {f['id']}  {f['ref']}")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
