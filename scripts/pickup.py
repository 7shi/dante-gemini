import sys, common

args = sys.argv[1:]
if len(args) < 2:
    print(f"Usage: python {sys.argv[0]} output file1 [file2 ...]", file=sys.stderr)
    sys.exit(1)

output = args.pop(0)

whole = 0
queries = []
for f in args:
    for q in common.read_queries(f):
        whole += 1
        if q.error and not q.result:
            queries.append(q)

d = args[0].split("/")[0]
print(f"{d}: error {len(queries)}/{whole}", file=sys.stderr)
common.write_queries(output, queries, count=len(queries), whole=whole)
