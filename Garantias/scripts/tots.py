import statistics
def tots(G):
    ab=[r for r in G if r['estado']=='ABIERTA']; ce=[r for r in G if r['estado']=='CERRADA']
    du=[r['duracion'] for r in ce if r['duracion'] is not None]; di=[r['dias'] for r in ab if r['dias'] is not None]
    t=dict(n=len(G),abiertas=len(ab),cerradas=len(ce),sin=len(G)-len(ab)-len(ce),
      pct_cierre=round(len(ce)/len(G)*100,1),dur_media=round(sum(du)/len(du),1),dur_mediana=statistics.median(du),
      aging_medio=round(sum(di)/len(di),1),ab_180=sum(d>180 for d in di),ab_365=sum(d>365 for d in di),
      proveedores=len({r['proveedor'] for r in G if r['proveedor']}),prov_abiertas=len({r['proveedor'] for r in ab if r['proveedor']}))
    for m in ('M3','M4'): t['n_'+m]=sum(r['mod']==m for r in G); t['ab_'+m]=sum(r['mod']==m for r in ab)
    for d in ('Eléctrica','I&C','Mecánica','Civil'): t['n_'+d]=sum(r['disc']==d for r in G); t['ab_'+d]=sum(r['disc']==d for r in ab)
    t['alto']=sum(r['nivel'] in ('ALTO','CRÍTICO') for r in ab)
    return t
