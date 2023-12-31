import sys, os, re, common

args = sys.argv[1:]

directories = "inferno purgatorio paradiso"
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

if len(args) < 3:
    print(f"Usage: python {sys.argv[0]} language word-dir output-dir [fix ...]", file=sys.stderr)
    print("  -d: specify sub directory", file=sys.stderr)
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
    prompt = "For each row in the table, fill the third column with a literal translation of the first column."
    if not query.result:
        q = common.query()
        q.info = query.info
        q.prompt = prompt
        q.error = "(skip)"
        return q
    table = []
    for i, row in enumerate(common.read_table(query.result)):
        if i == 0:
            table.append(f"| {language} | Lemma | English |")
        elif i == 1:
            table.append("|" + "|".join(row[:3]) + "|")
        else:
            lemma = row[1]
            if lemma:
                table.append(f"| {row[0]} | {lemma} | |")
    prompt += "\n\n"
    prompt += "\n".join(table)
    return gemini.query(prompt, query.info, show, retry)

for directory in directories.split():
    path = os.path.join(outdir, directory)
    if not os.path.exists(path):
        os.mkdir(path)
    files = [
        (int(m.group(1)), os.path.join(worddir, directory, f))
        for f in sorted(os.listdir(os.path.join(worddir, directory)))
        if (m := re.match(r"(\d+)\.xml", f))
    ]
    for canto, file in files:
        xml = os.path.join(path, f"{canto:02}.xml")
        if os.path.exists(xml):
            continue
        print()
        print(f"# {directory} Canto {canto}")
        queries = common.read_queries(file)
        qs = []
        for query in queries:
            if len(qs) % 10 == 0:
                gemini.init()
            if not query.result and query.info in fixes:
                for q in fixes[query.info]:
                    qs.append(send(q))
            else:
                qs.append(send(query))
        common.write_queries(xml, qs, count=len(qs))
        if once:
            sys.exit(0)
