import sys, re

args = sys.argv[1:]

if not args:
    print(f"usage: python {sys.argv[0]} xml1 [xml2 ...]", file=sys.stderr)
    sys.exit(1)

import common

def split_lines(text):
    if not text:
        return [], [], []
    lines = [line.strip() for line in text.strip().split("\n")]
    s1 = 0
    for i in range(len(lines)):
        if re.match(r"\*\*.+\*\*$", lines[i]):
            s1 = i
    s2 = -1
    for i in range(s1, len(lines)):
        if re.match("\d+ ", lines[i]):
            s2 = i
            break
    if s2 < 0:
        return "", [], []
    lnums = []
    lnum  = []
    texts = []
    text  = []
    for i in range(s2, len(lines)):
        if m := re.match("(\d+) ", lines[i]):
            lnum.append(int(m.group(1)))
            text.append(lines[i])
        elif lnum:
            lnums.append(lnum)
            texts.append("\n".join(text))
            lnum = []
            text = []
    if lnum:
        lnums.append(lnum)
        texts.append("\n".join(text))
    return "\n".join(lines[:s2]), lnums, texts

def equals(a, b):
    if len(a) != len(b):
        return False
    return all(a[i] == b[i] for i in range(len(a)))

for arg in args:
    src = common.read_queries(arg)
    dst = []
    for q in src:
        if not (m := re.match(r"(.+) (\d+)/(\d+)$", q.info)):
            print(f"invalid format @ {q.info}", file=sys.stderr)
            dst.append(q)
            continue
        info1 = m.group(1)
        info2 = int(m.group(2))
        info3 = int(m.group(3))
        ppre, pln, ptx = split_lines(q.prompt)
        if not pln:
            print(f"no lines found @ {q.info}", file=sys.stderr)
            if q.result:
                q.error = q.result
                q.result = None
            dst.append(q)
            continue
        if info2 != pln[0][0]:
            print(f"line not match: {pln[0][0]} @ {q.info}", file=sys.stderr)
            if q.result:
                q.error = q.result
                q.result = None
            dst.append(q)
            continue
        rpre, rln, rtx = split_lines(q.result)
        if not q.result or not rln:
            for i in range(len(pln)):
                q1 = common.query()
                q1.info = f"{info1} {pln[i][0]}/{info3}"
                q1.prompt = f"{ppre}\n{ptx[i]}"
                if i == 0 and q.result:
                    q1.error = q.result
                elif i == 0 and q.error:
                    q1.error = q.error
                else:
                    q1.error = "(no result)"
                dst.append(q1)
            continue
        for i in range(len(pln)):
            q1 = common.query()
            q1.info = f"{info1} {pln[i][0]}/{info3}"
            q1.prompt = f"{ppre}\n{ptx[i]}"
            if i >= len(rln):
                if i == 0:
                    q1.error = q.result
                else:
                    q1.error = "(no result)"
            elif not equals(pln[i], rln[i]):
                if i == 0 and rpre:
                    q1.error = f"{rpre}\n{rtx[i]}"
                else:
                    q1.error = rtx[i]
            else:
                if i == 0 and rpre:
                    q1.error = rpre.strip()
                q1.result = rtx[i]
            dst.append(q1)
    common.write_queries(arg, dst, count=len(dst))
