"""Extractor v2 reconstruido: tracking M3/M4/M5 (hojas GENERAL, ESTADO ODB, ALERTAS) -> DATA del dashboard."""
import re, datetime as dt, collections
def iso(v):
    if isinstance(v, dt.datetime): return v.date().isoformat() if v.year > 1990 else None
    if isinstance(v, dt.date): return v.isoformat()
    if isinstance(v, str):
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", v)
        if m:
            try: return dt.date(int(m[3]), int(m[2]), int(m[1])).isoformat()
            except ValueError: return None
    return None
def num(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0
def s(v): return re.sub(r"\s+", " ", str(v)).strip() if v not in (None, "") else ""
def dd(a, b): return (dt.date.fromisoformat(a) - dt.date.fromisoformat(b)).days
ES = {'MEC._ACCESORIOS':'Mec. Accesorios','MEC._VÁLVULAS':'Mec. Válvulas','MEC._TUBERÍA':'Mec. Tubería','INST._Y_CONTROL':'Inst. y Control','CABLES':'Cables',
      'ELÉCTRICA':'Eléctrica','MEC._ROTATIVA':'Mec. Rotativa','SEG._Y_SCI':'Seg. y SCI','MEC._ESTÁTICA':'Mec. Estática','CONSUMIBLES':'Consumibles','UN._PAQUETE':'Un. Paquete'}
def etapa(est, q, rec):
    e = est.lower()
    if e.startswith('recib') or (rec > 0 and rec >= q): return 'Recibido'
    if e.startswith('en tránsito') or e.startswith('en transito'): return 'En tránsito'
    if e.startswith('en fabric') or e.startswith('suma global'): return 'En fabricación'
    if 'pre-contractual' in e or 'precontractual' in e: return 'Planeación PC'
    if 'abastecimiento' in e: return 'Planeación ABA'
    return 'Planeación PY'
EXCL_TIPO = re.compile(r"FOTOVOLT|ILUMIN|LUMINAR|PANEL SOLAR|DISPLAY|TARJETA|RELAY|REPUEST|BOQUILLA|FILTRO EN Y|FILTRO TEMPORAL|ESCOTILLA|TRAMPA|MANGUERA|ABRAZADERA|CONDUIT|CONDULETA|CONECTOR|PERNO|REDUCCI|RIEL|ACCESORIO|BANDEJA|LICENCIA|PATCHCORD|PIG TAIL|SFP|KIT DE AMPLIACION|SERVICIOS|CONFIGURACI|PRUEBAS|INTEGRACI|ACTUALIZACI"
                       r"|^DPS$|PROTECTOR DE AVES|CLAMP|^LAMP|TERMINAL|^CABLE|CIRCUIT|^MODULE|^PLATE|^SWITCH$|CONVERTIDOR|MASTIL|O-RING|PARTS KIT|SPARE PARTS"
                       r"|^CAJAS?\b|CAJA DE COMUNICACIONES|^FILTRO$|STRAINER|AMPLIACIÓN EN TABLEROS", re.I)
CAT = [("Transformadores", lambda t, tm: tm == "TRANSFORMADORES"),
       ("Skids VFD/SUT y E-House", lambda t, tm: tm == "EQ. ELÉCTRICO SKID"),
       ("Tableros y celdas", lambda t, tm: tm in ("TABLEROS Y CEL. ELÉC", "TABLEROS DE CONTROL") or (tm == "MAT. INST. Y CONTROL" and re.search(r"GABINETE|CENTRO MANIOBRA|DATA CENTER|TABLERO", t))),
       ("Variadores", lambda t, tm: tm == "VARIADORES"), ("Otros eléctricos", lambda t, tm: tm == "OTROS EQUIPOS ELÉCTRICOS"),
       ("Bombas y rotativos", lambda t, tm: tm == "EQ. ROTATIVO"), ("Recipientes y estáticos", lambda t, tm: tm in ("RECIPIENTE A PRESIÓN", "EQ. ESTÁTICO"))]
def categoria(tipo, tm):
    if EXCL_TIPO.search(tipo): return None
    for name, f in CAT:
        if f(tipo.upper(), tm): return name
    return None
def loc(*vals):
    for v in vals:
        m = re.search(r"\b(CASE|CUMA|EMBR|WDCS|CMO)[\s\-_]*0*(\d{1,4})", str(v or ""), re.I)
        if m: return f"{m.group(1).upper()}-{int(m.group(2)):04d}"
    return None
def subname(x): return s(x).title()
FR = 'Fecha requerida por el proyecto para llegada del material (dd/mm/aaaa)2'
def rows(H, R):
    for r in R: yield {h: (r[i] if i < len(r) else None) for i, h in enumerate(H)}

def extract(sources, hoy, taladro):
    """sources: list of (mod, {'GENERAL':(H,R),'ESTADO ODB':(H,R),'ALERTAS':(H,R)}); taladro: loc -> (tal, tin)"""
    items, odbs, alertas, canc = [], [], [], collections.Counter()
    EO = {}
    for mod, sh in sources:
        for d in rows(*sh['ESTADO ODB']):
            if s(d.get('ODB')): EO[(mod, s(d['ODB']))] = d
    for mod, sh in sources:
        for d in rows(*sh['GENERAL']):
            est = s(d.get('Estado del Proceso de Aprovisionamiento')); sp = subname(d.get('Sub Proyecto'))
            if est.lower().startswith('cancel') or s(d.get('ESTADO DE LA ODB')).upper() == 'CANCELADA':
                canc[f"{mod}|{sp}"] += 1; continue
            q = num(d.get('Cantidad por ítem')); rec = num(d.get('Cantidad recibida en Sitio')); pen = num(d.get('Cantidad Pendiente por Recibir'))
            et = etapa(est, q, rec)
            odb = s(d.get('No. Orden de Compra')); e = EO.get((mod, odb))
            eta = iso(d.get('Fecha Proyectada de Recibo en sitio o Fecha Real Recibido en Sitio'))
            fsap = iso(d.get('Fecha de Recibido en SAP'))
            foc = iso(d.get('Fecha Entrega OC')) or (iso(e.get('FECHA DE ENTREGA ODB')) if e else None)
            fre = iso(e.get('FECHA REQUERIDA POR EL PROYECTO')) if e else None
            tm = s(d.get('Tipología Material')).upper(); ti = s(d.get('Tipo de material'))
            a1, a2, tag = s(d.get('Área de instalación 1 (Sistema)')), s(d.get('Área de instalación 2 (Sub-Sistema)')), s(d.get('TAG'))
            if et == 'Recibido': ll = 'Recibido'; pen = 0
            elif pen <= 0: pen = max(q - rec, 0) or q
            if et == 'Recibido': pass
            elif et.startswith('Planeación'): ll = 'Sin compra'
            elif not eta: ll = 'Sin fecha'
            elif eta < hoy: ll = 'ETA vencida'
            elif dd(eta, hoy) <= 30: ll = '≤30 días'
            elif dd(eta, hoy) <= 90: ll = '31–90 días'
            else: ll = '>90 días'
            l = loc(a1, tag, a2); t = taladro.get(l) if l else None
            x = dict(m=mod, sp=sp, mr=s(d.get('Código de MR')), imr=s(d.get('Ítem MR')), de=s(d.get('Descripción del ítem'))[:90], q=q, u=s(d.get('Unidad del ítem')),
                     et=et, ll=ll, odb=odb, eta=eta, eq=categoria(ti, tm), ti=ti, pv=s(d.get('Proveedor')), tp=tm.title(), es=ES.get(s(d.get('Especialidad')).upper(), s(d.get('Especialidad')).title()),
                     a1=a1, tag=tag, loc=l, eo=s(d.get('ESTADO DE LA ODB')).upper(), foc=foc, fre=fre, fsap=fsap, rec=rec, pen=pen,
                     tal=t[0] if t else None, tin=t[1] if t else None)
            ref = fsap if (et == 'Recibido' and fsap) else eta
            x['dv'] = dd(fre, ref) if (fre and ref) else None
            if et != 'Recibido':
                x.update(a2=a2, dia=s(d.get('Diámetro (in)')), adq=s(d.get('Tipo de Adquisición')), ins=s(d.get('Estado de Inspección del Ítem')),
                         exp=s(d.get('No. del Expediente, ID Compra SIMBO')), sol=s(d.get('No. de Solped')), sap=s(d.get('Código SAP')), ioc=s(d.get('Ítem de la OC')),
                         flib=iso(d.get('Fecha final de liberación del ítem')), ob=s(d.get('Observaciones Proceso de Compra')))
            items.append({k: v for k, v in x.items() if v not in (None, '')})
    return items, canc, EO

def pnum(v):
    if v in (None, ''): return None
    try:
        f = float(v); f = f * 100 if 0 < f <= 1 else f
        return round(f) if abs(f - round(f)) < 1e-9 else round(f, 1)
    except (TypeError, ValueError): return None

def build_odb(sources, items):
    by = collections.defaultdict(list)
    for x in items:
        if x.get('odb'): by[(x['m'], x['odb'])].append(x)
    out, seen = [], set()
    for mod, sh in sources:
        for d in rows(*sh['ESTADO ODB']):
            odb = s(d.get('ODB'))
            if not odb or (mod, odb) in seen: continue
            seen.add((mod, odb)); L = by.get((mod, odb), [])
            if not L: continue
            ab = [x for x in L if x['et'] != 'Recibido']
            f_proy, f_req = iso(d.get('FECHA PROYECTADA O ESTIMADA')), iso(d.get('FECHA REQUERIDA POR EL PROYECTO'))
            etas = [x['eta'] for x in ab if x.get('eta')]
            sp = L[-1]['sp']
            out.append(dict(mod=mod, odb=odb, tipo=s(d.get('TIPO DE MATERIAL'))[:90], prov=s(d.get('PROVEEDOR')), f_ent=iso(d.get('FECHA DE ENTREGA ODB')), f_proy=f_proy, f_req=f_req,
                            est=s(d.get('ESTADO ODB')).upper(), avance=s(d.get('AVANCE TRACKING'))[:420], insp=s(d.get('ESTADO DE INSPECCIÓN ODB')),
                            p_ing=pnum(d.get('%AVANCE INGENIERÍA')), p_mat=pnum(d.get('%AVANCE MATERIALES')), p_prod=pnum(d.get('%AVANCE PRODUCCIÓN')), p_ens=pnum(d.get('%AVANCE ENSAYOS')),
                            f_lib=iso(d.get('FECHA FINAL DE LIBERACIÓN ODB')), sub=s(d.get('Sub Proyecto')).upper(), sp=sp, n=len(L), n_ab=len(ab),
                            eq=any(x.get('eq') for x in L), eta=max(etas) if etas else None, dv=dd(f_req, f_proy) if (f_req and f_proy) else None))
    return out

def build_alertas(sources):
    out = []
    for mod, sh in sources:
        g = collections.OrderedDict()
        for d in rows(*sh['ALERTAS']):
            c = s(d.get('CODIGO ALERTA'))
            if c: g.setdefault(c, []).append(d)
        for c, L in g.items():
            cerr = any(s(d.get('ESTADO ALERTA')).upper() == 'CERRADA' for d in L)
            act = [d for d in L if s(d.get('ESTADO ALERTA')).upper() == 'CERRADA'] if cerr else [d for d in L if s(d.get('ESTADO ALERTA')).upper() != 'CERRADA']
            d = (act or L)[-1] if cerr else (act or L)[0]
            fc = [iso(x.get('FECHA DE CIERRE ESTADO O ALERTA')) for x in L if iso(x.get('FECHA DE CIERRE ESTADO O ALERTA'))]
            out.append(dict(mod=mod, cod=c, equipo=s(d.get('TIPO DE EQUIPO'))[:70], prov=s(d.get('PROVEEDOR'))[:50], odb=s(d.get('ODB')), item=s(d.get('ÍTEM')),
                            f_act=iso(d.get('FECHA DE ACTIVACIÓN')), f_cie=fc[0] if fc else None, desc=s(d.get('DESCRIPCIÓN ALERTA'))[:300],
                            nivel=s(d.get('ESTADO ALERTA')).upper(),
                            abierta=not cerr, cat=s(d.get('CATEGORIA')), sub=s(d.get('Sub Proyecto')).upper()))
    return out
