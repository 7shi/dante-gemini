import sys, common

args = sys.argv[1:]

if not args:
    print(f"Usage: python {sys.argv[0]} target1 [target2 ...]", file=sys.stderr)
    sys.exit(1)

for arg in args:
    qs = common.read_queries(arg)
    for q in qs:
        if q.result:
            if "||---" in q.result:
                q.result = None
                q.error = "(broken table)"
            else:
                table = []
                flag = False
                for line in q.result.split("\n"):
                    prev = flag
                    flag = line.startswith("|")
                    if prev and not flag:
                        break
                    elif flag:
                        table.append(line)
                if len(table) >= 2:
                    q.result = "\n".join(table)
        common.write_queries(arg, qs, count=len(qs))
