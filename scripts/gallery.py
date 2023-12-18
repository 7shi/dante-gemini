import sys, os, re, common, xml7shi

def get_sample(tdir, d, n=1):
    xml = os.path.join(tdir, d, "inferno", "01.xml")
    if not os.path.exists(xml):
        return "", [], []
    with open(xml, "r", encoding="utf-8") as f:
        xml = f.read()
    xr = xml7shi.reader(xml)
    texts1 = []
    texts2 = []
    for _ in range(n):
        q = common.parse(xr)
        if not (q.result and (m := re.search(r"into (.*)\.", q.prompt))):
            continue
        lang = m.group(1)
        if m := re.search(r" and (.*)", lang):
            lang = m.group(1)
        it = q.prompt.split("\n")[2:]
        if not (m := re.match(r"(\d+ )", it[0])):
            continue
        ln = m.group(1)
        lines = q.result.split("\n")
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith(ln):
                break
        if texts1:
            texts1.append("")
            texts2.append("")
        texts1 += it
        texts2 += lines[i : i + len(it)]
    return lang, texts1, texts2

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print(f"Usage: python {sys.argv[0]} translate-dir", file=sys.stderr)
        sys.exit(1)

    tdir = args[0]
    texts = []
    it = []

    for d in os.listdir(tdir):
        lang, it, ts = get_sample(tdir, d, 2)
        if lang:
            texts.append((lang, ts))

    texts.sort(key=lambda lang: lang)
    print("<table>")
    print("<tr><th>Language</th><th>Text</th></tr>")
    print("<tr><td>Italian</td><td>", "<br>".join(it), "</td></tr>", sep="")
    for lang, text in texts:
        attrs = ' dir="rtl" align="right"' if lang in ["Arabic", "Hebrew"] else ''
        print(f"<tr><td>{lang}</td><td{attrs}>", "<br>".join(text), "</td></tr>", sep="")
    print("</table>")
