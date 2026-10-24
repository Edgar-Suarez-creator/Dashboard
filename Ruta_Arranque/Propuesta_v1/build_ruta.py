import os, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
css = re.search(r"<style>(.*?)</style>", open(r"C:\Users\edgar.suarez\Dashboard\Control_Dossiers_AC1-HC1\Exteriores\Propuesta_v2\template_v3.html", encoding="utf-8").read(), re.S).group(1)
tpl = open(os.path.join(HERE, "template_ruta.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(HERE, "data_ruta.json"), encoding="utf-8"))
data["locs"] = [x for x in data["locs"] if x["loc"] != "CASE-0000"]
html = tpl.replace("/*__CSS__*/", css).replace("const DATA = __DATA__;", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")
out = os.path.join(HERE, "Dashboard_Ruta_Arranque.html"); open(out, "w", encoding="utf-8").write(html)
print("OK", out, f"{os.path.getsize(out):,} bytes")
