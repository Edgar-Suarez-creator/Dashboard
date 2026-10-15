"""Arma Dashboard_Tracking_Equipos.html: CSS del dashboard de Dossieres v3 + template_trk.html + data_trk.json"""
import os, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
css_src = open(r"C:\Users\edgar.suarez\Dashboard\Control_Dossiers_AC1-HC1\Propuesta_v2\template_v3.html", encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", css_src, re.S).group(1)
tpl = open(os.path.join(HERE, "template_trk.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(HERE, "data_trk.json"), encoding="utf-8"))
html = tpl.replace("/*__CSS__*/", css).replace("const DATA = __DATA__;", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")
out = os.path.join(HERE, "Dashboard_Tracking_Equipos.html")
open(out, "w", encoding="utf-8").write(html)
print("OK", out, f"{os.path.getsize(out):,} bytes")
