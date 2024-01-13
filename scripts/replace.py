import sys, common

args = sys.argv[1:]
if len(args) < 2:
    print(f"usage: python {sys.argv[0]} fix target1 [target2 ...]", file=sys.stderr)
    sys.exit(1)

fixes = common.read_fixes(args.pop(0))
for arg in args:
    fix = 0
    qs = []
    for q in common.read_queries(arg):
        if q.info in fixes:
            fix += 1
            qs += fixes[q.info]
        else:
            qs.append(q)
    if fix:
        print("fixed:", arg, fix, "/", len(qs), file=sys.stderr)
        common.write_queries(arg, qs, count=len(qs))
