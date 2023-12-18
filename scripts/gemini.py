"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import sys, os, re, time

print("Reading modules...")
import google.generativeai as genai

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Please set GOOGLE_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]

def escape(s):
    return s.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

def parse(s, i):
    start = s[i]
    i += 1
    ret = ""
    while i < len(s) and s[i] != start:
        ch = s[i]
        i += 1
        if ch == "\\" and i < len(s):
            ch = s[i]
            i += 1
            if ch == "n":
                ret += "\n"
            elif ch == "t":
                ret += "\t"
            elif ch == "r":
                ret += "\r"
            else:
                ret += ch
        else:
            ret += ch
    return ret, i

class Watcher:
    def __init__(self):
        self.history = [time.time()]

    def countup(self):
        if len(self.history) == 60:
            diff = self.history.pop(0) + 61 - time.time()
            if diff > 0:
                time.sleep(diff)
        self.history.append(time.time())

watcher = Watcher()
history = None
model = None
convo = None
chatCount = 0

def init(*hist):
    global history
    history = []
    role = ["user", "model"]
    for i, h in enumerate(hist):
        history.append({ "role": role[i % 2], "parts": h.strip() })
    start()

def start():
    global model, convo, chatCount
    print("Starting model...", file=sys.stderr)
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    if history:
        convo = model.start_chat(history=history)
    else:
        convo = model.start_chat()
    chatCount = 0
    watcher.countup()

class Query:
    def __init__(self, prompt, info=None, show=False, retry=True):
        global chatCount
        self.prompt = prompt.replace("\r\n", "\n").rstrip()
        self.info = info.strip() if info else None
        self.result = None
        self.error = None
        self.retry = False
        if show:
            print()
            if info:
                print(info)
            for line in prompt.split("\n"):
                print(">", line)
        for _ in range(2):
            try:
                chatCount += 1
                watcher.countup()
                convo.send_message(self.prompt)
                r = convo.last.text.rstrip()
                # if len(r) > len(prompt) * 3:
                #     raise(Exception(f"Response too long: {len(r)}"))
                self.result = r
                if show:
                    print()
                    print(r)
                return
            except Exception as e:
                err = str(e).rstrip()
                self.error = err
                if show:
                    print()
                    print(err)
                if m := re.search("text: ", err):
                    r, _ = parse(err, m.end())
                    r = r.rstrip()
                    self.result = r
                    if show:
                        print()
                        print(r)
                    return
                elif not retry or chatCount == 1:
                    return
                else:
                    self.retry = True
                    if show:
                        print()
                    print("Retrying...", file=sys.stderr)
                    start()

    def __str__(self):
        s = "<query>\n"
        if self.info:
            s += f"<info>{escape(self.info)}</info>\n"
        attrs = ' retry="true"' if self.retry else ''
        s += f"<prompt{attrs}>\n{escape(self.prompt)}\n</prompt>\n"
        if self.error:
            attrs = ' result="true"' if self.result else ''
            s += f"<error{attrs}>\n{escape(self.error)}\n</error>\n"
        if self.result:
            s += f"<result>\n{escape(self.result)}\n</result>\n"
        return s + "</query>\n"
