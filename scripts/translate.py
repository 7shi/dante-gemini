import sys, os, re, common, option

needsp = False

def parse(i, args):
    global needsp
    if args[i] == "--need-space":
        args.pop(i)
        needsp = True

if not option.parse(parse) or option.args:
    print(f"Usage: python {sys.argv[0]} language italian-dir output-dir", file=sys.stderr)
    print("  --need-space: require at least one space in each line", file=sys.stderr)
    option.show()
    sys.exit(1)

checklen = 6 if " and " in option.language else 3

import gemini

it = []
current = 0

def send_lines(line_count, *plines):
    global current
    diru = option.directory[0].upper() + option.directory[1:]
    info = f"[{diru} Canto {option.canto}] {current + 1}/{len(it)}"
    prompt = " ".join(plines)
    for i in range(line_count):
        if i == 0 or current % 3 == 0:
            prompt += "\n"
        line = f"{current + 1} {it[current]}"
        prompt += "\n" + line
        current += 1
    def check(r):
        if len(r) > len(prompt) * checklen:
            return f"Response too long: ({len(r)} > {len(prompt) * checklen})"
        if needsp:
            for line in r.split("\n"):
                if m := re.match(r"(\d+)", line):
                    text = line[m.end():]
                    if not text.startswith(" ") or " " not in text[1:]:
                        return f"Too few spaces: {repr(r)}"
        return None
    return gemini.query(prompt, info, option.show, option.retry, check)

prompt = f"Please translate each line literally into {option.language}."
if os.path.exists(option.init):
    init_qs = common.read_queries(option.init)
else:
    print(f"making {option.init}...")
    gemini.init()
    option.directory = "inferno"
    option.canto = 1
    file = os.path.join(option.srcdir, option.directory, f"01.txt")
    with open(file, "r", encoding="utf-8") as f:
        it = [l for line in f if (l := line.strip())]
    init_qs = []
    for length in [3, 6]:
        q = send_lines(length, prompt)
        if not q.result:
            print("Abort.", file=sys.stderr)
            sys.exit(1)
        init_qs.append(q)
    common.write_queries(option.init, init_qs, count=len(init_qs))
history = common.unzip(init_qs)
init_ps = history[:1] if option.interval == 1 else None

@option.proc
def proc(src, xml):
    global it, current
    with open(src, "r", encoding="utf-8") as f:
        it = [l for line in f if (l := line.strip())]
    current = 0
    qs = []
    while current < len(it):
        if not (0 <= gemini.chat_count < option.interval):
            gemini.init(history, init_ps)
        length = min(3, len(it) - current)
        while current + length < len(it) and not it[current + length - 1].endswith("."):
            length += 1
        qs.append(send_lines(length, prompt))
    common.write_queries(xml, qs, count=len(qs))
