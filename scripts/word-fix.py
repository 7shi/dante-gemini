# obsolete: use redo.py instead

import sys, os, re, common

args = sys.argv[1:]

init_xml = "init.xml"
if len(args) > 1 and args[0] == "-i":
    init_xml = args[1]
    args = args[2:]

if args:
    print(f"usage: python {sys.argv[0]} [-i init]", file=sys.stderr)
    sys.exit(1)

error_qs = common.read_queries("1-error.xml")
errors = {q.info: q for q in error_qs}

# for q in error_qs:
#     print(q.info, q.error.split("\n")[0])

fix = {}
for f in os.listdir("."):
    if re.match(r".*fix.*\.xml", f):
        for q in common.read_queries(f):
            if q.result:
                fix[q.info] = q

# sys.exit(0)

init_qs = common.read_queries(init_xml)
history = common.unzip(init_qs)
if init_qs[0].prompt[:8] in ["This tex", "Create a"]:
    init_ps = [init_qs[0].prompt]
else:
    init_ps = [init_qs[1].prompt]
# init_prompt = "Create a word table.\n" + "\n".join(history[2].split("\n")[-4:])

import gemini

def init():
    gemini.init(history, init_ps)

qs = []

# init()
# for i in ["[Inferno Canto 13] 127/151"]:
#     q = errors[i]
#     q = gemini.query(q.prompt, q.info, show=True, retry=False)
#     if q.result:
#         qs.append(q)

one_line = True

fixed = 0

def query(prompt, info):
    global fixed
    if not (0 <= gemini.chat_count < 10):
        init()
    q = gemini.query(prompt, info, show=True, retry=False)
    qs.append(q)
    if q.result:
        fixed += 1

for q in error_qs:
    if q.info in fix:
        continue
    if one_line:
        lines = q.prompt.split("\n")
        for i, line in enumerate(lines[2:]):
            info = f"{q.info}+{i}"
            if info in fix:
                continue
            query(f"{lines[0]}\n{line}", info)
    else:
        query(q.prompt, q.info)

print("Fixed:", fixed, "/", len(qs))

if qs:
    prefix = "fix" if fixed else "error"
    num = 0
    for f in os.listdir("."):
        if m := re.match(prefix + r"-(\d+)\.xml", f):
            num = max(num, int(m.group(1)))
    fn = f"{prefix}-{num+1:03}.xml"
    common.write_queries(fn, qs, fixed=fixed, count=len(qs))
    print("Written:", fn)
