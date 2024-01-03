import sys, os, re, common

args = sys.argv[1:]

translate = ["English", "Italian"]
fields = [[0], [1]]

directories = common.directories
init_xml = "init.xml"
interval = 10
once  = False
retry = True
show  = True

i = 0
while i < len(args):
    if args[i] == "-t" and len(args) > i + 1:
        translate = [l.strip() for l in args.pop(i + 1).split(",")]
        args.pop(i)
    elif args[i] == "-f" and len(args) > i + 1:
        fields = [[int(f) for f in fs.split("+")] for fs in args.pop(i + 1).split(",")]
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
    print("  -t: specify language to translate (comma separated)", file=sys.stderr)
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

def send(query):
    global fields
    flen = len(fields)
    colnum = ", ".join(str(flen + c + 1) for c in range(len(translate)))
    prompt = f"For each row in the table, fill in columns {colnum} with the direct translation of column 1."
    if not query.result:
        q = common.query()
        q.info = query.info
        q.prompt = prompt
        q.error = "(skip)"
        return q
    table = []
    for i, row in enumerate(common.read_table(query.result)):
        if i == 1:
            table.append("|" + "---|" * (flen + len(translate)))
            continue
        rowf = [" ".join(row[f].strip() for f in fs) for fs in fields]
        if i == 0:
            cells = " | ".join([language, *rowf[1:]])
            table.append("| " + cells + " | " + " | ".join(translate) + " |")
        else:
            cells = " | ".join(rowf)
            if cells.upper() != cells.lower():
                table.append("| " + cells + " |" * (len(translate) + 1))
    prompt += "\n\n"
    prompt += "\n".join(table)
    return gemini.query(prompt, query.info, show, retry)

if os.path.exists(init_xml):
    init_qs = common.read_queries(init_xml)
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
