import sys, os, re, common

args = sys.argv[1:]

directories = "Inferno Purgatorio Paradiso"
once   = False
retry  = True
show   = True
needsp = False
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
    elif args[i] == "--need-space":
        needsp = True
        args.pop(i)
    elif args[i] == "-d" and len(args) > i + 1:
        directories = args.pop(i + 1)
        args.pop(i)
    else:
        i += 1

if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} italian-dir output-dir language", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    print("  --need-space: require at least one space in each line", file=sys.stderr)
    sys.exit(1)

itdir, outdir, language = args
checklen = 6 if " and " in language else 3
if not os.path.exists(outdir):
    os.mkdir(outdir)

import gemini

it = []
current = 0
directory = ""
canto = 0

history = []
for i in range(1, 5):
    fxml = os.path.join(outdir, "inferno", f"{i:02}.xml")
    if os.path.exists(fxml):
        history = common.unzip(common.read_queries(fxml))
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
    def check(r):
        if len(r) > len(prompt) * checklen:
            return f"Response too long: ({len(r)} > {len(prompt) * checklen})"
        if needsp:
            for line in r.split("\n"):
                if m := re.match(r"(\d+)", line):
                    text = line[m.end():]
                    if not text.startswith(" ") or " " not in text[1:]:
                        return f"Too few spaces: {repr(r)}"
        return None
    return gemini.query(prompt, info, show, retry, check)

for directory in directories.split():
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
            q = send_lines(length, f"Please translate each line literally into {language}.")
            queries.append(q)
            current += length
        common.write_queries(xml, queries, count=len(queries))
        if once:
            sys.exit(0)
