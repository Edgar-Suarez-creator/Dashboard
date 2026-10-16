"""Dashboard Control de Dossieres · FACILIDADES / ESTACIONES (mismo diseño v3 de Exteriores).
La BD de facilidades no trae RSPA-ARRANQUE ni ESTATUS DOSSIERES y sus hojas resumen tienen #N/A,
así que los HC1/AC1 se arman desde los datos crudos de SmartCompletions:
  ASSURANCE_IMPORT (certificados AC1 / HC1) · TASK_IMPORT (certificados pre/com) · PTES_IMPORT (pendientes)
  SUBSISTEMAS (estado de arranque, donde el nombre es legible)
Uso: python build_fac.py   ->  Ejecutable/Dashboard_Control_Dossiers_Facilidades.html"""
import os, sys, glob, json, shutil, tempfile, re, collections
from datetime import datetime, timedelta, date
sys.stdout.reconfigure(encoding="utf-8")
from pyxlsb import open_workbook
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = max(glob.glob(os.path.join(HERE, "BD GENERAL*FACILIDADES*.xlsb")), key=os.path.getmtime)
TPL = os.path.join(HERE, "..", "Exteriores", "Propuesta_v2", "template_v3.html")
OUT = os.path.join(HERE, "Ejecutable", "Dashboard_Control_Dossiers_Facilidades.html")
TODAY = date.today().isoformat()
shadow = os.path.join(tempfile.gettempdir(), "_BD_fac_shadow.xlsb"); shutil.copyfile(SRC, shadow)

def d(v):
    try:
        n = float(v)
        return (datetime(1899, 12, 30) + timedelta(days=n)).strftime("%Y-%m-%d") if 1 < n < 100000 else ""
    except (TypeError, ValueError): return ""
def s(v):
    if v is None or (isinstance(v, int) and not isinstance(v, bool)): return ""
    t = str(v).strip(); return "" if t.startswith("0x") else t
def code(v, proj=""):  # llave módulo|código del sistema o subsistema (sin prefijos CSE-ECUxxxxx_yy-)
    txt = s(v); t = txt.split(" - ")[0].strip().upper()
    t = re.sub(r"^CSE-", "", t); t = re.sub(r"^ECU\d+(_\d+)?-", "", t)
    both = (txt + " " + s(proj)).upper()
    mod = "21212" if "21212" in both else "17049" if "17049" in both else "24091" if "24091" in both else "?"
    return mod + "|" + t
def sheet(wb, name, skip):
    with wb.get_sheet(name) as ws:
        return [[c.v for c in r] for i, r in enumerate(ws.rows()) if i >= skip]
with open_workbook(shadow) as wb:
    TASK = sheet(wb, "TASK_IMPORT", 2); PTES = sheet(wb, "PTES_IMPORT", 2); ASSU = sheet(wb, "ASSURANCE_IMPORT", 2)
    SUBS = sheet(wb, "SUBSISTEMAS", 5)
    with wb.get_sheet("HOME") as ws:
        corte = next((d(c.v) for r in ws.rows() for c in r if isinstance(c.v, float) and c.v > 40000), "")
g = lambda r, i: r[i] if i < len(r) else None

# ---- contexto por sistema / subsistema (proyecto, subproyecto, etapa, nombre completo)
CTX_SS, CTX_S = {}, {}
etapas_ss, etapas_s = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
for r in TASK:
    if not s(g(r, 3)): continue
    ss, sy = code(g(r, 3), g(r, 0)), code(g(r, 2), g(r, 0))
    CTX_SS.setdefault(ss, dict(proyecto=s(g(r, 0)), sub=s(g(r, 1)), sistema=s(g(r, 2)), subsistema=s(g(r, 3))))
    CTX_S.setdefault(sy, dict(proyecto=s(g(r, 0)), sub=s(g(r, 1)), sistema=s(g(r, 2))))
    if s(g(r, 9)): etapas_ss[ss][s(g(r, 9))] += 1; etapas_s[sy][s(g(r, 9))] += 1
for r in PTES:
    if not s(g(r, 3)): continue
    ss, sy = code(g(r, 3), g(r, 0)), code(g(r, 2), g(r, 0))
    CTX_SS.setdefault(ss, dict(proyecto=s(g(r, 0)), sub=s(g(r, 1)), sistema=s(g(r, 2)), subsistema=s(g(r, 3))))
    CTX_S.setdefault(sy, dict(proyecto=s(g(r, 0)), sub=s(g(r, 1)), sistema=s(g(r, 2))))
    if s(g(r, 7)): etapas_ss[ss][s(g(r, 7))] += 1; etapas_s[sy][s(g(r, 7))] += 1
# estado de arranque por subsistema (hoja SUBSISTEMAS, solo filas legibles)
ARR = {}
for r in SUBS:
    if s(g(r, 4)): ARR[code(g(r, 4), g(r, 1))] = s(g(r, 53)) or ""
# ---- certificados y pendientes abiertos por subsistema / sistema y disciplina
DISC_C = {"ELEC": "cert_electrica", "INST": "cert_instr", "MECH-EST": "cert_tuberia", "MECH": "cert_tuberia", "CIVIL": "cert_civil"}
DISC_P = {"CIVIL": "pdts_civil", "ELEC": "pdts_elect", "INST": "pdts_instr", "MECH-EST": "pdts_tuber", "MECH": "pdts_tuber"}
cert_s = collections.defaultdict(collections.Counter); cert_ss = collections.defaultdict(collections.Counter)
cert_tot_ss = collections.defaultdict(lambda: [0, 0])
for r in TASK:
    if not s(g(r, 3)): continue
    ss, sy = code(g(r, 3), g(r, 0)), code(g(r, 2), g(r, 0)); closed = s(g(r, 13)) == "Closed"
    cert_tot_ss[ss][0] += 1; cert_tot_ss[ss][1] += closed
    if not closed:
        k = DISC_C.get(s(g(r, 4)), "cert_civil"); cert_s[sy][k] += 1; cert_ss[ss][k] += 1
pend_s = collections.defaultdict(collections.Counter); pend_ss = collections.defaultdict(collections.Counter)
for r in PTES:
    if not s(g(r, 3)) or s(g(r, 14)) == "Closed": continue
    ss, sy = code(g(r, 3), g(r, 0)), code(g(r, 2), g(r, 0)); k = DISC_P.get(s(g(r, 4)), "pdts_civil")
    pend_s[sy][k] += 1; pend_ss[ss][k] += 1
def short_proj(p):
    return "M3" if "17049" in p else "M4" if "21212" in p else "M5" if "24091" in p else (p[:10] or "—")
def venc(st, fp):
    if st == "CERRADO": return "CERRADO"
    if not fp: return "SIN FECHA"
    dd = (date.fromisoformat(fp) - date.today()).days
    return "VENCIDO" if dd < 0 else "PROXIMO A VENCER" if dd <= 15 else "A TIEMPO"

# ---- AC1: un registro por certificado AC1 + subsistemas sin certificado AC1
ac1, seen_ss = [], set()
hc1, seen_s = [], set()
for r in ASSU:
    typ = s(g(r, 10)); sy_full, ss_full = s(g(r, 6)), s(g(r, 7)); st = "CERRADO" if s(g(r, 13)) == "Closed" else "PENDIENTE"
    fp, fc = d(g(r, 12)), d(g(r, 14))
    if typ.startswith("AC1"):
        ss = code(ss_full, g(r, 3)); seen_ss.add(ss); ctx = CTX_SS.get(ss, {})
        tot = cert_tot_ss.get(ss, [0, 0])
        ac1.append(dict(proyecto=s(g(r, 3)), subpry=ctx.get("sub", ""), etapa=(etapas_ss[ss].most_common(1)[0][0] if etapas_ss[ss] else ""),
                        subsistema=ss_full, rspa="", id_certificado=s(g(r, 8)), estado_arranque=ARR.get(ss) or ("ARRANCADO" if st == "CERRADO" else "NO ARRANCADO"),
                        fecha_programada=fp, fecha_cierre_sc=fc, estatus=st, estado_ac1_sc=st, vencimiento_ac1=venc(st, fp),
                        req=1, cer=1 if st == "CERRADO" else 0, av_sem=0,
                        observaciones=(f"Certificados pre/com: {tot[1]}/{tot[0]} cerrados · pendientes abiertos: {sum(pend_ss[ss].values())}" if tot[0] else "")))
    elif typ.startswith("HC1"):
        sy = code(sy_full, g(r, 3)); seen_s.add(sy); ctx = CTX_S.get(sy, {})
        cs, ps = cert_s[sy], pend_s[sy]
        hc1.append(dict(proyecto=s(g(r, 3)), subproyecto=ctx.get("sub", ""), etapa=(etapas_s[sy].most_common(1)[0][0] if etapas_s[sy] else ""),
                        sistema=sy_full, rspa="", f_arranque=fc, f_prog_hc1=fp, firma_ops=fc, id_hc1=s(g(r, 8)),
                        e_arranque="ARRANCADO" if st == "CERRADO" else "NO ARRANCADO", e_entrega="ENTREGADO" if st == "CERRADO" else "NO ENTREGADO",
                        e_smart_c="CERRADO" if st == "CERRADO" else "ABIERTO", vigencia_hc1=venc(st, fp),
                        excl1="", excl2="", excl3="", excl4="", excl5="", con_exclusiones="", scada_pozos_electrico="", comentarios_hc1="",
                        cert_electrica=cs["cert_electrica"], cert_instr=cs["cert_instr"], cert_tuberia=cs["cert_tuberia"], total_cert_pendientes=sum(cs.values()),
                        pdts_civil=ps["pdts_civil"], pdts_elect=ps["pdts_elect"], pdts_instr=ps["pdts_instr"], pdts_tuber=ps["pdts_tuber"], total_pend_abiertos=sum(ps.values()),
                        fecha_envio_cit="", observaciones="", fecha_aprob_cit="", estatus_entrega_dossier="", semanal_hc1=0, responsable="",
                        comentarios_dosieres="", ruta_ecosearch="", estatus_gd_dossier="", plan_entrega="", pendiente_envio=""))
# un registro por certificado (ASSURANCE_IMPORT repite el HC1 una vez por subsistema)
def dedup(rows, key):
    out, ids = [], set()
    for r in rows:
        k = r[key]
        if k in ids: continue
        ids.add(k); out.append(r)
    return out
hc1 = dedup(hc1, "id_hc1"); ac1 = dedup(ac1, "id_certificado")
for ss, ctx in CTX_SS.items():
    if ss in seen_ss: continue
    tot = cert_tot_ss.get(ss, [0, 0])
    ac1.append(dict(proyecto=ctx["proyecto"], subpry=ctx["sub"], etapa=(etapas_ss[ss].most_common(1)[0][0] if etapas_ss[ss] else ""), subsistema=ctx["subsistema"], rspa="",
                    id_certificado="SIN CERTIFICADO", estado_arranque=ARR.get(ss) or "NO ARRANCADO", fecha_programada="", fecha_cierre_sc="", estatus="PENDIENTE",
                    estado_ac1_sc="SIN CERTIFICADO", vencimiento_ac1="SIN FECHA", req=1, cer=0, av_sem=0,
                    observaciones=(f"Certificados pre/com: {tot[1]}/{tot[0]} cerrados · pendientes abiertos: {sum(pend_ss[ss].values())}" if tot[0] else "")))
for r in hc1 + ac1: r["mod"] = short_proj(r["proyecto"])
C = collections.Counter
print("fuente:", os.path.basename(SRC), "· corte", corte)
print("HC1:", len(hc1), C(x["e_entrega"] for x in hc1), "| vig", C(x["vigencia_hc1"] for x in hc1))
print("AC1:", len(ac1), C(x["estatus"] for x in ac1), "| sin cert", sum(1 for x in ac1 if x["id_certificado"] == "SIN CERTIFICADO"), "| arranque", C(x["estado_arranque"] for x in ac1))
print("subproyectos AC1:", C(x["subpry"] for x in ac1).most_common(8))
print("cert. pendientes en HC1:", sum(x["total_cert_pendientes"] for x in hc1), "· pendientes abiertos:", sum(x["total_pend_abiertos"] for x in hc1))
data = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "today": TODAY, "hc1": hc1, "ac1": ac1}
json.dump(data, open(os.path.join(HERE, "data_fac.json"), "w", encoding="utf-8"), ensure_ascii=False)
