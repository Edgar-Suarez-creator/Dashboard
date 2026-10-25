"""template_at.html + data_at.json (+ CSS común de los dashboards) -> Ejecutable/Dashboard_Asistencias_Tecnicas.html"""
import os, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
css = re.search(r"<style>(.*?)</style>", open(r"C:\Users\edgar.suarez\Dashboard\Control_Dossiers_AC1-HC1\Exteriores\Propuesta_v2\template_v3.html", encoding="utf-8").read(), re.S).group(1)
tpl = open(os.path.join(HERE, "template_at.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(HERE, "data_at.json"), encoding="utf-8"))
html = tpl.replace("/*__CSS__*/", css).replace("const DATA = __DATA__;", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")
assert "__DATA__" not in html
out_dir = os.path.join(os.path.dirname(HERE), "Ejecutable"); os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "Dashboard_Asistencias_Tecnicas.html"); open(out, "w", encoding="utf-8").write(html)
print("OK", out, f"{os.path.getsize(out):,} bytes")
