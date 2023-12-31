import sys, os, re, common

args = sys.argv[1:]

directories = common.directories
init_xml = "init.xml"
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
        directories = args.pop(i + 1).split()
        args.pop(i)
    elif args[i] == "-i" and len(args) > i + 1:
        init_xml = args.pop(i + 1)
        args.pop(i)
    else:
        i += 1

if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} language italian-dir output-dir", file=sys.stderr)
    print("  -i: specify init.xml", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    print("  --need-space: require at least one space in each line", file=sys.stderr)
    sys.exit(1)

language, itdir, outdir = args
checklen = 6 if " and " in language else 3
if not os.path.exists(outdir):
    os.mkdir(outdir)

import gemini

it = []
current = 0
directory = ""
canto = 0

def send_lines(line_count, *plines):
    global current
    diru = directory[0].upper() + directory[1:]
    info = f"[{diru} Canto {canto}] {current + 1}/{len(it)}"
    prompt = " ".join(plines)
    for i in range(line_count):
        if i == 0 or current % 3 == 0:
            prompt += "\n"
        line = f"{current + 1} {it[current]}"
        prompt += "\n" + line
        current += 1
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

prompt = f"Please translate each line literally into {language}."
if os.path.exists(init_xml):
    init_qs = common.read_queries(init_xml)
else:
    print(f"making {init_xml}...")
    gemini.init()
    directory = "inferno"
    canto = 1
    with open(os.path.join(itdir, directory, "01.txt"), "r", encoding="utf-8") as f:
        it = [l for line in f if (l := line.strip())]
    init_qs = [send_lines(length, prompt) for length in [3, 6]]
    common.write_queries(init_xml, init_qs, count=len(init_qs))
history = common.unzip(init_qs)

for directory in directories:
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
        qs = []
        while current < len(it):
            if len(qs) % 10 == 0:
                gemini.init(history)
            length = min(3, len(it) - current)
            while current + length < len(it) and not it[current + length - 1].endswith("."):
                length += 1
            qs.append(send_lines(length, prompt))
        common.write_queries(xml, qs, count=len(qs))
        if once:
            sys.exit(0)
