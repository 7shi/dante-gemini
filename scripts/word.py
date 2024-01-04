import sys, os, re, common

args = sys.argv[1:]

directories = common.directories
init_xml = "init.xml"
interval = 10
once  = False
retry = True
show  = True

i = 0
while i < len(args):
    if args[i] == "-d" and len(args) > i + 1:
        directories = args.pop(i + 1).split()
        args.pop(i)
    elif args[i] == "-i" and len(args) > i + 1:
        init_xml = args.pop(i + 1)
        args.pop(i)
    elif args[i] == "-n" and len(args) > i + 1:
        interval = int(args.pop(i + 1))
        args.pop(i)
    elif args[i] == "-1":
        once = True
        args.pop(i)
    elif args[i] == "--no-retry":
        retry = False
        args.pop(i)
    elif args[i] == "--no-show":
        show = False
        args.pop(i)
    else:
        i += 1

if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} language source-dir output-dir", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
    print("  -i: specify init.xml", file=sys.stderr)
    print("  -n: specify interval (default 10)", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    sys.exit(1)

language, srcdir, outdir = args
if not os.path.exists(outdir):
    os.mkdir(outdir)

init_qs = common.read_queries(init_xml)
history = common.unzip(init_qs)
if init_qs[0].prompt[:8] in ["This tex", "Create a"]:
    init_ps = [init_qs[0].prompt]
else:
    init_ps = [init_qs[1].prompt]

import gemini

def send(text, info):
    prompt = "Create a word table.\n\n" + text
    return gemini.query(prompt, info, show, retry)

for directory in directories:
    diru = directory[0].upper() + directory[1:]
    path_s = os.path.join(srcdir, directory)
    path_o = os.path.join(outdir, directory)
    if not os.path.exists(path_o):
        os.mkdir(path_o)
    nmax = max(int(m.group(1)) for f in os.listdir(path_s) if (m := re.match(r"(\d+)\.", f)))
    for canto in range(1, nmax + 1):
        xml = os.path.join(path_o, f"{canto:02}.xml")
        if os.path.exists(xml):
            continue
        print()
        print(f"# {diru} Canto {canto}")
        srcs, src_lines = common.read_source(os.path.join(path_s, f"{canto:02}"), language)
        lmax = max(src_lines)
        qs = []
        for lines in srcs:
            text = "\n".join(lines)
            if not (m := re.match(r"(\d+) ", text)):
                continue
            if not (0 <= gemini.chat_count < interval):
                gemini.init(history, init_ps)
            info = f"[{diru} Canto {canto}] {m.group(1)}/{lmax}"
            q = send(text, info)
            if q:
                qs.append(q)
        common.write_queries(xml, qs, count=len(qs))
        if once:
            sys.exit(0)
