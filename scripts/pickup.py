import sys, common, xml7shi

args = sys.argv[1:]
if not args:
    print(f"Usage: python {sys.argv[0]} file1 [file2 ...]", file=sys.stderr)
    sys.exit(1)

all = 0
errors = []
for f in args:
    with open(f, "r", encoding="utf-8") as f:
        xml = f.read()
    xr = xml7shi.reader(xml)
    while (q := common.parse(xr)).prompt:
        all += 1
        if q.error and not q.result:
            errors.append(q)

d = args[0].split("/")[0]
print(f"{d}: error {len(errors)}/{all}", file=sys.stderr)

print(xml7shi.declaration)
print(f'<errors count="{len(errors)}" all="{all}">')
for q in errors:
    print(q, end="")
print("</errors>")
