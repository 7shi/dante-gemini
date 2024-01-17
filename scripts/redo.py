import sys, os

args = sys.argv[1:]

init_xml = "init.xml"
per1 = False

while args:
    if args[0] == "-i" and len(args) > 1:
        init_xml = args[1]
        args = args[2:]
    elif args[0] == "-1":
        per1 = True
        args = args[1:]
    else:
        break

if len(args) != 1:
    print(f"usage: python {sys.argv[0]} [-i init] [-1] input", file=sys.stderr)
    sys.exit(1)

import re, common

init_qs = common.read_queries(init_xml)
history = common.unzip(init_qs)
input_qs = common.read_queries(args[0])

queries = []
it = iter(input_qs)
q = next(it, None)
while q:
    if re.search(r"\+\d$", q.info):
        qs = [q]
        prefix = q.info[:-2]
        while q := next(it, None):
            if q.info.startswith(prefix):
                qs.append(q)
            else:
                break
        queries.append(qs)
        continue
    if per1:
        lines = q.prompt.strip().split("\n")
        if len(lines) == 5 and not lines[1]:
            qs = []
            for i in range(3):
                qq = common.query()
                qq.info = f"{q.info}+{i}"
                qq.prompt = "\n".join([lines[0], "", lines[i + 2]])
                qs.append(qq)
            queries.append(qs)
            q = next(it, None)
            continue
    queries.append([q])
    q = next(it, None)

def separate(result):
    lines = [line.strip() for line in result.strip().split("\n")]
    ret = []
    for line in lines:
        if re.match(r"\*\*.+\*\*$", line):
            ret.append([line, ""])
        elif ret and line:
            if ret[-1][1]:
                ret[-1][1] += "\n"
            ret[-1][1] += line
    return ret

import gemini

def query(prompt, info):
    if not (0 <= gemini.chat_count < 5):
        gemini.init(history, [init_qs[-1].prompt])
    return gemini.query(prompt, info, show=True, retry=False)

qs_ok = []
qs_ng = []
i = 0
count = sum(1 for qs1 in queries for q in qs1 if not q.result)
for qs1 in queries:
    qs2 = []
    ok = 0
    for q in qs1:
        if q.result:
            qq = q
        else:
            i += 1
            print(f"{i}/{count}", file=sys.stderr)
            qq = query(q.prompt, q.info)
        qs2.append(qq)
        if qq.result:
            ok += 1
    if ok == 3:
        q = common.query()
        q.info = qs2[0].info[:-2]
        q.prompt = "\n".join(qs2[0].prompt.split("\n")[:2])
        q.result = ""
        r = None
        for qq in qs2:
            q.prompt += "\n" + qq.prompt.split("\n")[2]
            if (sp := separate(qq.result)):
                if not r:
                    r = sp
                else:
                    for j in range(len(r)):
                        r[j] = (r[j][0], r[j][1] + "\n" + sp[j][1])
            else:
                line = qq.result.split("\n")[0]
                if r:
                    r[-1][1] += "\n" + line
                else:
                    if q.result:
                        q.result += "\n"
                    q.result += line
        if r:
            q.error = ""
            for j in range(len(r)):
                if q.error:
                    q.error += "\n\n"
                if j < len(r) - 1:
                    q.error += f"{r[j][0]}\n\n{r[j][1]}"
                else:
                    if q.result:
                        q.result += "\n"
                    q.error  += r[j][0]
                    q.result += r[j][1]
        qs_ok.append(q)
    elif ok == len(qs2):
        qs_ok += qs2
    else:
        qs_ng += qs2

all = sum(map(len, queries))
print("OK:", len(qs_ok), ", NG:", len(qs_ng), ", ALL:", all, file=sys.stderr)

fn = os.path.splitext(args[0])[0]
if qs_ok:
    common.write_queries(f"{fn}-ok.xml", qs_ok, count=len(qs_ok))
if qs_ng:
    error = sum(1 for q in qs_ng if not q.result)
    common.write_queries(f"{fn}-ng.xml", qs_ng, error=error, count=len(qs_ng))
