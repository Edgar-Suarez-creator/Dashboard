"""Genera el HTML de Facilidades/Estaciones con la plantilla v3 de Exteriores (sin tocar la de Exteriores)."""
import os, sys, json, re, collections, shutil, tempfile
sys.stdout.reconfigure(encoding="utf-8")
from pyxlsb import open_workbook
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "Exteriores", "Propuesta_v2", "template_v3.html")
OUT = os.path.join(HERE, "Ejecutable", "Dashboard_Control_Dossiers_Facilidades.html")
data = json.load(open(os.path.join(HERE, "data_fac.json"), encoding="utf-8"))
# ---- completar subproyecto / etapa con la hoja LISTA SISTEMAS Y SUBSISTEMAS
def code(v, proj=""):
    txt = str(v or ""); t = txt.split(" - ")[0].strip().upper(); t = re.sub(r"^CSE-", "", t); t = re.sub(r"^ECU\d+(_\d+)?-", "", t)
    both = (txt + " " + str(proj or "")).upper()
    return ("21212" if "21212" in both else "17049" if "17049" in both else "24091" if "24091" in both else "?") + "|" + t
with open_workbook(os.path.join(tempfile.gettempdir(), "_BD_fac_shadow.xlsb")) as wb:
    with wb.get_sheet("LISTA SISTEMAS Y SUBSISTEMAS") as ws:
        L = [[c.v for c in r] for r in ws.rows()]
    with wb.get_sheet("TASK_IMPORT") as ws:
        T = [[c.v for c in r] for i, r in enumerate(ws.rows()) if i >= 2]
SUB_SS = {code(r[1], r[2]): str(r[2]) for r in L if len(r) > 2 and r[1] and r[2]}
SUB_S = {code(r[0], r[2]): str(r[2]) for r in L if len(r) > 2 and r[0] and r[2]}
for r in data["ac1"]:
    if not r["subpry"]: r["subpry"] = SUB_SS.get(code(r["subsistema"], r["proyecto"]), "")
for r in data["hc1"]:
    if not r["subproyecto"]: r["subproyecto"] = SUB_S.get(code(r["sistema"], r["proyecto"]), "")
# totales de certificados pre/com (TASK_IMPORT)
req = sum(1 for r in T if len(r) > 13 and r[3]); ok = sum(1 for r in T if len(r) > 13 and r[3] and r[13] == "Closed")
data["cert"] = {"req": req, "ok": ok}
print("AC1 sin subproyecto:", sum(1 for r in data["ac1"] if not r["subpry"]), "| HC1 sin subproyecto:", sum(1 for r in data["hc1"] if not r["subproyecto"]), "| cert", req, ok)

s = open(TPL, encoding="utf-8").read()
def rep(a, b):
    global s
    assert a in s, a[:90]; s = s.replace(a, b)
rep("<title>Control de Dossieres AC1 / HC1 · CSE</title>", "<title>Control de Dossieres AC1 / HC1 · Facilidades CSE</title>")
s = re.sub(r"CONTROL DE DOSSIERES · CAÑO SUR ESTE", "CONTROL DE DOSSIERES · FACILIDADES Y ESTACIONES", s, count=1)
rep('<div class="sub"><b>HC1</b> RSPA-Arranque &nbsp;·&nbsp; <b>AC1</b> Subsistemas &nbsp;·&nbsp; <b>Dossieres</b> CIT &nbsp;·&nbsp; Módulos 3, 4 y 5</div>',
    '<div class="sub"><b>HC1</b> por sistema &nbsp;·&nbsp; <b>AC1</b> por subsistema &nbsp;·&nbsp; <b>Certificados</b> y <b>pendientes</b> SmartCompletions &nbsp;·&nbsp; Estación Centauros EP1 · PAD MITO 2 · PAD 3 · PAD 2</div>')
rep("Fuente: BD GENERAL · CSE · PAD2 y Exteriores (oficial)", "Fuente: BD GENERAL · CSE · PAD2 y Facilidades")
# indicador de dossier -> certificados pre/com
rep('<div class="gcard" onclick="goTab(\'dos\')"><div id="g-dos"></div><div><div class="gt">Dossieres aprobados CIT</div>',
    '<div class="gcard" onclick="goTab(\'ac1\')"><div id="g-dos"></div><div><div class="gt">Certificados pre/com cerrados</div>')
s = re.sub(r"  gauge\('g-dos', pct\(ap,ar\), C\.mg\);[^\n]*\n",
           "  gauge('g-dos', pct(DATA.cert.ok,DATA.cert.req), C.mg); $('gv-dos').textContent=`${nf(DATA.cert.ok)} / ${nf(DATA.cert.req)}`; $('gs-dos').textContent=`${nf(DATA.cert.req-DATA.cert.ok)} certificados abiertos en SmartCompletions`;\n", s, count=1)
assert "DATA.cert.ok" in s
# ocultar pestaña de dossieres (la BD de facilidades no trae estatus de dossier)
rep('<div class="fg"><label>Estatus dossier</label><select id="hc1-dos"></select></div>', '<div class="fg" style="display:none"><label>Estatus dossier</label><select id="hc1-dos"></select></div>')
rep('<button class="tab" data-v="dos">', '<button class="tab" data-v="dos" style="display:none">')
# columnas de la tabla HC1
rep("['estatus_entrega_dossier','Dossier',bDos],['total_pend_abiertos','Pdtes',null,'n'],['f_arranque','F. arranque'],['responsable','Responsable']",
    "['total_cert_pendientes','Cert. pend.',null,'n'],['total_pend_abiertos','Pdtes',null,'n'],['f_prog_hc1','F. prog. HC1'],['firma_ops','F. cierre SC']")
rep("['HC1 arrancados',hr,'f_arranque',()=>true,C.lm,'hc1']", "['HC1 cerrados en SC',hr,'firma_ops',()=>true,C.lm,'hc1']")
s = s.replace("Control de Dossieres AC1 / HC1 · Caño Sur Este · v3", "Control de Dossieres AC1 / HC1 · Facilidades y Estaciones · Caño Sur Este")
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
s = s.replace("__PAYLOAD__", payload).replace('href="../../index.html"', 'href="../../../index.html"')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(s)
print("OK", OUT, f"{os.path.getsize(OUT):,}")
