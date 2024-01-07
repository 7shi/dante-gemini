import sys, os, re, common, xml7shi

def get_sample(xml, n=1):
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

def type1(topdir, filename):
    tdir = os.path.join(topdir, "translate")
    texts = []
    it = []

    for d in os.listdir(tdir):
        lang, it, ts = get_sample(f"{tdir}/{d}/{filename}", 2)
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

def type2(topdir, filename):
    dirs = [os.path.join(topdir, d) for d in ["word", "word-tr", "etymology"]]
    langs = {}
    for lc in os.listdir(dirs[0]):
        mk = os.path.join(dirs[0], lc, "Makefile")
        if not os.path.exists(mk):
            continue
        lang = common.read_defs(mk).get("LANG")
        if not lang:
            print(f"no LANG in {mk}", file=sys.stderr)
            continue
        print(lc, lang, file=sys.stderr)
        files = [f"{d}/{lc}/{filename}" for d in dirs]
        index = 1 if lc == "eo" else 0
        it = common.read_tables(*files, index)
        _, lines, table = next(it)
        header = table[0]
        tables = common.split_table(lines, table)
        langs[lang] = (lines, header, tables)
    sp = ["Italian", "English"]
    for lang in sp + sorted(set(langs) - set(sp)):
        lines, header, tables = langs[lang]
        print()
        print("###", lang)
        for i in range(3 if lc in sp else 1):
            print()
            print(common.write_md(lines[i], header, tables[i]), end="")

if __name__ == "__main__":
    args = sys.argv[1:]
    filename = "inferno/01.xml"
    if len(args) > 1 and args[0] == "-f":
        filename = args[1]
        args = args[2:]
    if len(args) != 1:
        print(f"Usage: python {sys.argv[0]} [-f dir/xml] top-dir", file=sys.stderr)
        sys.exit(1)
    type2(args[0], filename)
