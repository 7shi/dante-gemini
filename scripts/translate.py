import sys, os, re

args = sys.argv[1:]
if len(args) != 3:
    print(f"Usage: python {sys.argv[0]} italian-dir output-dir language", file=sys.stderr)
    sys.exit(1)

itdir, outdir, language = args
if not os.path.exists(outdir):
    os.mkdir(outdir)

import gemini

it = []
current = 0
directory = ""
canto = 0

def send_lines(line_count, *plines):
    info = f"[{directory} Canto {canto}] {current + 1}/{len(it)}"
    prompt = " ".join(plines)
    for i in range(line_count):
        ln = current + i
        if i == 0 or ln % 3 == 0:
            prompt += "\n"
        line = f"{ln + 1} {it[ln]}"
        prompt += "\n" + line
    return gemini.Query(prompt, info, show=True, retry=True)

def write(f, text):
    f.write(text.encode("utf_8"))

for directory in ["Inferno", "Purgatorio", "Paradiso"]:
    path = os.path.join(outdir, directory.lower())
    if not os.path.exists(path):
        os.mkdir(path)
    itfiles = [
        (int(m.group(1)), os.path.join(itdir, directory, f))
        for f in sorted(os.listdir(os.path.join(itdir, directory)))
        if (m := re.match(r"(\d+)\.txt", f))
    ]
    for canto, itf in itfiles:
        xml = os.path.join(path, f"{canto:02}.xml")
        if os.path.exists(xml):
            continue
        print()
        print(f"# {directory} Canto {canto}")
        with open(itf, "r", encoding="utf-8") as f:
            it = [l for line in f if (l := line.strip())]
        current = 0
        queries = []
        gemini.init()
        while current < len(it):
            length = min(3, len(it) - current)
            while current + length < len(it) and not it[current + length - 1].endswith("."):
                length += 1
            q = send_lines(length, f"Please translate literally into {language}.")
            queries.append(q)
            current += length
        with open(xml, "wb") as f:
            write(f, '<?xml version="1.0" encoding="utf-8"?>\n')
            for q in queries:
                write(f, str(q))
        # sys.exit(0)
