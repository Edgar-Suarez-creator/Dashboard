"""Pendientes abiertos tipo A / tipo B por HC1 (sistema) desde la hoja 'PEND POWER BI INTERFACE ' de la BD GENERAL.
Agrega a cada registro hc1: pa, pb (totales) y pa_civ/pa_ele/pa_ins/pa_mec, pb_civ/pb_ele/pb_ins/pb_mec."""
import collections
from pyxlsb import open_workbook

SHEET = "PEND POWER BI INTERFACE "
DISC = {"CIVIL": "civ", "ELEC": "ele", "INST": "ins", "MECH-EST": "mec", "MECH": "mec"}
KEYS = ["pa", "pb"] + [f"{t}_{d}" for t in ("pa", "pb") for d in ("civ", "ele", "ins", "mec")]


def conteo(xlsb):
    """{sistema: Counter(campo -> pendientes abiertos)}"""
    out = collections.defaultdict(collections.Counter)
    with open_workbook(xlsb) as wb:
        name = SHEET if SHEET in wb.sheets else next(s for s in wb.sheets if s.strip() == SHEET.strip())
        with wb.get_sheet(name) as s:
            H = None
            for row in s.rows():
                v = [c.v for c in row]
                if H is None:
                    H = [str(x or "").strip() for x in v]; ix = {h: i for i, h in enumerate(H)}; continue
                g = lambda k: v[ix[k]] if ix[k] < len(v) else None
                if str(g("ESTATUS") or "").strip().upper() != "ABIERTO":
                    continue
                cat = str(g("CATEGORIA") or "").strip().upper()
                if cat not in ("A", "B"):
                    continue
                t = "pa" if cat == "A" else "pb"
                d = DISC.get(str(g("DISCIPLINA") or "").strip().upper(), "mec")
                c = out[str(g("SISTEMA") or "").strip()]
                c[t] += 1; c[f"{t}_{d}"] += 1
    return out


def agregar(xlsb, data):
    cnt = conteo(xlsb)
    for r in data["hc1"]:
        c = cnt.get(str(r.get("sistema") or "").strip(), {})
        for k in KEYS:
            r[k] = int(c.get(k, 0))
    tot = sum(sum(c[k] for k in ("pa", "pb")) for c in cnt.values())
    asign = sum(r["pa"] + r["pb"] for r in data["hc1"])
    return {"abiertos_hoja": tot, "asignados_hc1": asign,
            "tipo_a": sum(r["pa"] for r in data["hc1"]), "tipo_b": sum(r["pb"] for r in data["hc1"])}
