# CC0 http://creativecommons.org/publicdomain/zero/1.0/

import io, html

declaration = '<?xml version="1.0" encoding="UTF-8"?>'

class reader:
    def __init__(self, src):
        self.pos = 0
        self.reserved = ""
        self.text = ""
        self.tag = ""
        self.values = {}
        self.src = src

    def __contains__(self, key):
        return key in self.values

    def __getitem__(self, key):
        return self.values[key]

    def get(self, key, default=None):
        return self.values.get(key, default)

    def check(self, tag, **kwargs):
        if tag != self.tag: return False
        for key, value in kwargs.items():
            key = key.removesuffix("_")
            if key not in self or self[key] != value:
                return False
        return True

    def find(self, tag, **kwargs):
        while self.read():
            if self.check(tag, **kwargs):
                return True
        return False

    def each(self, tag = "", **kwargs):
        end = "/" + self.tag
        i = 0
        while self.tag != end and self.read():
            if tag == "" or self.check(tag, **kwargs):
                yield i
                i += 1

    def read(self):
        self.text = ""
        self.tag  = ""
        self.values = {}
        if self.reserved != "":
            self.tag = self.reserved
            self.reserved = ""
        elif self.pos >= len(self.src):
            return False
        else:
            self.read_text()
        return True

    def read_text(self):
        p = self.src.find("<", self.pos)
        if p < 0:
            self.text = html.unescape(self.src[self.pos:])
            self.pos = len(self.src)
        else:
            self.text = html.unescape(self.src[self.pos:p])
            self.pos = p + 1
            self.read_tag()

    def read_char(self):
        if self.pos >= len(self.src):
            self.cur = ""
        else:
            self.cur = self.src[self.pos]
            self.pos += 1
        return self.cur

    def read_tag(self):
        with io.StringIO() as t:
            while self.read_char() != "":
                ch = self.cur
                if ch == ">" or (ch == "/" and t.tell() > 0):
                    break
                elif ch > " ":
                    t.write(ch)
                    if t.tell() == 3 and t.getvalue() == "!--":
                        break
                elif t.tell() > 0:
                    break
            self.tag = t.getvalue().lower()
        if ch == "/":
            self.reserved = "/" + self.tag
            ch = self.read_char()
            while (ch := self.read_char()) != "" and ch != ">":
                pass
        if ch != ">":
            if self.tag == "!--":
                self.read_comment()
            else:
                while self.read_values(): pass
                if self.cur == "/":
                    self.reserved = "/" + self.tag
                    while (ch := self.read_char()) != "" and ch <= " ":
                        pass

    def read_comment(self):
        p = self.src.find("-->", self.pos)
        if p < 0:
            self.values["comment"] = self.src[self.pos:]
            self.pos = len(self.src)
        else:
            self.values["comment"] = self.src[self.pos:p]
            self.pos = p + 3

    def read_values(self):
        nm = self.read_value(True).lower()
        if nm == "": return False
        if self.cur == "=":
            self.values[nm] = self.read_value(False)
        else:
            self.values[nm] = ""
        return self.cur != "/" and self.cur != ">"

    def read_value(self, isleft):
        with io.StringIO() as v:
            while self.read_char() != "":
                ch = self.cur
                if ch == ">" or ch == "/" or (isleft and ch == "="):
                    break
                elif ch == '"':
                    while self.read_char() != "":
                        if self.cur == '"': break
                        v.write(self.cur)
                    break
                elif ch > " ":
                    v.write(ch)
                elif v.tell() > 0:
                    break
            return v.getvalue()
