import sys, os, re, xml7shi, common

args = sys.argv[1:]

once   = False
retry  = True
show   = True
chklen = False
i = 0
while i < len(args):
    if args[i] == "-1":
        once = True
        args.pop(i)
    elif args[i] == "--no-retry":
        retry = False
        args.pop(i)
    elif args[i] == "--no-show":
        show = False
        args.pop(i)
    elif args[i] == "--check-length":
        chklen = True
        args.pop(i)
    else:
        i += 1

if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} italian-dir output-dir language", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    print("  --check-length: check that responses aren't too long", file=sys.stderr)
    sys.exit(1)

itdir, outdir, language = args
if not os.path.exists(outdir):
    os.mkdir(outdir)

import gemini

it = []
current = 0
directory = ""
canto = 0

history = None
for i in range(1, 5):
    fxml = os.path.join(outdir, "inferno", f"{i:02}.xml")
    if os.path.exists(fxml):
        with open(fxml, "r", encoding="utf-8") as f:
            xml = f.read()
        xr = xml7shi.reader(xml)
        qs = [common.parse(xr) for _ in range(2)]
        history = [
            qs[0].prompt,
            qs[0].result,
            qs[1].prompt,
            qs[1].result
        ]
        break

def send_lines(line_count, *plines):
    info = f"[{directory} Canto {canto}] {current + 1}/{len(it)}"
    prompt = " ".join(plines)
    for i in range(line_count):
        ln = current + i
        if i == 0 or ln % 3 == 0:
            prompt += "\n"
        line = f"{ln + 1} {it[ln]}"
        prompt += "\n" + line
    return gemini.query(prompt, info, show, retry, chklen)

def write(f, text):
    f.write(text.encode("utf_8"))

for directory in ["Inferno", "Purgatorio", "Paradiso"]:
    path = os.path.join(outdir, directory.lower())
    if not os.path.exists(path):
        os.mkdir(path)
    itfiles = [
        (int(m.group(1)), os.path.join(itdir, directory, f))
        for f in sorted(os.listdir(os.path.join(itdir, directory)))
        if (m := re.match(r"(\d+)\.txt", f))
    ]
    for canto, itf in itfiles:
        xml = os.path.join(path, f"{canto:02}.xml")
        if os.path.exists(xml):
            continue
        print()
        print(f"# {directory} Canto {canto}")
        with open(itf, "r", encoding="utf-8") as f:
            it = [l for line in f if (l := line.strip())]
        current = 0
        queries = []
        gemini.init(*history)
        while current < len(it):
            length = min(3, len(it) - current)
            while current + length < len(it) and not it[current + length - 1].endswith("."):
                length += 1
            q = send_lines(length, f"Please translate literally into {language}.")
            queries.append(q)
            current += length
        with open(xml, "wb") as f:
            write(f, '<?xml version="1.0" encoding="utf-8"?>\n')
            for q in queries:
                write(f, str(q))
        if once:
            sys.exit(0)
