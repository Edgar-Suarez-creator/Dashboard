import json,sys,datetime as dt
from extract import extract
from tots import tots
html,xlsx,today,fuente,out=sys.argv[1:6]
MES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
lf=lambda iso:(lambda x:f"{x.day} de {MES[x.month-1]} de {x.year}")(dt.date.fromisoformat(iso))
s=open(html,encoding='utf-8').read(); dec=json.JSONDecoder()
i=s.index('const DATA = ')+13; D,ie=dec.raw_decode(s,i)
j=s.index('const PREV = ')+13; P,je=dec.raw_decode(s,j)
old={r['key']:r for r in D['items']}
G=extract(xlsx,today)
for r in G:
    o=old.get(r['key'])
    r['nueva']=o is None
    r['cerrada_desde_corte']=bool(o and o['estado']=='ABIERTA' and r['estado']=='CERRADA')
    r['reabierta']=bool(o and o['estado']=='CERRADA' and r['estado']=='ABIERTA')
    r['bitacora_nueva']=bool(o and r['estado']=='ABIERTA' and (o.get('bitacora') or '')!=(r.get('bitacora') or ''))
    r['estado_ant']=o['estado'] if o else None
    r['nivel_ant']=o['nivel'] if (o and o['nivel']!=r['nivel']) else None
nk={r['key'] for r in G}
ret=[dict(fila=o['fila'],odb=o['odb'],proveedor=o['proveedor'],reporte=o['reporte'],estado=o['estado'],tipo=o['tipo'],disc=o['disc']) for k,o in old.items() if k not in nk]
otros=[dict(odb=r['odb'],proveedor=r['proveedor'],de=r['estado_ant'],a=r['estado']) for r in G if r['estado_ant'] and r['estado_ant']!=r['estado'] and not r['cerrada_desde_corte'] and not r['reabierta']]
ND=dict(generated_at=dt.datetime.now().strftime('%Y-%m-%d %H:%M'),today=today,corte=lf(today),fuente=fuente,items=G)
NP=dict(corte_ant=D['corte'],corte_act=lf(today),ref_ant=D['today'],ref_act=today,archivo_ant=D['fuente'],archivo_act=fuente,
  tot_ant=tots(D['items']),tot_act=tots(G),retiradas=ret,n_nuevas=sum(r['nueva'] for r in G),n_cerradas=sum(r['cerrada_desde_corte'] for r in G),
  n_reabiertas=sum(r['reabierta'] for r in G),n_bitacora=sum(r['bitacora_nueva'] for r in G),n_nivel=sum(r['nivel_ant'] is not None for r in G),otros_estado=otros)
js=lambda o:json.dumps(o,ensure_ascii=False).replace('</','<\\/')
s=s[:i]+js(ND)+s[ie:j]+js(NP)+s[je:]
open(out,'w',encoding='utf-8').write(s)
print(json.dumps({k:v for k,v in NP.items() if k not in('tot_ant','tot_act')},ensure_ascii=False,indent=0)[:3000])
print('ANT',NP['tot_ant']);print('ACT',NP['tot_act'])
print('nuevas',[(r['fila'],r['reporte'],r['proveedor']) for r in G if r['nueva']])
print('cerradas',[(r['fila'],r['vip'],r['fecha_cierre']) for r in G if r['cerrada_desde_corte']])
print('bit',[(r['fila'],r['vip']) for r in G if r['bitacora_nueva']])
