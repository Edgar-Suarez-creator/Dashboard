"""Actualiza SOLO los datos (const DATA) del dashboard de Control de Dossieres · Exteriores con la BD del buzón.
Usa la misma extracción de build_dashboard.py + los ajustes de mapeo de Propuesta_v2/build_v3.py.
Uso: python update_ext.py "ruta\\BD GENERAL ... .xlsb" [--write]"""
import os, sys, json, re, shutil, tempfile, datetime, collections
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
XLSB = sys.argv[1]; WRITE = "--write" in sys.argv
HTML = os.path.join(HERE, "Ejecutable", "Dashboard_Control_Dossiers.html")
shadow = os.path.join(tempfile.gettempdir(), "_BD_shadow_ext.xlsb"); shutil.copyfile(XLSB, shadow)

# código de build_v3.py con las rutas actuales (la carpeta se movió a Exteriores\)
b3 = open(os.path.join(HERE, "Propuesta_v2", "build_v3.py"), encoding="utf-8").read()
b3 = b3[:b3.index("# ---------- v3: solo datos")]
b3 = b3.replace('BASE = r"C:\\Users\\edgar.suarez\\Dashboard\\Control_Dossiers_AC1-HC1"', f'BASE = r"{HERE}"')
b3 = b3.replace('SRC_XLSB = os.path.join(BASE, "BD GENERAL - CSE - PAD2 Y EXTERIORES (OFICIAL).xlsb")', f'SRC_XLSB = r"{XLSB}"')
b3 = b3.replace('shadow = os.path.join(tempfile.gettempdir(), "_BD_shadow_v2.xlsb")', f'shadow = r"{shadow}"')
g = {}
exec(compile(b3, "build_v3_cfg", "exec"), g)
src = g["src"]
g2 = {}
exec(compile(src[:src.index('HTML = r"""')], "build_data", "exec"), g2)
new = json.loads(g2["payload"])
# columnas de fecha con texto (p. ej. "NO EXISTE HC1"): la fecha queda vacía y el texto pasa a comentarios
FECHAS = {"hc1": ["f_arranque", "f_prog_hc1", "firma_ops", "fecha_envio_cit", "fecha_aprob_cit"], "ac1": ["fecha_programada", "fecha_cierre_sc"]}
NOTA = {"hc1": "comentarios_hc1", "ac1": "observaciones"}
movidos = collections.Counter()
for k, cols in FECHAS.items():
    for r in new[k]:
        for c in cols:
            v = r.get(c) or ""
            if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(v)):
                r[NOTA[k]] = (f"{c.replace('_', ' ')}: {v}" + (" · " + r[NOTA[k]] if r.get(NOTA[k]) else ""))
                r[c] = ""; movidos[(k, c, str(v))] += 1
print("textos en columnas de fecha:", dict(movidos))
# pendientes tipo A / tipo B por HC1 (hoja PEND POWER BI INTERFACE)
sys.path.insert(0, HERE); import pend_ab
print("pendientes tipo A/B:", pend_ab.agregar(shadow, new))

h = open(HTML, encoding="utf-8").read()
i = h.index("const DATA = ") + len("const DATA = ")
old, end = json.JSONDecoder().raw_decode(h[i:])
print("antes:", old["today"], "hc1", len(old["hc1"]), "ac1", len(old["ac1"]))
print("ahora:", new["today"], "hc1", len(new["hc1"]), "ac1", len(new["ac1"]))
ko = set(old["hc1"][0]); kn = set(new["hc1"][0]); print("campos hc1 iguales:", ko == kn, ko ^ kn)
ko = set(old["ac1"][0]); kn = set(new["ac1"][0]); print("campos ac1 iguales:", ko == kn, ko ^ kn)
import collections
for k, L in (("hc1", "e_entrega"), ("ac1", "estatus")):
    print(f"  {k}.{L} antes:", collections.Counter(r.get(L) for r in old[k]).most_common(6))
    print(f"  {k}.{L} ahora:", collections.Counter(r.get(L) for r in new[k]).most_common(6))
out = h[:i] + json.dumps(new, ensure_ascii=False, separators=(",", ":")) + h[i + end:]
if WRITE:
    shutil.copy2(HTML, HTML + ".bak_before_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    open(HTML, "w", encoding="utf-8").write(out); print("ESCRITO", HTML)
