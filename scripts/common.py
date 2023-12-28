import xml7shi

directories = ["inferno", "purgatorio", "paradiso"]

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
