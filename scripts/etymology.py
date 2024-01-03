import sys, os, re, common

args = sys.argv[1:]

derived = "Latin, Greek, Germanic"
fields = [1]

directories = common.directories
init_xml = "init.xml"
interval = 10
once  = False
retry = True
show  = True

i = 0
while i < len(args):
    if args[i] == "-e" and len(args) > i + 1:
        derived = args.pop(i + 1)
        args.pop(i)
    elif args[i] == "-f" and len(args) > i + 1:
        tmp = args.pop(i + 1).strip()
        fields = [int(f) for f in tmp.split(",")] if tmp else []
        args.pop(i)
    elif args[i] == "-d" and len(args) > i + 1:
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

if len(args) < 3:
    print(f"Usage: python {sys.argv[0]} language word-dir output-dir [fix ...]", file=sys.stderr)
    print("  -e: specify etymology language(s)", file=sys.stderr)
    print("  -f: specify field to column 2 (0-based, comma separated)", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
    print("  -i: specify init.xml", file=sys.stderr)
    print("  -n: specify interval (default 10)", file=sys.stderr)
    print("  -1: just do one canto", file=sys.stderr)
    print("  --no-retry: don't retry queries", file=sys.stderr)
    print("  --no-show: don't show queries and responses", file=sys.stderr)
    sys.exit(1)

language, worddir, outdir, *fix_files = args
if not os.path.exists(outdir):
    os.mkdir(outdir)
fixes = common.read_fixes(*fix_files)

import gemini

prompt_template = " ".join([
    'For each row in the table, look up the etymology of the word.',
    f'In the "Derived" column, write {derived}, etc.',
    'In the "Etymology" column, fill in the corresponding word in Greek, Latin, or others,',
    'but leave blank if unknown.'
])

def send(query):
    prompt = prompt_template
    if not query.result:
        q = common.query()
        q.info = query.info
        q.prompt = prompt
        q.error = "(skip)"
        return q
    table = []
    for i, row in enumerate(common.read_table(query.result)):
        rowf = [row[f] for f in fields]
        if i == 0:
            head = " | " + " | ".join(rowf[1:]) if len(rowf) > 1 else ""
            table.append(f"| {language}{head} | Derived | Etymology |")
        elif i == 1:
            table.append("|" + "---|" * (len(fields) + 2))
        else:
            table.append(f"| " + " | ".join(rowf) + " | | |")
    prompt += "\n\n"
    prompt += "\n".join(table)
    return gemini.query(prompt, query.info, show, retry)

if os.path.exists(init_xml):
    init_qs = common.read_queries(init_xml)
    prompt_template = init_qs[0].prompt.split("\n")[0]
else:
    print(f"making {init_xml}...")
    gemini.init()
    inferno1 = common.read_queries(os.path.join(worddir, "inferno", "01.xml"))
    q = send(inferno1[0])
    if not q.result:
        print("Abort.", file=sys.stderr)
        sys.exit(1)
    init_qs = [q]
    common.write_queries(init_xml, init_qs, count=len(init_qs))
history = common.unzip(init_qs)

for directory in directories:
    diru = directory[0].upper() + directory[1:]
    worddir2 = os.path.join(worddir, directory)
    if not os.path.exists(worddir2):
        continue
    outdir2 = os.path.join(outdir, directory)
    if not os.path.exists(outdir2):
        os.mkdir(outdir2)
    files = [
        (int(m.group(1)), os.path.join(worddir2, f))
        for f in sorted(os.listdir(worddir2))
        if (m := re.match(r"(\d+)\.xml", f))
    ]
    for canto, file in files:
        xml = os.path.join(outdir2, f"{canto:02}.xml")
        if os.path.exists(xml):
            continue
        print()
        print(f"# {diru} Canto {canto}")
        queries = common.read_queries(file)
        qs = []
        for query in queries:
            if not (0 <= gemini.chat_count < interval):
                gemini.init(history)
            if not query.result and query.info in fixes:
                for q in fixes[query.info]:
                    qs.append(send(q))
            else:
                qs.append(send(query))
        common.write_queries(xml, qs, count=len(qs))
        if once:
            sys.exit(0)
