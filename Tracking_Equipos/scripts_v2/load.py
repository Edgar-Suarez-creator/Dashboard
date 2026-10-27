import openpyxl,warnings,re,datetime,json,pickle,os
warnings.simplefilter('ignore')
FILES=[('M3','M3.xlsx'),('M4','M4P.xlsx'),('M4','M4E.xlsx'),('M5','M5.xlsx')]
def sheet(f,name):
    ws=openpyxl.load_workbook(f,read_only=True,data_only=True)[name]
    it=ws.iter_rows(values_only=True); H=[re.sub(r'\s+',' ',str(h or '')).strip() for h in next(it)]
    return H,[r for r in it if any(v not in (None,'') for v in r)]
if not os.path.exists('raw.pkl'):
    raw={}
    for m,f in FILES:
        for sh in ['GENERAL','ESTADO ODB','ALERTAS']: raw[(f,sh)]=sheet(f,sh)
    pickle.dump(raw,open('raw.pkl','wb'))
raw=pickle.load(open('raw.pkl','rb'))
def old():
    D=json.load(open('D.json')); C=D['cols']; n=D['n']; out=[]
    for i in range(n):
        o={}
        for k,v in C['v'].items():
            x=v[i]
            if x is None: continue
            if k in C['d']: x=C['d'][k][x]
            o[k]=x
        out.append(o)
    return D,out
