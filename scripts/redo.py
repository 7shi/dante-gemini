import sys, os

args = sys.argv[1:]

init_xml = "init.xml"

while args:
    if args[0] == "-i" and len(args) > 1:
        init_xml = args[1]
        args = args[2:]
    else:
        break

if len(args) != 1:
    print(f"usage: python {sys.argv[0]} [-i init] input", file=sys.stderr)
    sys.exit(1)

import common

init_qs = common.read_queries(init_xml)
history = common.unzip(init_qs)
input_qs = common.read_queries(args[0])

import gemini

def query(q):
    if not (0 <= gemini.chat_count < 5):
        gemini.init(history, [init_qs[-1].prompt])
    return gemini.query(q.prompt, q.info, show=True, retry=False)

qs1 = []
qs2 = []
for q in input_qs:
    q = query(q)
    (qs1 if q.result else qs2).append(q)

print("OK:", len(qs1), ", NG:", len(qs2), ", ALL:", len(input_qs), file=sys.stderr)
fn = os.path.splitext(args[0])[0]
if qs1:
    common.write_queries(f"{fn}-ok.xml", qs1, count=len(qs1))
if qs2:
    common.write_queries(f"{fn}-ng.xml", qs2, count=len(qs2))
