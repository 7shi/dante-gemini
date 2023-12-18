import sys, os, re, xml7shi

args = sys.argv[1:]
if len(args) != 1:
    print(f"Usage: python {sys.argv[0]} translate-dir", file=sys.stderr)
    sys.exit(1)

tdir = args[0]
texts = []
it = ""

for d in os.listdir(tdir):
    xml = os.path.join(tdir, d, "inferno", "01.xml")
    if not os.path.exists(xml):
        continue
    with open(xml, "r", encoding="utf-8") as f:
        xml = f.read()
    xr = xml7shi.reader(xml)
    if not (xr.find("prompt") and xr.read()):
        continue
    prompt = xr.text.strip()
    if not (m := re.search(r"into (.*)\.", prompt)):
        continue
    lang = m.group(1)
    if m := re.search(r" and (.*)", lang):
        lang = m.group(1)
    if not it:
        it = prompt.split("\n")[2:5]
    if xr.read() and xr.tag == "error":
        if not (xr.read() and xr.read()):
            continue
    if not (xr.tag == "result" and xr.read()):
        continue
    lines = xr.text.strip().split("\n")
    for i in range(len(lines), 0, -1):
        if lines[i - 1].startswith("1 "):
            break
    texts.append((lang, xr.text.strip().split("\n")[i - 1 : i + 2]))

texts.sort(key=lambda lang: lang[0])
print("<table>")
print("<tr><th>Language</th><th>Text</th></tr>")
print("<tr><td>Italian</td><td>", "<br>".join(it), "</td></tr>", sep="")
for lang, text in texts:
    attrs = ' dir="rtl" align="right"' if lang in ["Arabic", "Hebrew"] else ''
    print(f"<tr><td>{lang}</td><td{attrs}>", "<br>".join(text), "</td></tr>", sep="")
print("</table>")
