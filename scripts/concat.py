import sys, common

args = sys.argv[1:]
if len(args) < 2:
    print(f"usage: python {sys.argv[0]} output input1 [input2 ...]", file=sys.stderr)
    sys.exit(1)

qs = []
for arg in args[1:]:
    qs += common.read_queries(arg)
common.write_queries(args[0], qs, count=len(qs))
