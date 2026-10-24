"""Ruta al arranque: cruza por locación los datos de los dashboards publicados
(Tracking → Inventarios → Preservación → Programación → AC1/HC1-Dossier → [IDA] → Garantías → QA)  ->  data_ruta.json"""
import re, json, sys, os, datetime, collections
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\edgar.suarez\Dashboard"
HERE = os.path.dirname(os.path.abspath(__file__))
HOY = datetime.date.today().isoformat()
def load(p, name="DATA"):
    h = open(R + "\\" + p, encoding="utf-8").read(); m = re.search(r"const %s\s*=\s*" % name, h)
    return json.JSONDecoder().raw_decode(h[m.end():])[0]
def _trk_v2():
    """Tracking v2 (columnar): se decodifica y se dejan solo los equipos, con los nombres de campo que usa este extractor."""
    D = load(r"Tracking_Equipos\Ejecutable\Dashboard_Tracking_Equipos.html")
    if "items" in D: return D
    C = D["cols"]; items = []
    for i in range(D["n"]):
        x = {k: (C["d"][k][col[i]] if k in C["d"] and col[i] is not None else col[i]) for k, col in C["v"].items()}
        if not x.get("eq"): continue
        rec = x.get("et") == "Recibido"
        tarde = bool(not rec and x.get("eta") and x.get("tin") and x["eta"] > x["tin"])
        items.append(dict(tipo=x.get("ti") or x.get("eq"), tag=x.get("tag") or "", prov=x.get("pv") or "", odb=x.get("odb"), eta=x.get("eta"),
                          lleg=x.get("ll"), recibido=rec, cant=x.get("q") or 0, f_sap=x.get("fsap"), loc=x.get("loc"), a1=x.get("a1"), a2=x.get("a2"),
                          sub=x.get("sp"), alertas=[f"llega después del taladro ({x.get('tal')}, {x.get('tin')})"] if tarde else []))
    return {"items": items, "hoy": D.get("corte")}
TRK = _trk_v2()
INV = load(r"Inventarios\Ejecutable\Dashboard_Inventarios.html")
PRE = load(r"Dashboard_Preservación\Ejecutable\Dashboard_Preservacion.html")
DOS = load(r"Control_Dossiers_AC1-HC1\Exteriores\Ejecutable\Dashboard_Control_Dossiers.html")
FAC = load(r"Control_Dossiers_AC1-HC1\Facilidades\Ejecutable\Dashboard_Control_Dossiers_Facilidades.html")
GAR = load(r"Garantias\Ejecutable\Dashboard_Garantias.html")
QA = load(r"Consolidado_QA\Ejecutable\Dashboard_QA_CSE.html")
TAL = load(r"Timeline_Taladro\Ejecutable\Timeline_Taladro_Q3Q4_2026.html")
EST = load(r"Timeline_Estaciones\Ejecutable\Timeline_Estaciones_Q3Q4_2026.html")

CLR = re.compile(r"\b(CASE|CUMA|EMBR|WDCS)[\s\-_]*0*(\d{1,4})\b", re.I)
def norm_loc(*vals):
    t = " ".join(str(v) for v in vals if v not in (None, "", "None"))
    m = CLR.search(t)
    if m: return f"{m.group(1).upper()}-{int(m.group(2)):04d}"
    u = t.upper()
    m = re.search(r"CLUSTER\s*0*(\d{2,4})\b", u)
    if m: return f"CASE-{int(m.group(1)):04d}"
    m = re.search(r"\bCMO[\s\-_]*0*(\d{1,2})\b", u)
    if m: return f"CMO-{int(m.group(1)):02d}"
    if re.search(r"MITO\s*2|MITO\s*II|PADMITO", u): return "PAD MITO 2"
    if re.search(r"PAD\s*3|INYECCI", u): return "PAD 3 · Inyección"
    if re.search(r"\bEP\s*-?1\b|CENTAUROS|ESTACI[OÓ]N|SKIM|FWKO|TRATAMIENTO|UTILITARIOS|CARCAMOS", u): return "Estación Centauros (EP1)"
    if re.search(r"PAD\s*2|PAD-2", u): return "PAD 2"
    if re.search(r"\bEMBRUJO\b", u): return "EMBR-0001"
    if re.search(r"\bCUMANDAY\s*0*(\d{1,4})\b", u): return f"CUMA-{int(re.search(r'CUMANDAY\s*0*(\d{1,4})', u).group(1)):04d}"
    if re.search(r"TRONCAL|RAMAL|REDES|SUBTRANSMISI", u): return "Troncales y redes"
    if re.search(r"MITO\s*1|CAMPAMENTO|BIOCAMP", u): return "MITO 1 · Campamento"
    return None
def frente(loc):
    return "Exteriores" if re.match(r"(CASE|CUMA|EMBR|WDCS|CMO)-|Troncales", loc or "") else "Estaciones"
L = collections.defaultdict(lambda: {"trk": [], "inv": [], "pre": [], "ac1": [], "hc1": [], "gar": [], "qa": []})

# --- 1 Tracking (compras / llegada de equipos)
for x in TRK["items"]:
    loc = norm_loc(x["loc"], x["a1"], x["tag"], x["a2"], x["sub"])
    if not loc: continue
    L[loc]["trk"].append(dict(t=x["tipo"], tag=x["tag"], prov=x["prov"], odb=x["odb"], eta=x["eta"], lleg=x["lleg"], rec=x["recibido"], cant=x["cant"], al=x["alertas"][:2]))
# --- 2 En campo: SOLO EQUIPOS. Recibidos en sitio según tracking + equipos que el inventario tiene en bodega
EQ_INV = re.compile(r"TRANSFORMER|SKID|SWITCHGEAR|E-HOUSE|PUMP|BOMBA|DRIVE|VARIABLE FREQ|MOTOR|GENERATOR|PANEL|SWITCHBOARD|TABLERO|CABINET|VESSEL|TANK\b|COMPRESSOR|SEPARATOR|HEATER|RECLOSER|DISCONNECT|UPS|BATTERY CHARGER|ANALYZER|BLOWER|FAN, ", re.I)
for x in TRK["items"]:
    if not x["recibido"]: continue
    loc = norm_loc(x["loc"], x["a1"], x["tag"], x["a2"], x["sub"])
    if not loc: continue
    L[loc]["inv"].append(dict(src="Tracking · recibido en sitio", t=x["tipo"], tag=x["tag"], cant=float(x["cant"] or 0), prov=x["prov"], f=x["f_sap"] or x["eta"], alm=""))
for x in INV["items"]:
    if not EQ_INV.search(str(x["texto_breve"] or "")): continue
    loc = norm_loc(x["clas2"], x["clas1"])
    if not loc: continue
    L[loc]["inv"].append(dict(src="Inventario · en bodega", t=x["texto_breve"], tag=x["material"], cant=float(x["cantidad"] or 0), prov="", f="", alm=x["denom_alm"]))
# --- 3 Preservación
for x in PRE["equipos"]:
    loc = norm_loc(x["destino"], x["tag"], x["area"], x["ubic2"])
    if not loc: continue
    L[loc]["pre"].append(dict(t=x["tipo"], tag=x["tag"], ubic=x["ubic"], venc=x["n_venc"] or 0, pend=x["n_pend"] or 0, ejec=x["n_ejec"] or 0, ult=x["ultima_ejec"], hc1=str(x["ubic"]).startswith("Entregado")))
# --- 5 Certificación AC1 / HC1 / dossier
_ids = set()
for x in DOS["ac1"] + FAC["ac1"]:
    cid = x["id_certificado"]
    if cid and cid != "SIN CERTIFICADO":
        if cid in _ids: continue
        _ids.add(cid)
    fac = x in FAC["ac1"]
    loc = norm_loc(x["subpry"], x["subsistema"]) if fac else norm_loc(x["subsistema"], x["subpry"], x["etapa"])
    if not loc: continue
    L[loc]["ac1"].append(dict(id=x["id_certificado"], ss=x["subsistema"], st=x["estatus"], fp=x["fecha_programada"], arr=x["estado_arranque"], req=x["req"], cer=x["cer"]))
_ids = set()
for x in DOS["hc1"] + FAC["hc1"]:
    if x["id_hc1"]:
        if x["id_hc1"] in _ids: continue
        _ids.add(x["id_hc1"])
    fac = x in FAC["hc1"]
    loc = norm_loc(x["subproyecto"], x["sistema"]) if fac else norm_loc(x["sistema"], x["etapa"], x["subproyecto"])
    if not loc: continue
    L[loc]["hc1"].append(dict(id=x["id_hc1"], s=x["sistema"], arr=x["e_arranque"], ent=x["e_entrega"], fp=x["f_prog_hc1"], cert=float(x["total_cert_pendientes"] or 0),
                              pend=float(x["total_pend_abiertos"] or 0), dos=x["estatus_entrega_dossier"], cit=x["fecha_aprob_cit"]))
# --- 7 Garantías
for x in GAR["items"]:
    loc = norm_loc(x["ubic"], x["sistema"], x["subsistema"], x["tag"])
    if not loc: continue
    L[loc]["gar"].append(dict(t=x["tipo"], prov=x["proveedor"], st=x["estado"], ap=x["fecha_apertura"], dias=x["dias"], niv=x["nivel"]))
# --- 8 QA (aspectos, NCR, solicitudes técnicas, dossier QA)
for sec, k in (("aspectos", "estado"), ("ncr", "estado"), ("soltec", "estado"), ("dossier", "estatus")):
    for x in QA[sec]["rows"]:
        loc = norm_loc(x.get("loc"), x.get("ubic"), x.get("subProy"))
        if not loc: continue
        st = str(x.get(k) or "")
        abierto = (st.upper().startswith("ABIERT")) if sec != "dossier" else (st.upper() in ("CRITICO", "MODERADO", "EN TIEMPO"))
        L[loc]["qa"].append(dict(sec=sec, cod=x.get("codigo") or x.get("loc"), st=st, ab=abierto, f=x.get("fvis") or x.get("fhall") or x.get("femit") or x.get("frev1"),
                                 d=(x.get("aspecto") or x.get("detectH") or x.get("desc") or x.get("ejec") or "")[:140]))
# --- 4 Programación: ruta del taladro y cronogramas de estaciones
TC = {}
for x in TAL["items"]:
    c = norm_loc(x["cluster"]) or x["cluster"]
    t = TC.setdefault(c, dict(taladro=set(), ini=None, fin=None, comp1=None, pozos=set(), est=collections.Counter()))
    t["taladro"].add(x["taladro"].split(" - ")[0]); t["pozos"].add(x["pozo"]); t["est"][x["estado"]] += 1
    if x["ini"]: t["ini"] = min(t["ini"] or x["ini"], x["ini"])
    if x["fin"]: t["fin"] = max(t["fin"] or x["fin"], x["fin"])
    if x["evento"] == "COMPLETAMIENTO" and x["fin"]: t["comp1"] = min(t["comp1"] or x["fin"], x["fin"])
EP = collections.defaultdict(list)   # tareas de cronogramas de estaciones que mencionan una locación
for aliado, rows in EST["todo"].items():
    for x in rows:
        loc = norm_loc(x["descripcion"])
        if loc and (x.get("hijos") in (0, "0", None)):
            EP[loc].append(dict(al=aliado, d=x["descripcion"][:90], fin=x["fin"], pron=x["pronostico"], prog=x["pctProg"], ejec=x["pctEjec"]))
# --- 4a Construcción: entrega de locaciones por aliado (Timeline Estaciones). Sin entrega de construcción no se llevan equipos.
# Aplican solo los aliados con equipos relevantes; TECNITANQUES (100 %), PETROLABIN y BIOCAMPAMENTOS no aplican.
APLICA = {"DIATECO": ("Estaciones · EP1", "Estación Centauros (EP1)"), "MTZ 08": ("Clústeres", None),
          "DISCON 17": ("Troncales eléctricas y centro de maniobra", "Troncales y redes"),
          "PYC ANDINOS 08": ("Facilidades de pozo y ramales", None), "GTC 010": ("PAD 3 · troncal de inyección · troncal 2A", "PAD 3 · Inyección")}
HITO = re.compile(r"^\s*(fin\b|acta\b|hito|jitos|aprobaci|odc firmada|cierre documental|mantenimiento de zodme|actividades iniciales|suministros|uso de opci)", re.I)
BAJAR = {"GTC 010", "DISCON 17"}   # su nivel 1 agrupa varios frentes: se toma el nivel 2
def cons_loc(al, d):
    if al == "GTC 010": return "Troncales y redes" if re.search(r"TRONCAL\s*2A|TR 2A", d, re.I) else "PAD 3 · Inyección"
    if al == "DISCON 17": return "Troncales y redes"
    if al == "DIATECO": return "Estación Centauros (EP1)"
    return norm_loc(d) or APLICA[al][1]
CONS = collections.defaultdict(list)
for al, rows in EST["todo"].items():
    if al not in APLICA: continue
    byid = {r["id"]: r for r in rows}
    kids = collections.defaultdict(list)
    for r in rows: kids[str(r.get("parent"))].append(r)
    def take(r, nivel):
        d = r["descripcion"] or ""
        if HITO.search(d) or not r.get("fin"): return
        loc = cons_loc(al, d)
        if loc is None or (nivel == 1 and al in BAJAR and kids.get(str(r["id"]))) or (nivel == 1 and al in ("MTZ 08", "PYC ANDINOS 08") and not norm_loc(d)):
            for k in kids.get(str(r["id"]), []): take(k, nivel + 1)
            return
        CONS[loc].append(dict(al=al, d=d[:90], ini=r["comienzo"], fin=r["fin"], pron=r.get("pronostico") or r["fin"], prog=float(r["pctProg"] or 0),
                              ejec=float(r["pctEjec"] or 0), dur=float(r.get("duracion") or 0) or 1))
    for r in rows:
        if str(r.get("nivel")) == "1": take(r, 1)
ALIADOS = []
for aliado, rows in EST["todo"].items():
    if aliado not in APLICA: continue
    top = [r for r in rows if r.get("parent") in (None, "None")]
    if not top: continue
    fin = max((r["fin"] for r in top if r["fin"]), default=None); pron = max((r["pronostico"] for r in top if r.get("pronostico")), default=None)
    w = sum(float(r["duracion"] or 0) for r in top) or 1
    ALIADOS.append(dict(al=aliado, alcance=APLICA[aliado][0], fin=fin, pron=pron, prog=sum(float(r["pctProg"] or 0) * float(r["duracion"] or 0) for r in top) / w,
                        ejec=sum(float(r["pctEjec"] or 0) * float(r["duracion"] or 0) for r in top) / w,
                        locs=sorted({l for l, v in CONS.items() if any(x["al"] == aliado for x in v)})))

# --- armar locaciones con estado por etapa
def dd(a, b): return (datetime.date.fromisoformat(a[:10]) - datetime.date.fromisoformat(b[:10])).days
out = []
for loc in sorted(set(L) | {c for c in TC if c and re.match(r"(CASE|CUMA|EMBR|WDCS)-", c)} | set(CONS)):
    d = L[loc]; t = TC.get(loc); ep = EP.get(loc, []); cn = CONS.get(loc, [])
    S = {}
    # 1 compras
    tr = d["trk"]; p = [x for x in tr if not x["rec"]]
    late = [x for x in p if any("después" in a for a in x["al"]) or x["lleg"] == "ETA vencida"]
    sc = [x for x in p if x["lleg"] == "Sin compra"]
    S["trk"] = dict(n=len(tr), ok=len(tr) - len(p), pend=len(p), late=len(late), sc=len(sc),
                    st="na" if not tr else "ok" if not p else "bad" if late else "warn")
    # 2 inventario
    iv = d["inv"]; S["inv"] = dict(n=len(iv), trk=sum(1 for x in iv if x["src"].startswith("Tracking")), bod=sum(1 for x in iv if x["src"].startswith("Inventario")), st="info" if iv else "na")
    # 3 preservación (sin entregados a operaciones)
    pr = [x for x in d["pre"] if not x["hc1"]]
    venc = sum(x["venc"] for x in pr); pend = sum(x["pend"] for x in pr)
    S["pre"] = dict(n=len(pr), hc1=len(d["pre"]) - len(pr), venc=venc, pend=pend, st="na" if not pr else "bad" if venc else "warn" if pend else "ok")
    # 4a construcción (entrega de la locación por el aliado)
    if cn:
        w = sum(x["dur"] for x in cn); ej = sum(x["ejec"] * x["dur"] for x in cn) / w; pg = sum(x["prog"] * x["dur"] for x in cn) / w
        fin = max(x["fin"] for x in cn); pron = max(x["pron"] for x in cn); done = ej >= 0.999
        tarde = bool(t and t["ini"] and not done and pron > t["ini"])
        S["cons"] = dict(al=sorted({x["al"] for x in cn}), n=len(cn), ejec=100 if done else min(99, int(ej * 100)), prog=round(pg * 100), fin=fin, pron=pron, done=done,
                         abiertas=sum(1 for x in cn if x["ejec"] < 0.999), st="ok" if done else "bad" if tarde else "warn")
    else:
        S["cons"] = dict(st="na")
    # 4b programación
    if t:
        dias = dd(t["ini"], HOY) if t["ini"] else None
        st = "ok" if t["fin"] and t["fin"] < HOY else "warn" if (dias is not None and dias <= 90) else "info"
        S["prog"] = dict(tipo="taladro", taladro=sorted(t["taladro"]), ini=t["ini"], fin=t["fin"], comp1=t["comp1"], pozos=len(t["pozos"]), dias=dias, st=st)
    elif ep:
        fin = max(x["fin"] for x in ep if x["fin"]); ej = sum(float(x["ejec"] or 0) for x in ep) / len(ep)
        S["prog"] = dict(tipo="cronograma", n=len(ep), fin=fin, ejec=round(ej * 100), st="ok" if ej >= .999 else "warn")
    else:
        S["prog"] = dict(tipo=None, st="na")
    # ventana de preparación: desde la entrega de construcción (o hoy) hasta el 1er completamiento del taladro
    c_ok = S["cons"].get("pron") if cn else None
    v_ini = max(c_ok or HOY, HOY) if (not cn or not S["cons"]["done"]) else HOY
    v_fin = (t["comp1"] or t["ini"]) if t else None
    S["prog"]["vent"] = dict(ini=v_ini, fin=v_fin, cons=c_ok, cons_ok=bool(cn and S["cons"]["done"]),
                             dias=dd(v_fin, v_ini) if v_fin else None)
    # 5 AC1 / HC1 / dossier
    a1 = d["ac1"]; a1p = [x for x in a1 if x["st"] != "CERRADO"]; a1v = [x for x in a1p if x["fp"] and x["fp"] < HOY]
    S["ac1"] = dict(n=len(a1), ok=len(a1) - len(a1p), pend=len(a1p), venc=len(a1v), st="na" if not a1 else "ok" if not a1p else "bad" if a1v else "warn")
    h1 = d["hc1"]; h1p = [x for x in h1 if x["ent"] != "ENTREGADO"]
    dev = sum(1 for x in h1 if x["dos"] == "DEVUELTO"); dpend = sum(1 for x in h1 if x["dos"] in ("PENDIENTE", "DEVUELTO", "ENVIADO"))
    cert = sum(x["cert"] for x in h1); pa = sum(x["pend"] for x in h1)
    h1v = [x for x in h1p if x["fp"] and x["fp"] < HOY]
    S["hc1"] = dict(n=len(h1), ok=len(h1) - len(h1p), pend=len(h1p), venc=len(h1v), cert=int(cert), pab=int(pa),
                    st="na" if not h1 else "ok" if not h1p else "bad" if h1v else "warn")
    # 5b elaboración de dossier: estatus de entrega del dossier de los HC1 + dossier QA del aliado
    dq = [x for x in d["qa"] if x["sec"] == "dossier"]
    dq_crit = sum(1 for x in dq if x["st"].upper() == "CRITICO"); dq_ab = sum(1 for x in dq if x["ab"])
    hd = [x for x in h1 if x["dos"]]
    S["dos"] = dict(n=len(hd) + len(dq), ok=sum(1 for x in hd if x["dos"] == "ENTREGADO") + (len(dq) - dq_ab), pend=dpend + dq_ab, dev=dev, crit=dq_crit,
                    hc1=len(hd), qa=len(dq), st="na" if not (hd or dq) else "bad" if (dev or dq_crit) else "warn" if (dpend or dq_ab) else "ok")
    # 6 IDA (por integrar)
    S["ida"] = dict(st="na")
    # 7 garantías
    g = d["gar"]; ga = [x for x in g if x["st"] == "ABIERTA"]
    S["gar"] = dict(n=len(g), ab=len(ga), st="na" if not g else "bad" if ga else "ok")
    # 8 QA
    q = [x for x in d["qa"] if x["sec"] != "dossier"]; qa_ab = [x for x in q if x["ab"]]
    ncr = sum(1 for x in qa_ab if x["sec"] == "ncr")
    S["qa"] = dict(n=len(q), ab=len(qa_ab), ncr=ncr, asp=sum(1 for x in qa_ab if x["sec"] == "aspectos"), sol=sum(1 for x in qa_ab if x["sec"] == "soltec"),
                   st="na" if not q else "bad" if ncr else "warn" if qa_ab else "ok")
    # alertas cruzadas
    al = []
    pend_eq = S["trk"]["pend"]
    vigente = bool(t and t["ini"] and (t["fin"] or t["ini"]) >= HOY)   # el taladro aún no termina en la locación
    if cn and vigente:
        C_ = S["cons"]
        if t and t["ini"] and not C_["done"] and C_["pron"] > t["ini"]:
            al.append(("bad", "Construcción", f"el taladro llega el {t['ini']} y la construcción ({', '.join(C_['al'])}) se entrega el {C_['pron']} · {C_['ejec']} % ejecutado"))
        elif not C_["done"] and t and t["ini"] and dd(t["ini"], HOY) <= 120:
            al.append(("warn", "Construcción", f"construcción al {C_['ejec']} % ({', '.join(C_['al'])}), entrega pronosticada {C_['pron']}: hasta la entrega no se pueden llevar equipos"))
        if C_["done"] and pend_eq and t and t["ini"] and dd(t["ini"], HOY) <= 120:
            al.append(("bad", "Compras", f"locación entregada por construcción y {pend_eq} equipo(s) aún sin llegar a campo"))
    v = S["prog"]["vent"]
    if v["fin"] and v["fin"] >= HOY and v["dias"] is not None and v["dias"] < 30 and (S["ac1"]["pend"] or S["pre"]["n"] or pend_eq):
        al.append(("bad" if v["dias"] < 0 else "warn", "Preparación", f"solo quedan {v['dias']} días entre la entrega de construcción/hoy ({v['ini']}) y el 1er completamiento ({v['fin']})"))
    if t and t["ini"]:
        dias = dd(t["ini"], HOY)
        if S["trk"]["late"]: al.append(("bad", "Compras", f"{S['trk']['late']} equipo(s) llegan después del taladro o con fecha vencida"))
        if S["trk"]["sc"] and dias <= 120: al.append(("warn", "Compras", f"{S['trk']['sc']} equipo(s) sin compra y el taladro {'ya está' if dias <= 0 else f'llega en {dias} días'}"))
        if S["ac1"]["pend"] and 0 <= dias <= 90: al.append(("warn", "Certificación", f"{S['ac1']['pend']} AC1 abiertos y el taladro " + ("llega hoy" if dias == 0 else f"llega en {dias} días")))
    if S["pre"]["venc"]: al.append(("bad", "Preservación", f"{S['pre']['venc']} rutina(s) de preservación vencida(s)"))
    if S["ac1"]["venc"]: al.append(("bad", "Certificación", f"{S['ac1']['venc']} AC1 con fecha programada vencida"))
    if S["hc1"]["venc"]: al.append(("bad", "HC1 / Dossier", f"{S['hc1']['venc']} HC1 sin entregar con fecha programada vencida"))
    if S["dos"]["dev"]: al.append(("bad", "Dossier", f"{S['dos']['dev']} dossier(es) devuelto(s)"))
    if S["dos"]["crit"]: al.append(("bad", "Dossier", f"{S['dos']['crit']} dossier(es) QA en estado crítico"))
    if S["hc1"]["cert"] and S["hc1"]["pend"]: al.append(("warn", "HC1 / Dossier", f"{S['hc1']['cert']} certificados pendientes en HC1 por entregar"))
    if S["gar"]["ab"] and (S["hc1"]["pend"] or (t and t["ini"])): al.append(("warn", "Garantías", f"{S['gar']['ab']} garantía(s) abierta(s) en la locación"))
    if S["qa"]["ncr"]: al.append(("bad", "QA", f"{S['qa']['ncr']} NCR abierta(s)"))
    if S["qa"]["asp"] + S["qa"]["sol"]: al.append(("warn", "QA", f"{S['qa']['asp'] + S['qa']['sol']} hallazgo(s)/solicitud(es) técnica(s) abiertas"))
    app = [k for k, v in S.items() if v["st"] in ("ok", "warn", "bad")]
    ready = round(100 * sum(1 for k in app if S[k]["st"] == "ok") / len(app)) if app else None
    hit = sum(len(x) for x in d.values()) + (1 if t else 0) + len(cn)
    if hit == 0: continue
    out.append(dict(loc=loc, fr=frente(loc), S=S, al=al, ready=ready, ruta=bool(t),
                    det={k: v[:250] for k, v in d.items()}, ep=ep[:60], cons=cn[:80]))
out.sort(key=lambda x: (not x["ruta"], x["S"]["prog"].get("ini") or "9999", x["fr"], x["loc"]))
META = dict(hoy=HOY, fuentes=dict(
    tracking=TRK.get("hoy"), inventarios=INV.get("today"), preservacion=PRE.get("corte") or PRE.get("today"), dossier=DOS.get("today"), facilidades=FAC.get("today"),
    garantias=GAR.get("corte"), qa=QA["meta"].get("corte"), taladro=TAL.get("corte"), estaciones=EST.get("corte")))
TOT = dict(
    trk=dict(n=len(TRK["items"]), rec=sum(1 for x in TRK["items"] if x["recibido"]), pend=sum(1 for x in TRK["items"] if not x["recibido"]),
             late=sum(1 for x in TRK["items"] if not x["recibido"] and (x["lleg"] == "ETA vencida" or any("después" in a for a in x["alertas"]))),
             sc=sum(1 for x in TRK["items"] if x["lleg"] == "Sin compra")),
    inv=dict(trk=sum(1 for x in TRK["items"] if x["recibido"]), bod=sum(1 for x in INV["items"] if EQ_INV.search(str(x["texto_breve"] or "")))),
    pre=dict(n=len(PRE["equipos"]), hc1=sum(1 for x in PRE["equipos"] if str(x["ubic"]).startswith("Entregado")),
             venc=sum(1 for a in PRE["actividades"] if a["estado"] == "vencida"), pend=sum(1 for a in PRE["actividades"] if a["estado"] == "pendiente")),
    prog=dict(cl=len([c for c in TC if c]), activos=sum(1 for c, t in TC.items() if t["ini"] and t["ini"] <= HOY <= (t["fin"] or "")), aliados=ALIADOS),
    cons=dict(n=sum(1 for x in out if x["S"]["cons"]["st"] != "na"), ok=sum(1 for x in out if x["S"]["cons"]["st"] == "ok"),
              tarde=sum(1 for x in out if x["S"]["cons"]["st"] == "bad")),
    dos=dict(n=sum(x["S"]["dos"].get("n", 0) for x in out), ok=sum(x["S"]["dos"].get("ok", 0) for x in out), dev=sum(x["S"]["dos"].get("dev", 0) for x in out),
             crit=sum(x["S"]["dos"].get("crit", 0) for x in out)),
    ac1=dict(n=len(DOS["ac1"]) + len(FAC["ac1"]), ok=sum(1 for x in DOS["ac1"] + FAC["ac1"] if x["estatus"] == "CERRADO"), fac=len(FAC["ac1"])),
    hc1=dict(n=len(DOS["hc1"]) + len(FAC["hc1"]), ok=sum(1 for x in DOS["hc1"] + FAC["hc1"] if x["e_entrega"] == "ENTREGADO"), fac=len(FAC["hc1"]), dos_ok=sum(1 for x in DOS["hc1"] if x["estatus_entrega_dossier"] == "ENTREGADO"),
             dev=sum(1 for x in DOS["hc1"] if x["estatus_entrega_dossier"] == "DEVUELTO")),
    gar=dict(n=len(GAR["items"]), ab=sum(1 for x in GAR["items"] if x["estado"] == "ABIERTA")),
    qa=dict(asp=sum(1 for x in QA["aspectos"]["rows"] if str(x["estado"]).upper().startswith("ABIERT")), ncr=sum(1 for x in QA["ncr"]["rows"] if str(x["estado"]).upper().startswith("ABIERT")),
            sol=sum(1 for x in QA["soltec"]["rows"] if str(x["estado"]).upper().startswith("ABIERT")), dcrit=sum(1 for x in QA["dossier"]["rows"] if str(x["estatus"]).upper() == "CRITICO")),
)
json.dump(dict(meta=META, tot=TOT, locs=out), open(os.path.join(HERE, "data_ruta.json"), "w", encoding="utf-8"), ensure_ascii=False, default=str)
print("locaciones:", len(out), "| en ruta del taladro:", sum(1 for x in out if x["ruta"]))
print("TOT:", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'aliados'} for k, v in TOT.items()}, ensure_ascii=False))
for x in out[:40]:
    print(f"{x['loc']:24} {x['fr'][:4]} ready={x['ready']} | " + " ".join(f"{k}:{v['st']}" for k, v in x["S"].items()) + f" | alertas {len(x['al'])}")
cov = {k: sum(1 for x in out if x["S"][k]["st"] != "na") for k in out[0]["S"]}
print("cobertura por etapa (locaciones con datos):", cov)
