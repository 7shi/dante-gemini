import sys, os, re, xml7shi

def escape(s):
    return s.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

class query:
    def __init__(self):
        self.prompt = None
        self.info   = None
        self.result = None
        self.error  = None
        self.retry  = False

    def __str__(self):
        s = "<query>\n"
        if self.info:
            s += f"<info>{escape(self.info)}</info>\n"
        attrs = ' retry="true"' if self.retry else ''
        s += f"<prompt{attrs}>\n{escape(self.prompt)}\n</prompt>\n"
        if self.error:
            attrs = ' result="true"' if self.result else ''
            s += f"<error{attrs}>\n{escape(self.error)}\n</error>\n"
        if self.result:
            s += f"<result>\n{escape(self.result)}\n</result>\n"
        return s + "</query>\n"

def parse(xr: xml7shi.reader):
    q = query()
    while xr.read():
        if xr.tag == "prompt":
            q.retry = xr.get("retry") == "true"
            if xr.read():
                q.prompt = xr.text.strip()
        elif xr.tag == "info" and xr.read():
            q.info = xr.text.strip()
        elif xr.tag == "error" and xr.read():
            q.error = xr.text.strip()
        elif xr.tag == "result" and xr.read():
            q.result = xr.text.strip()
        elif xr.tag == "/query":
            break
    return q

def read_queries(file):
    with open(file, "r", encoding="utf-8") as f:
        xml = f.read()
    xr = xml7shi.reader(xml)
    qs = []
    while xr.read():
        if xr.tag == "query":
            qs.append(parse(xr))
    return qs

def write(f, text="", end="\n"):
    f.write((str(text) + end).encode("utf_8"))

def write_queries(file, qs, **root_attrs):
    with open(file, "wb") as f:
        write(f, xml7shi.declaration)
        attrs = "".join(f' {k}="{v}"' for k, v in root_attrs.items())
        write(f, f"<queries{attrs}>")
        for q in qs:
            write(f, q, end="")
        write(f, "</queries>")

def unzip(qs):
    ret = []
    for q in qs:
        ret.append(q.prompt)
        ret.append(q.result)
    return ret

# table

def read_table(src):
    ret = []
    for line in src.split("\n"):
        if line.startswith("|"):
            ret.append([t.strip() for t in line.split("|")[1:-1]])
        elif ret:
            break
    if len(ret) > 1 and not re.match(r"-+$", ret[1][0]):
        ret.insert(1, ["---"] * len(ret[0]))
    return ret

abbrevs = {
    "singular": "sg.", "plural": "pl.",
    "masculine": "m.", "feminine": "f.", "neuter": "n.",
    "first": "1", "second": "2", "third": "3",
    "1st": "1", "2nd": "2", "3rd": "3",
}

def fix_cell(cell):
    cell = cell.strip()
    if cell in ["-", "n/a", "N/A"]:
        return ""
    ab = abbrevs.get(cell.lower())
    if ab:
        return ab
    return cell

def fix_table(lines):
    output = ""
    for line in lines.split("\n"):
        if line.endswith("\r"):
            line = line[:-1]
        if line.startswith("|"):
            data = [fix_cell(cell) for cell in line.split("|")]
            line = "|".join(data)
        output += line + "\n"
    return output.rstrip()

# source

def read_source(path, language=None):
    srcs = []
    src_lines = {}

    file = path
    if path.endswith(".txt") or os.path.exists(file := f"{path}.txt"):
        with open(file, "r", encoding="utf-8") as f:
            ln = 1
            lines = []
            for line in f:
                line = line.strip()
                if line:
                    line = f"{ln} {line}"
                    src_lines[ln] = line
                    ln += 1
                    lines.append(line)
                    if len(lines) == 3:
                        srcs.append(lines)
                        lines = []
            if lines:
                srcs.append(lines)
        return srcs, src_lines

    file = path
    if path.endswith(".xml") or os.path.exists(file := f"{path}.xml"):
        qs = read_queries(file)
        if qs and (m := re.search(r"/(\d+)", qs[0].info)):
            src_lines = {int(m.group(1)): None}
        for q in qs:
            if not q.result:
                continue
            r = q.result
            if language and language in r:
                r = r[r.find("\n", r.find(language)):]
            lines = []
            for line in (r.strip() + "\n").split("\n"):
                if m := re.match(r"(\d+)", line):
                    src_lines[int(m.group(1))] = line
                if line:
                    lines.append(line)
                if lines and (len(lines) == 3 or not line):
                    srcs.append(lines)
                    lines = []
    else:
        print(f"no source files found in {path}", file=sys.stderr)
    return srcs, src_lines

# fix

def read_fixes(*fix_files):
    ret = {}
    for f in fix_files:
        for q in read_queries(f):
            info = q.info
            if re.search(r"\+\d$", info):
                info = info[:-2]
            if info not in ret:
                ret[info] = []
            ret[info].append(q)
    return ret
