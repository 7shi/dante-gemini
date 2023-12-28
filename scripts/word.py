import sys, os, re, common

args = sys.argv[1:]

directories = common.directories
once  = False
show  = True
retry = True
i = 0
while i < len(args):
    if args[i] == "-d" and len(args) > i + 1:
        directories = args.pop(i + 1)
        args.pop(i)
    elif args[i] == "-1":
        once = True
        args.pop(i)
    elif args[i] == "--no-show":
        show = False
        args.pop(i)
    elif args[i] == "--no-retry":
        retry = False
        args.pop(i)
    else:
        i += 1

if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} italian-dir init-xml output-dir", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    sys.exit(1)

itdir, initxml, outdir = args
if not os.path.exists(outdir):
    os.mkdir(outdir)

init_qs = common.read_queries(initxml)
history = common.unzip(init_qs)

import gemini

it = []
current = 0
directory = ""
canto = 0

def send_lines(line_count, *plines):
    info = f"[{directory} Canto {canto}] {current + 1}/{len(it)}"
    ls = it[current:current+line_count]
    prompt = " ".join(plines) + "\n" + "\n".join(ls)
    def check(r):
        if "|---||" in r:
            return f"Table broken: {repr(r)}"
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
        while current < len(it):
            if current % 30 == 0:
                gemini.init(history, [init_qs[2].prompt])
            queries.append(send_lines(3, "Create a word table."))
            current += 3
        common.write_queries(xml, queries, count=len(queries))
        if once:
            sys.exit(0)
