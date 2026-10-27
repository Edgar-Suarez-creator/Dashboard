"""Genera Dashboard_Tracking_Equipos.html con el nuevo corte, conservando el corte anterior como PREV."""
import json, sys, datetime as dt, collections
from load import raw, FILES, old
import extract2
HTML = sys.argv[1]; HOY = sys.argv[2]
NOMBRES = {'M3.xlsx': 'ECU17049_CAÑO SUR_ESTE_MÓDULO_3.xlsx', 'M4P.xlsx': 'ECU21212 CAÑO_ SUR_ ESTE MODULO 4_P.xlsx',
           'M4E.xlsx': 'ECU21212_CAÑO_SUR_ESTE_MODULO_4-E.xlsx', 'M5.xlsx': 'ECU24091_DESARROLLO_INTEGRAL_CSE_M5.xlsx'}
D, O = old()
TAL = {o['loc']: (o['tal'], o.get('tin')) for o in O if o.get('loc') and o.get('tal')}
srcs = [(m, {sh: raw[(f, sh)] for sh in ['GENERAL', 'ESTADO ODB', 'ALERTAS']}) for m, f in FILES]
items, canc, _ = extract2.extract(srcs, HOY, TAL)
odbs = extract2.build_odb(srcs, items); als = extract2.build_alertas(srcs)
NUMK = {'q', 'rec', 'pen', 'dv'}
def encode(rows, keys):
    v, d = {}, {}
    for k in keys:
        col = [r.get(k) for r in rows]
        if k in NUMK: v[k] = col
        else:
            u = sorted({x for x in col if x is not None}, key=str); ix = {x: i for i, x in enumerate(u)}
            d[k] = u; v[k] = [ix[x] if x is not None else None for x in col]
    return dict(v=v, d=d)
keys = list(D['cols']['v'].keys())
for x in items:
    for k in x:
        if k not in keys: keys.append(k)
subs = collections.defaultdict(set); off = 0
for (m, f) in FILES:
    pass
fuentes = []
for m, f in FILES:
    sp = sorted({extract2.subname(d.get('Sub Proyecto')) for d in extract2.rows(*raw[(f, 'GENERAL')]) if d.get('Sub Proyecto')})
    fuentes.append(dict(mod=m, archivo=NOMBRES[f], fecha=HOY, subs=sp))
ND = dict(hoy=HOY, generado=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), fuentes=fuentes, odb=odbs, alertas=als,
          canceladas=dict(sorted(canc.items())), n=len(items), corte=HOY, cols=encode(items, keys))
PK = list(json.load(open('P.json'))['cols']['v'].keys())
NP = dict(corte=D['corte'], n=len(O), cols=encode(O, PK), alertas=[dict(cod=a['cod'], mod=a['mod'], abierta=a['abierta']) for a in D['alertas']])
s = open(HTML, encoding='utf-8').read(); dec = json.JSONDecoder()
i = s.index('const DATA = ') + 13; _, ie = dec.raw_decode(s, i)
j = s.index('const PREV = ') + 13; _, je = dec.raw_decode(s, j)
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
s = s[:i] + js(ND) + s[ie:j] + js(NP) + s[je:] if i < j else s[:j] + js(NP) + s[je:i] + js(ND) + s[ie:]
open(sys.argv[3], 'w', encoding='utf-8').write(s)
# resumen
c = collections.Counter
eq = [x for x in items if x.get('eq')]
def kp(L):
    n = len(L); comp = sum(1 for x in L if not x['et'].startswith('Planeación')); rec = sum(1 for x in L if x['et'] == 'Recibido')
    l90 = sum(1 for x in L if x['ll'] in ('≤30 días', '31–90 días')); ven = sum(1 for x in L if x['ll'] == 'ETA vencida')
    return dict(n=n, comprado=round(comp / n * 100, 1), recibido=round(rec / n * 100, 1), llegan90=l90, vencidas=ven)
print('ACT', kp(items), 'equipos', len(eq), 'alertas abiertas', sum(a['abierta'] for a in als), 'odb', len(odbs))
print('ANT', kp(O), 'equipos', sum(1 for o in O if o.get('eq')), 'alertas abiertas', sum(a['abierta'] for a in D['alertas']), 'odb', len(D['odb']))
print('etapas', c(x['et'] for x in items)); print('etapas ant', c(o['et'] for o in O))
print('ll', c(x['ll'] for x in items))
